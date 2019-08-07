from typing import Union

from enum import Enum
from io import StringIO
import re
import warnings

from .rule import LineComponents, Final
from .rules import get_rules
from .filter_multiline_comments import filter_multiline_comments
from .__util import *


class ResultBehaviour(Enum):
    try_ = 'try'
    var = 'variable'


def convert(pascal: str, check_syntax=True, result_behaviour: Union[str, ResultBehaviour] = 'try', disclose=True,
            remove_inline_comments=True, pre_parts=('from talos import *',), post_parts=()):
    """
    convert a pascal script to a python script
    :param pascal: the pascal script as a single string
    :param check_syntax: whether to check the python syntax of the output and issue a warning if any errors are found
    :param result_behaviour: how to handle the result variable
    :param disclose: whether to add a disclosure tot he output stating it was automatically generated
    :param remove_inline_comments: whether to remove inline comments in the source code. Setting this to false will
        raise an error if inline comments are found.
    :param pre_parts: any text to add before the output code should be entered here
    :param post_parts: any text to add after the output code should be entered here
    :return: the python script as a string
    """
    result_behaviour = ResultBehaviour(result_behaviour)
    result_as_var = result_behaviour == ResultBehaviour.var
    pre_words, post_words, rules = get_rules(result_as_var, disclose=disclose,
                                             pre_raw_parts=pre_parts, post_raw_parts=post_parts)
    env = {}

    lines = list(
        filter_multiline_comments(pascal.splitlines(keepends=False), remove_inline_comments=remove_inline_comments))
    # just treat single-line scripts as though they have a begin and end around them
    if len(lines) in (0, 1):
        lines = ['begin', *('\t' + l for l in lines), 'end']
    else:
        try:
            var_index = lines.index('var')
        except ValueError:
            # if there is no var, then delete nothing (we want to keep anything before begin in case it's a comment)
            pass
        else:
            begin_index = lines.index('begin', var_index)
            del lines[var_index:begin_index]

    ret = StringIO()

    for line in lines:
        # note: we want to pass blank lines only if it was blank in the original!
        if isblank(line):
            ret.write('\n')
            continue

        indent = re.match('^\s*', line).group(0)
        comps = LineComponents(line)
        non_final = comps.non_final_part()
        while non_final:
            comp_ind, comp = non_final
            if not comp:
                comps[comp_ind] = Final(comp)
            else:
                env['last_component'] = comp_ind + 1 == len(comps)
                for rule in rules:
                    try:
                        res = rule(comp, env)
                    except EarlyReturnDetected:
                        return convert(pascal, check_syntax, 'variable', disclose, remove_inline_comments, pre_parts,
                                       post_parts)
                    if res is not None:
                        comp = comps[comp_ind] = res
                        if not isinstance(res, str):
                            break
                        if not comp:
                            comps[comp_ind] = Final(comp)
                            break

            non_final = comps.non_final_part()

        line = ''.join(comps)
        env['prev_indent'] = indent
        if not isblank(line):
            ret.write(line + '\n')

    ret = pre_words.join() + ret.getvalue() + post_words.join()
    ret = ret.rstrip() + '\n'  # add a single trailing newline as per PEP8
    if check_syntax:
        valid, error = is_valid_python(ret)
        if not valid:
            warnings.warn(
                f'the python script did not pass syntax checking, the error was: {error}',
                category=FatalTransmogripyWarning)
    return ret
