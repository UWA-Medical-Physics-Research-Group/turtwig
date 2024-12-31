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
    """
    assert all(dicts[0].keys() == d.keys() for d in dicts)
    return dicts
