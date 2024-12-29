"""
Utility functions for generating sequences
"""

from itertools import islice
from typing import Callable, Iterable, Iterator

import toolz as tz
import toolz.curried as curried

from .decorator import curry


@curry
def growby[
    T, R
](func: Callable[[T | R], R], init: T, length: int | None = None) -> Iterator[T | R]:
    """
    Grow a sequence by repeatedly applying `func` to last item in sequence

    Parameters
    ----------
    func : Callable
        Function to be called repeatedly on the last element of the sequence
    init : any
        Initial value of the sequence
    length : int | None
        Length of the sequence to be generated, if None, sequence is infinite

    Returns
    -------
    Iterator[T | R]
        Sequence constructed by repeatedly applying `func`, i.e. compute
        `[init, func(init), func(func(init)), ...]`

    Examples
    --------
    >>> list(growby(lambda x: x + 1, 1, length=5))
    [1, 2, 3, 4, 5]
    """
    return islice(tz.iterate(func, init), length)


@curry
def growby_fs[T, R](funcs: Callable[[T | R], R], init: T) -> Iterable[T | R]:
    """
    Grow a sequence by applying list of functions to the last element of the current sequence

    i.e. Given a list of functions `[f1, f2, ...]`, compute the sequence
    `[init, f1(init), f2(f1(init)), f3(f2(f1(init))), ...]`

    Parameters
    ----------
    funcs : Callable
        List of functions to be called on the last element of the sequence
    init: any
        Initial value of the sequence

    Returns
    -------
    Generator[T | R, None, None]
        Sequence constructed by repeatedly applying each function in `funcs`,
        `[init, f1(init), f2(f1(init)), ...]`

    Examples
    --------
    >>> fs = [lambda x: x + 1, lambda x: x * 2, lambda x: x ** 2]
    >>> list(growby_accum(fs, 1))
    [1, 2, 4, 16]
    """
    return tz.pipe(
        funcs,
        curried.cons(init),  # [init, f1, f2, ...]
        curried.accumulate(lambda x, f: f(x)),
    )  # type: ignore


@curry
def transform_nth(n: int, func: Callable, seq: Iterable) -> Iterable:
    """
    Apply a function `func` to the nth element of a sequence

    Parameters
    ----------
    n : int
        Index of the element to be transformed
    func : Callable
        Function to be applied to the nth element
    seq : Iterable
        Sequence to be transformed

    Returns
    -------
    Iterable
        Sequence with the nth element transformed

    Examples
    --------
    >>> list(transform_nth(1, lambda _: 'a', [1, 2, 3]))
    [1, 'a', 3]
    """
    return (func(x) if i == n else x for i, x in enumerate(seq))
