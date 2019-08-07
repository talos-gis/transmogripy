import ast


def is_valid_python(code):
    try:
        ast.parse(code)
    except SyntaxError as e:
        return False, e
    return True, None


def isblank(s: str):
    """
    >>> assert isblank('')
    >>> assert isblank('  ')
    >>> assert not isblank('   a    ')
    """
    return not s or s.isspace()


class TransmogripyWarning(UserWarning):
    """
    A warning indicating the resulting script might not work as intended
    """
    pass


class FatalTransmogripyWarning(TransmogripyWarning):
    """
    A warning indicating the result script doesn't pass basic sanity checks
    """
    pass


class EarlyReturnDetected(Exception):
    """
    An exception indicating an early return
    """


__all__ = ['is_valid_python', 'isblank', 'TransmogripyWarning', 'FatalTransmogripyWarning', 'EarlyReturnDetected']
