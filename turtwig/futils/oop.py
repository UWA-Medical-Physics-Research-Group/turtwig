"""
Functions for dealing with object-oriented programming.
"""

from copy import deepcopy
from typing import Callable

import toolz as tz

from .common import side_effect


def call_method[
    T
](method_name: str, pure: bool = True, /, *args, **kwargs) -> Callable[[T], T]:
    """
    Return a function that take an object, calls `method_name` on it, and returns the object

    Parameters
    ----------
    method_name: str
        Name of the method to call
    pure: bool
        If True, the input object is copied before calling the method to avoid
        modifying the input object.
    args, kwargs: any
        Arguments to pass to the method

    Returns
    -------
    Callable[[T], T]
        Unary Function that takes an object, calls `method_name` on it, and
        returns the object

    Examples
    --------
    >>> class Test:
    ...     def __init__(self, x):
    ...         self.x = x
    ...     def add(self, y):
    ...         self.x += y
    >>> test = Test(5)
    >>> test2 = call_method("add", y=3, pure=True)(test)
    >>> test2.x
    8
    >>> test.x   # original object is not modified
    5
    >>> test is test2
    False
    >>> test3 = call_method("add", y=3, pure=False)(test)
    >>> test3.x
    8
    >>> test.x   # original object is modified
    8
    >>> test is test3
    True
    """
    return lambda obj: tz.pipe(
        obj if not pure else deepcopy(obj),
        side_effect(
            lambda obj: getattr(obj, method_name)(*args, **kwargs), pass_val=True
        ),
    )
