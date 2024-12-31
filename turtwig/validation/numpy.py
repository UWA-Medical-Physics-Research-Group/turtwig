"""
Validation functions for numpy arrays.
"""

import numpy as np

from ..futils import curry


@curry
def is_ndim(arr: np.ndarray, *, ndim: int | list[int] | tuple[int]) -> np.ndarray:
    """
    Assert that ``arr`` has ``ndim`` dimensions.

    Parameters
    ----------
    arr : np.ndarray
        Array to check.
    ndim : int | list[int] | tuple[int]
        Number of dimensions to check for. If a list or tuple, check
        for any of the dimensions in the list.
    
    Returns
    -------
    np.ndarray
        The input array.

    Example
    -------
    >>> from pydantic import AfterValidator, validate_call
    >>> from typing import Annotated
    >>> import numpy as np
    >>> @validate_call()
    ... def test(
    ...     arr: Annotated[np.ndarray, AfterValidator(is_ndim(ndim=2))]
    ... ):
    ...     return arr
    ...
    >>> test(np.array([[1, 2], [3, 4]]))
    array([[1, 2],
           [3, 4]])
    >>> test(np.array([1, 2, 3])) # Error, expected 2 dimensions, got 1
    >>> test(np.array([[[1, 2], [3, 4]], [[5, 6], [7, 8]]])) # Error, expected 2 dimensions, got 3
    """
    if isinstance(ndim, int):
        assert (
            len(arr.shape) == ndim
        ), f"Expected {ndim} dimensions, got {len(arr.shape)}"
    elif isinstance(ndim, list | tuple):
        assert (
            len(arr.shape) in ndim
        ), f"Expected {ndim} dimensions, got {len(arr.shape)}"
    else:
        raise TypeError(f"Expected int, list, or tuple, got {type(ndim)}")
    return arr
