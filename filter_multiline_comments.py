from typing import Iterable, Union, List, Tuple, Match

from enum import Enum
from collections import namedtuple
import re

from transmogripy.__util import *


class ScanMode(Enum):
    code = 'code', None, None
    raw = 'raw', "'", "'"
    bracket_comment = 'com', '{', '}'
    star_comment = 'com', '(*', '*)'
    line_comment = 'com', '//', ''


class Comment(str):
    __slots__ = ('args',)

    @classmethod
    def full(cls, arg, open_, close):
        return open_ + arg.strip() + close

    def __new__(cls, arg: str, open_, close):
        full = cls.full(arg, open_, close)
        ret = super().__new__(cls, full)
        ret.args = arg, open_, close
        return ret

    def __repr__(self):
        return type(self).__name__ + '(' + ', '.join(self.args) + ')'


class LineParts(List[str]):
    __slots__ = ('remove_inline_comments',)

    def __new__(cls, *args, remove_inline_comments=False, **kwargs):
        return super().__new__(cls, *args, **kwargs)

    def __init__(self, *args, remove_inline_comments=False, **kwargs):
        super().__init__(*args, **kwargs)
        self.remove_inline_comments = remove_inline_comments

    @property
    def last_is_comment(self):
        for i in reversed(self):
            if isinstance(i, Comment):
                return True
            if isblank(i):
                continue
            return False
        return False

    def append(self, o, mode=None):
        if mode and mode.value[0] == 'com':
            o = Comment(o, *mode.value[1:])
        if not isinstance(o, Comment) and not o.isspace():
            while self.last_is_comment:
                if self.remove_inline_comments:
                    self.pop()
                    continue
                raise NotImplementedError('inline comments must be at the end of a line')
        super().append(o)

    def join(self):
        return ''.join(str(i) for i in self)


Region = namedtuple('Region', 'start_pattern end_pattern mode')
regions = [
    Region(re.compile("'"), re.compile(r"(?<!\\)'"), ScanMode.raw),
    Region(re.compile('{(?!\$)'), re.compile('}'), ScanMode.bracket_comment),
    Region(re.compile('\(\*'), re.compile('\*\)'), ScanMode.star_comment),
    Region(re.compile('//'), re.compile('$'), ScanMode.line_comment),
]


def next_region_ind(line):
    """
    returns the index of the first matching region. If not found, returns the line's length
    >>> next_region_ind("abc{d'ef")
    3
    >>> next_region_ind("re'ge{x")
    2
    >>> next_region_ind("regex")
    5
    """
    matches = [reg.start_pattern.search(line) for reg in regions]
    match = min(matches,
                key=lambda m: float('inf') if m is None else m.start())
    if match is None:
        return len(line)

    return match.start()


def match_region(line) -> Tuple[Region, Match]:
    """
    returns the region that matches the first characters in the line, raises an error if there is more or less than one
    matching region. Also returns the match
    """
    matches = [(reg, reg.start_pattern.match(line)) for reg in regions]
    matches = [(k, v) for (k, v) in matches if v]
    if len(matches) != 1:
        raise AssertionError(f'expected 1 match, got {len(matches)}')
    return matches[0]


def filter_multiline_comments(source: Iterable[str], remove_inline_comments=False):
    """
    all this function does is wrap all lines in between multiline comments with a seperate multiline comment
        {a
        b
        c}
    to:
        {a}
        {b}
        {c}
    >>> assert list(filter_multiline_comments(["abcd","efgh"])) == ["abcd","efgh"]
    >>> assert list(filter_multiline_comments(["abc{def","def","def}"])) == ["abc{def}","{def}","{def}"]
    >>> assert list(filter_multiline_comments(["abc{def","   def","def}"])) == ["abc{def}","   {def}","{def}"]
    >>> assert list(filter_multiline_comments(["my mother said 'i need {some} dire frui{{t'" \
                                                ,"{she didn't actually","say","that}" \
                                                ,"but you {don't care} {do you?}"])) \
                                                 == ["my mother said 'i need {some} dire frui{{t'" \
                                                 ,"{she didn't actually}","{say}","{that}" \
                                                 ,"but you {don't care} {do you?}"]
    >>> assert list(filter_multiline_comments(['hi //there','how are you?','{i','am}','//fi{ne','thanks', \
                                                '{no //problem}'])) \
                                                == ['hi //there', 'how are you?', '{i}', '{am}', '//fi{ne', 'thanks',\
                                                 '{no //problem}']
    """

    region: Union[Region, type(...), None] = None
    # the region we are in, None means we are in code
    # ... means the next token is the start of a region, and we need to find out which
    for line in source:
        line_parts = LineParts(remove_inline_comments=remove_inline_comments)
        if region is not None:
            indent = re.match('\s*', line)
            line_parts.append(indent.group())
            line = line[indent.end():]
        capture = ''
        while line:
            if region is None:
                code_scan_length = next_region_ind(line)
                if code_scan_length == 0:
                    region = ...
                else:
                    line_parts.append(line[:code_scan_length])
                    line = line[code_scan_length:]
            elif region is ...:
                region, match = match_region(line)
                if region.mode.value[0] == 'com':
                    capture = ''
                elif region.mode == ScanMode.raw:
                    capture = match[0]
                else:
                    raise AssertionError('unhandled region mode: ' + str(region.mode))
                line = line[match.end():]
            else:
                # regular region (string or comment)
                end_token_match = region.end_pattern.search(line)
                mode = region.mode
                if not end_token_match:
                    # the rest of the line is the current region (it continues unto the next line but we split it here)
                    # technically, this is only allowed if we're in a comment, but I'm not about to start throwing
                    # pascal errors
                    capture += line
                    line = ''
                else:
                    if region.mode.value[0] == 'com':
                        end_cap_ind = end_token_match.start()
                    elif region.mode == ScanMode.raw:
                        end_cap_ind = end_token_match.end()
                    else:
                        raise AssertionError('unhandled region mode: ' + str(region.mode))
                    capture += line[:end_cap_ind]
                    line = line[end_token_match.end():]
                    region = None
                # either way, this region is done
                line_parts.append(capture, mode)
                capture = ''
        yield line_parts.join()
