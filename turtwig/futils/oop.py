"""
Functions for dealing with object-oriented programming.
"""
from copy import deepcopy
from typing import Callable
import toolz as tz

from .common import side_effect

def call_method[T](method_name: str, pure: bool = True, /, *args, **kwargs) -> Callable[[T], T]:
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
    """
    return lambda obj: tz.pipe(
        obj if not pure else deepcopy(obj),
        side_effect(lambda obj: getattr(obj, method_name)(*args, **kwargs), pass_val=True),
    )
