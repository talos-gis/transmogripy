from typing import Union, Callable, Optional, List

from abc import ABC, abstractmethod

import re

from transmogripy.__util import *


class Final(str):
    """
    a string component in a line that should not be run through any more rules
    """
    __slots__ = ()
    pass


class LineComponents:
    """
    Like a list, but setting a cell with an iterable instead inserts it at the area
    >>> x = LineComponents('')
    >>> x.parts = ['a', 'bcd', 'e']
    >>> ' '.join(x)
    'a bcd e'
    >>> x[1] = ['b', 'c', 'd']
    >>> ' '.join(x)
    'a b c d e'
    """

    def __init__(self, start: str):
        self.parts: List[str] = [start]

    def non_final_part(self):
        """
        get the index and value of the first element in the list that is not a member of the Final class
        """
        return next(
            ((i, p) for (i, p) in enumerate(self.parts) if not isinstance(p, Final)),
            None)

    def __setitem__(self, key, value):
        if not isinstance(value, str):
            key = slice(key, key + 1)
            value = (v for v in value if v)
        self.parts[key] = value

    def __iter__(self):
        yield from self.parts

    def __len__(self):
        return len(self.parts)


class Rule(ABC):
    @abstractmethod
    def __call__(self, line, env) -> Union[str, None, List[Union[str, Final]]]:
        """
        :return: None if the line hasn't changed, or the line if it is changed,
            a list if the rule causes a split in the captured pattern.
        """
        return None

    @classmethod
    def maybe(cls, cond):
        if cond:
            return cls
        return _NilRule


class _NilRule(Rule):
    _single = None

    def __new__(cls, *args, **kwargs):
        if not cls._single:
            cls._single = super().__new__(cls)
        return cls._single

    def __call__(self, line, env):
        return None


class PatternRule(Rule, ABC):
    def __init__(self, pattern: str):
        self.pattern = re.compile(pattern, re.IGNORECASE)


class EarlyReturnRule(PatternRule):
    def __call__(self, line, env):
        if self.pattern.search(line):
            raise EarlyReturnDetected()
        return None


class ReReplaceRule(PatternRule):
    def __init__(self, pattern: str, sub: str, add_prev_indent=False, hook: Optional[Callable[[], None]] = None,
                 demand_last_component=False, conv: Optional[Callable[[str], str]] = None):
        super().__init__(pattern)
        self.sub = sub
        self.add_prev_indent = add_prev_indent
        self.hook = hook
        self.demand_last_component = demand_last_component
        self.output_convert = conv

    def __call__(self, line, env):
        if self.demand_last_component and not env['last_component']:
            return None
        ret, n = self.pattern.subn(self.sub, line)
        if n == 0:
            return None
        if self.output_convert:
            ret = self.output_convert(ret)
        if self.add_prev_indent:
            ret = env['prev_indent'] + ret
        if self.hook:
            self.hook()
        return ret


class ReReplaceFinalRule(PatternRule):
    def __init__(self, pattern: str, sub: str):
        super().__init__(pattern)
        self.sub = sub

    def __call__(self, line, env):
        ret = []
        while True:
            next_match = self.pattern.search(line)
            if not next_match:
                if not ret:
                    return None
                ret.append(line)
                break
            ret.append(line[:next_match.start()])
            match_sub = next_match.expand(self.sub)
            ret.append(Final(match_sub))
            line = line[next_match.end():]
        return ret


class NotSupportedRule(PatternRule):
    def __init__(self, pattern: str, msg: str):
        super().__init__(pattern)
        self.msg = msg

    def __call__(self, line, env):
        if self.pattern.search(line):
            raise NotImplementedError(self.msg)
        return None


class HaltRule(Rule):
    def __call__(self, line, env):
        return [Final(line)]
