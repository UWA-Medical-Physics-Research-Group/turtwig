"""
Validation functions for dictionaries.
"""


def all_same_keys(dicts: list[dict]) -> list[dict]:
    """
    Assert if all dictionaries have the same keys.

    Parameters
    ----------
    dicts : list[dict]
        List of dictionaries to check.

    Returns
    -------
    list[dict]
        The input list of dictionaries.

    Example
    -------
    >>> from pydantic import AfterValidator, validate_call
    >>> from typing import Annotated
    >>> @validate_call()
    ... def test(
    ...     dicts: Annotated[list[dict], AfterValidator(all_same_keys)]
    ... ):
    ...     return dicts
    ...
    >>> test([{"a": 1, "b": 2}, {"a": 3, "b": 4}])
    [{'a': 1, 'b': 2}, {'a': 3, 'b': 4}]
    >>> test([{"a": 1, "b": 2}, {"a": 3}])  # Error, all dictionaries must have the same keys
    >>> test([{"a": 1, "b": 2}, {"a": 3, "c": 4}])  # Error, all dictionaries must have the same keys
    """
    assert all(
        dicts[0].keys() == d.keys() for d in dicts
    ), "All dictionaries must have the same keys"
    return dicts
