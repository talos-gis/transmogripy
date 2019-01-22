from typing import Dict, ClassVar

from transmogripy.__data__ import __version__

from functools import partial


class Segment:
    """
    A collection of parts that appears in the output file.
    This class is meant to be subclassed with a PARTS class member.
    """

    PARTS: ClassVar[Dict['str', 'str']]  # virtual member

    def __init__(self):
        self.raw_parts = []
        self.activated = set()  # so we don't add the same part twice

    def add_part(self, part_name):
        if part_name in self.activated:
            return
        val = self.PARTS[part_name]
        self.raw_parts.append(val)
        self.activated.add(part_name)

    def add_raw(self, part_string):
        self.raw_parts.append(part_string)

    def partial_part(self, part_name):
        return partial(self.add_part, part_name)

    def __iter__(self):
        yield from self.raw_parts

    def join(self, sep='\n'):
        return sep.join(self)


class PreWord(Segment):
    PARTS = {
        'numpy': 'import numpy as np',
        'math': 'import math',
        'random': 'import random',
        'disclose':
            f'"""\nthis script was automatically converted from pascal using transmogripy v{__version__}\n"""\n',
    }

    def join(self, *args, **kwargs):
        return super().join(*args, **kwargs) + '\n' * 2


class PostWord(Segment):
    PARTS = {}

    def join(self, *args, **kwargs):
        return '\n' * 2 + super().join(*args, **kwargs)
