"""
Wrappers for functions
"""

from functools import wraps
from typing import Callable

from toolz import curry as _curry


def curry(func: Callable) -> Callable:
    """
    Allow a function to be partially parameterised.

    If a curried function is passed only some of its
    arguments, a new function is returned with those
    arguments filled in. The new function can be called
    with the remaining arguments later on.

    This is just a wrapper that passes docstring of the
    wrapped function to the @curry decorator from toolz.

    Example
    -------
    >>> @curry
    ... def add(a, b, c=3):
    ...     return a + b + c
    >>> # If not all required parameters are provided, a function is returned
    >>> add_5 = add(5)  # equivalent to lambda b: 5 + b + 3
    >>> add_5(3) # call with remaining argument
    11
    >>> add(5, 3)  # using function normally
    11
    """

    @wraps(func)
    def curried(*args, **kwargs) -> Callable:
        return _curry(func)(*args, **kwargs)  # type: ignore

    return curried
