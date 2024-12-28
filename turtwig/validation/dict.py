def assert_all_same_keys(dicts: list[dict]):
    """
    Assert if all dictionaries have the same keys.

    Parameters
    ----------
    dicts : list[dict]
        List of dictionaries to check.

    Side Effects
    ------------
    AssertionError
        Raised if not all dictionaries have the same keys.
    """
    assert all(dicts[0].keys() == d.keys() for d in dicts)
