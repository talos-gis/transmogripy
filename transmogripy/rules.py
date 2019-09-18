from typing import Iterable

from typing import NamedTuple

from .rule import Rule, ReReplaceRule, NotSupportedRule, ReReplaceFinalRule, HaltRule, EarlyReturnRule
from .segment import PreWord, PostWord, Segment


class RuleSet(NamedTuple):
    pre_words: Segment
    post_words: Segment
    rules: Iterable[Rule]


def get_rules(result_as_var: bool, allow_numpy=True, disclose=True, pre_raw_parts=(), post_raw_parts=()) -> RuleSet:
    pre_words = PreWord()
    post_words = PostWord()

    if disclose:
        pre_words.add_part('disclose')
    for prp in pre_raw_parts:
        pre_words.add_raw(prp)
    for prp in post_raw_parts:
        post_words.add_raw(prp)

    # remember: all these patterns are compiled with the IGNORECASE flag
    rules = (
        # comment rules
        # all these comment rules have 2 modes: one for whole-line comment, and one for end-of-line comment
        # (where it adds 2 spaces)
        ReReplaceFinalRule(r'^(?P<indent>\s*)\{\s*(?P<com>([^$].*)?)\s*\}\s*', '\g<indent># \g<com>'),

        ReReplaceFinalRule('\s*\{\s*(?P<com>([^$].*)?)\s*\}\s*', '  # \g<com>'),

        ReReplaceFinalRule(r'^(?P<indent>\s*)\(\*\s*(?P<com>([^$].*)?)\s*\*\)\s*', '\g<indent># \g<com>'),

        ReReplaceFinalRule('\s*\(\*\s*(?P<com>([^$].*)?)\s*\*\)\s*', '  # \g<com>'),

        ReReplaceFinalRule(r'^(?P<indent>\s*)//\s*(?P<com>.*)', '\g<indent># \g<com>'),

        ReReplaceFinalRule(r'\s*//\s*(?P<com>.*)', '  # \g<com>'),

        # raw string

        ReReplaceFinalRule("'(?P<inner>[^']*)'", "'\g<inner>'"),

        # for loop

        ReReplaceRule('for\s+(?P<var_name>[^ ]+)\s*:=\s*(?P<start>.*)\s+to\s+(?P<end>.*)\s+do',
                      'for \g<var_name> in range(\g<start>, \g<end>+1):'),

        # remove semicolons

        ReReplaceRule(';', ''),

        # begin marks function start

        ReReplaceRule('^begin$', 'def main():'),

        # result rules

        ReReplaceRule.maybe(result_as_var)('(?<![_a-z0-9])Result(?![_0-9a-z])', '__Return__'),

        EarlyReturnRule.maybe(not result_as_var)('(?<=[a-z0-9_])[^a-z0-9_]+Result(?![_0-9a-z])'),
        ReReplaceRule.maybe(not result_as_var)('^(?P<indent>\s*)Result\s*:=\s*', '\g<indent>return '),

        # \\ connector at end of line for line continuation

        ReReplaceRule('(?<![_a-z0-9])(?P<connector>and|or|\+|-|%|^|\||&|\*|/|//)\s*$', r'\g<connector> \\',
                      demand_last_component=True),

        # if result is var, return it at the end

        ReReplaceRule.maybe(result_as_var)('^end\s*\.?\s*$', 'return __Return__', add_prev_indent=True),

        # delete all begins and ends (we trust the source is properly indented)

        ReReplaceRule('(?<![_a-z0-9])begin|end\.?(?![_0-9a-z])\s*', ''),

        # conditional clauses (while/if/elif)

        ReReplaceRule(r'else\s+if\s+(?P<condition>.+)(\s*|\))\sthen',
                      'if \g<condition>:'),

        ReReplaceRule(r'if\s+(?P<condition>.+)(\s*|\))\sthen',
                      'if \g<condition>:'),

        ReReplaceRule(r'while\s+(?P<condition>.+)(\s*|\))\sdo',
                      'while \g<condition>:'),

        # repeat/ until

        ReReplaceRule('(?<![_a-z0-9])repeat(?![_0-9a-z])', 'while True:'),

        ReReplaceRule('^\s*(?<![_a-z0-9])until\s+(?P<condition>.+)', 'if \g<condition>: break', add_prev_indent=True),

        # then

        ReReplaceRule('(?<![_a-z0-9])then(?![_0-9a-z])$', ':'),

        # else

        ReReplaceRule('(?<![_a-z0-9])else(?![_0-9a-z])', 'else:'),

        # all *= rules

        ReReplaceRule('(?<![<>:!])=', '=='),

        ReReplaceRule('(?P<var_name>[^\s]+)\s*:=\s*', '\g<var_name> = '),

        ReReplaceRule('<>', '!='),

        # functions/operators

        ReReplaceRule('(?<![_a-z0-9])length', 'len'),

        ReReplaceRule.maybe(allow_numpy)('(?<![_a-z0-9])length2\(', 'np.size(', hook=pre_words.partial_part('numpy')),

        ReReplaceRule('(?<![_a-z0-9])(str|float|int)to(?P<dest>str|float|int)\s*\(', '\g<dest>(', conv=str.lower),

        ReReplaceRule('(?<![_a-z0-9])exp\s*\(', 'math.exp(', hook=pre_words.partial_part('math')),

        ReReplaceRule('(?<![_a-z0-9])(ln|log)(?P<base>[0-9]*)\s*\(', 'math.log\g<base>(',
                      hook=pre_words.partial_part('math')),

        ReReplaceRule('(?<![_a-z0-9])floor\s*\(', 'math.floor(',
                      hook=pre_words.partial_part('math')),

        ReReplaceRule('(?<![_a-z0-9])ceil\s*\(', 'math.ceil(',
                      hook=pre_words.partial_part('math')),

        ReReplaceRule('(?<![_a-z0-9])power\s*\(', 'pow('),

        ReReplaceRule('(?<![_a-z0-9])random\s*\(', 'random.uniform(0,', hook=pre_words.partial_part('random')),

        ReReplaceRule('(?<![_a-z0-9])randomint\s*\((?P<args>.*)\)', 'random.randint(0,\g<args>-1)',
                      hook=pre_words.partial_part('random')),

        ReReplaceRule('(?<![_a-z0-9])normaldistribution\s*\(', 'random.normalvariate(',
                      hook=pre_words.partial_part('random')),

        ReReplaceRule.maybe(allow_numpy)('(?<![_a-z0-9])SetArray[123]\((?P<lengths>.*)\)', 'np.zeros((\g<lengths>))',
                                         hook=pre_words.partial_part('numpy')),

        ReReplaceRule('(?<![_a-z0-9])SetArray\((?P<length>.*)\)',
                      '[None]*\g<length>'),

        ReReplaceRule('(?<![_a-z0-9])nil(?![_0-9a-z])',
                      'None'),

        ReReplaceRule('\$(?P<num>[a-f0-9]+)',
                      '0x\g<num>'),

        ReReplaceRule('\s+div\s+',
                      '//'),

        # all new rules go BEFORE the NotSupportedRules

        NotSupportedRule('(\{|#|\(\*)\s*\$', 'pre-processor directives not supported'),

        NotSupportedRule('(?<![_a-z0-9])goto\s', 'goto statements are not supported'),

        # this rule goes absolutely last

        HaltRule(),
    )

    return RuleSet(pre_words=pre_words, post_words=post_words, rules=rules)
