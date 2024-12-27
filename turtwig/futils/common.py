"""
Collection of common utility functions
"""

from itertools import starmap as _starmap
from typing import Any, Callable, Iterable, Iterator

from .wrappers import curry


def star[T](f: Callable[..., T]) -> Callable[..., T]:
    """
    Returns function: x -> `f`(*x), i.e. unpacks arguments and pass to `f`

    Parameters
    ----------
    f : Callable[..., T]
        Function to be called

    Returns
    -------
    Callable[..., T]
        Function that unpacks the argument and pass them to `func`

    Examples
    --------
    >>> def add(a, b):
    ...     return a + b
    >>> star(add)((1, 2)) # equivalent to add(*(1, 2))
    3
    >>> add((1, 2)) # ERROR
    """
    return lambda args: f(*args)


@curry
def starmap[T](f: Callable[..., T], iterable: Iterable[tuple[Any]]) -> Iterator[T]:
    """
    Map non-unary function `f(a, b, ...)` over the elements of `iterable`.

    Used this instead of `map` when argument parameters have already been 
    “pre-zipped” into tuples.

    Curried version of `itertools.starmap`.

    Parameters
    ----------
    f : Callable[..., T]
        Function to be called on each element of `iterable`
    iterable : Iterable[tuple[Any]]
        Iterable of tuples of arguments

    Returns
    -------
    Iterator[T]
        Iterator of results of calling `f` on each element of `iterable`
    
    Examples
    --------
    >>> def add(a, b):
    ...     return a + b
    >>> lst = [(1, 2), (3, 4)]
    >>> list(starmap(add, lst))
    [3, 7]
    """
    return _starmap(f, iterable)


@curry
def starfilter(
    f: Callable[..., bool], iterable: Iterable[tuple[Any, ...]]
) -> Iterator[tuple[Any, ...]]:
    """
    Filter elements of `iterable` using non-unary function `f(a, b, ...)`

    Used this instead of `filter` when argument parameters have already been
    “pre-zipped” into tuples.

    Parameters
    ----------
    f : Callable[..., bool]
        Function to be called on each element of `iterable`
    iterable : Iterable[tuple[Any]]
        Iterable of tuples of arguments

    Returns
    -------
    Iterator[tuple[Any, ...]]
        Iterator of elements of `iterable` for which `f` returns True
    
    Examples
    --------
    >>> def is_even(a, b):
    ...     return (a + b) % 2 == 0
    >>> lst = [(1, 2), (3, 4), (4, 4)]
    >>> list(starfilter(is_even, lst))
    [(4, 4)]
    """
    return filter(star(f), iterable)


@curry
def iterate_while[
    T, R
](f: Callable[[T], R], pred: Callable[[T | R], bool], initial: T) -> R | T:
    """
    Repeatedly apply `f` to a value until `pred(value)` is false

    Parameters
    ----------
    `f` : Callable[[T], R]
        Function to be called repeatedly
    pred : Callable[[T | R], bool]
        Function that takes the output of `f` and returns a boolean
    initial : T
        Initial value to be passed to `f`

    Returns
    -------
    R | T
        Output of `f` when condition is met

    Examples
    --------
    >>> def f(x):
    ...     return x + 1
    >>> def pred(x):
    ...     return x < 5
    >>> iterate_while(f, pred, 0)
    5
    >>> iterate_while(f, pred, 5)
    5
    """
    return iterate_while(f, pred, f(initial)) if pred(initial) else initial


@curry
def side_effect[T](func: Callable[..., Any], val: T, pass_val: bool = False) -> T:
    """
    Perform side effect by calling `func` and let `val` pass through

    Parameters
    ----------
    func : Callable
        Function to be called, cannot take any arguments if `pass_val` is False,
        otherwise must take `val` as its only argument
    val : T
        Value to be returned
    pass_val : bool
        Whether to pass `val` to `func`

    Returns
    -------
    T
        The input value `val`

    Examples
    --------
    >>> def print_something():
    ...     print("Hello")
    >>> a = side_effect(print_something, 5)
    Hello
    >>> a
    5
    >>> def print_val(val):
    ...     print(val)
    >>> b = side_effect(print_val, 5, pass_val=True)
    5
    >>> b
    5
    """
    if pass_val:
        func(val)
    else:
        func()
    return val
