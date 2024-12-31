"""
Functions for serialising and deserialising data to and from HDF5 files.
"""

from datetime import date
from pathlib import Path
from typing import Any

import h5py
import numpy as np
from loguru import logger
from pydantic import validate_call

from ..futils import curry
from ..validation import H5File, H5Group, NumpyArray

SUPPORTED_TYPES = str | int | float | date | dict | NumpyArray | tuple | list | None


@curry
@validate_call()
def dict_to_h5(
    data: dict[str, SUPPORTED_TYPES],
    hf: H5File | H5Group | str | Path,
) -> None:
    """
    Serialise a dictionary to an h5 file. Supported types are:
    - str, int, float: saved as is
    - date: saved as a string
    - dict: saved as a group recursively
    - np.ndarray: saved as a dataset
    - tuple/list: If all elements are numeric or are numpy arrays,
      saved as a dataset. Else, saved as a group with indices as keys
    - None: skipped

    Parameters
    ----------
    dict_: dict
        Dictionary to save. Each value is saved as a dataset or group.
    hf: h5py.File | h5py.Group | str | Path
        H5 file or group to save to. If a string or Path, then the file
        is opened in append mode
    """
    if isinstance(hf, str | Path):
        with h5py.File(hf, "a") as hf:
            dict_to_h5(data, hf)
        return

    for key, val in data.items():
        match val:
            case x if isinstance(x, str | int | float):
                hf[key] = val
            case x if isinstance(x, date):
                hf[key] = str(val)
            case x if isinstance(x, dict):
                group = hf.create_group(key)
                dict_to_h5(val, group)
            case x if isinstance(x, np.ndarray) or (
                isinstance(x, tuple | list)
                and all(isinstance(i, int | float | np.ndarray) for i in x)
            ):
                hf.create_dataset(key, data=val, compression="gzip")
            case x if isinstance(x, list | tuple):
                group = hf.create_group(key)
                dict_to_h5({str(i): v for i, v in enumerate(x)}, group)
            case x if x is None:
                pass
            case _:
                logger.warning(f"Unsupported type {type(val)} for key {key}, skipping")


@validate_call()
def dict_from_h5(hf: H5File | H5Group | str | Path) -> dict[str, Any]:
    """
    Load a h5 file as a dictionary.

    WARNING: this loads the entire H5 file at once. To take advantage
    of lazy loading, use the ``h5py`` library directly.

    Parameters
    ----------
    hf: h5py.File | h5py.Group | str | Path
        H5 file or group to load from. If a string or Path, then the file
        is opened in read mode

    Returns
    -------
    dict
        Dictionary loaded from the h5 file
    """

    def load_value(val: Any) -> Any:
        match val:
            case x if isinstance(x, h5py.Dataset):
                if isinstance(val[()], bytes):
                    return val[()].decode()
                return val[()]
            case x if isinstance(x, h5py.Group):
                return load_dict(val)
            case _:
                return val

    def load_dict(hf: h5py.File | h5py.Group) -> dict[str, Any]:
        return {key: load_value(val) for key, val in hf.items()}

    if isinstance(hf, str | Path):
        with h5py.File(hf, "r") as hf:
            return load_dict(hf)

    return load_dict(hf)
