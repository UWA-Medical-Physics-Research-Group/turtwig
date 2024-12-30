"""
Collection of functions to process numpy arrays
"""

from typing import Annotated, Literal

import numpy as np
import SimpleITK as sitk
import toolz as tz
from fn import _
from pydantic import AfterValidator, validate_call

from turtwig.validation.datatype import NumpyNumber

from ..futils import call_method, curry, star
from ..validation import NumpyArray, is_ndim


@curry
@validate_call()
def map_interval(
    array: Annotated[np.ndarray, NumpyArray[NumpyNumber]],
    from_range: tuple[int | float, int | float],
    to_range: tuple[int | float, int | float],
) -> Annotated[np.ndarray, NumpyArray[np.float64]]:
    """
    Map values in an `array` in range `from_range` to `to_range`

    Parameters
    ----------
    array : np.ndarray
        Array with numeric elements to map
    from_range : tuple[int | float, int | float]
        Range of values in `array`, a tuple of (min, max) values
    to_range : tuple[int | float, int | float]
        Range of values to map to, a tuple of (min, max) values

    Returns
    -------
    np.ndarray
        Array with values mapped to range `to_range`

    Examples
    --------
    >>> a = np.array([1, 2, 3, 4, 5])
    >>> map_interval(a, (1, 5), (0, 1))
    array([0.  , 0.25, 0.5 , 0.75, 1.  ])
    """
    return tz.pipe(
        array,
        lambda a: np.array(
            (a - from_range[0]) / float(from_range[1] - from_range[0]), dtype=np.float64
        ),
        lambda arr_scaled: to_range[0] + (arr_scaled * (to_range[1] - to_range[0])),
    )


@validate_call()
def z_score_scale(
    array: Annotated[np.ndarray, NumpyArray[NumpyNumber]],
) -> Annotated[np.ndarray, NumpyArray[np.float64]]:
    """
    Z-score normalise `array` to have mean 0 and standard deviation 1

    Z-score normalisation is calculated as (x - mean) / std

    Parameters
    ----------
    array : np.ndarray
        Array with numeric elements to normalise

    Returns
    -------
    np.ndarray
        Normalised array with mean 0 and standard deviation 1

    Examples
    --------
    >>> a = np.array([1, 2, 3, 4, 5])
    >>> a_normed = z_score_scale(a)
    >>> a_normed.mean(), a_normed.std()
    np.float64(0.0), np.float64(0.9999999999999999)
    """
    return (array - array.mean()) / array.std()


@curry
@validate_call()
def make_isotropic(
    array: Annotated[
        np.ndarray, NumpyArray[NumpyNumber], AfterValidator(is_ndim(ndim=[2, 3]))
    ],
    spacings: list[int | float] | tuple[int | float],
    method: Literal["nearest", "linear", "b_spline", "gaussian"] = "linear",
) -> np.ndarray:
    """
    Return an isotropic array with uniformly 1 unit of spacing between coordinates

    Only accepts arrays of shape (H, W, D) or (H, W) for 2D and 3D arrays respectively

    Parameters
    ----------
    array : np.nddarray
        A 2D or 3D array to interpolate
    spacings : list[int | float] | tuple[int | float]
        Spacing of coordinate points for each dimension
    method : str, optional
        Interpolation method, by default "linear"

    Returns
    -------
    np.ndarray
        Interpolated array on an isotropic grid

    Examples
    --------
    >>> a = np.array([[1.0, 2.0],
    ...               [3.0, 4.0]])
    >>> make_isotropic(a, [2, 2], method="linear")
    array([[1. , 1.5, 2. , 0. ],
           [2. , 2.5, 3. , 0. ],
           [3. , 3.5, 4. , 0. ],
           [0. , 0. , 0. , 0. ]])
    """
    interpolators = {
        "nearest": sitk.sitkNearestNeighbor,
        "linear": sitk.sitkLinear,
        "b_spline": sitk.sitkBSpline,
        "gaussian": sitk.sitkGaussian,
    }
    new_size = [
        int(round(old_size * old_spacing))
        for old_size, old_spacing, in zip(array.shape, spacings)
    ]
    old_datatype = array.dtype
    return tz.pipe(
        array,
        # sitk don't work with bool datatypes in mask array
        _.call("astype", np.float32),
        # sitk moves (H, W, D) to (D, W, H) >:( move axis here so array is (H, W, D)
        curry(np.moveaxis)(source=1, destination=0),  # width to first axis
        lambda arr: (
            np.moveaxis(arr, -1, 0) if len(arr.shape) == 3 else arr
        ),  # depth to first axis
        sitk.GetImageFromArray,
        call_method("SetOrigin", (0, 0, 0), pure=False),
        call_method("SetSpacing", spacings, pure=False),
        lambda arr: sitk.Resample(
            arr,
            new_size,
            sitk.Transform(),
            interpolators[method],
            arr.GetOrigin(),
            (1, 1, 1),  # new spacing
            arr.GetDirection(),
            0,
            arr.GetPixelID(),
        ),
        sitk.GetArrayFromImage,
        # arr is (D, W, H) move back to (H, W, D)
        lambda arr: (
            np.moveaxis(arr, 0, -1) if len(arr.shape) == 3 else arr
        ),  # move depth to last axis
        curry(np.moveaxis)(source=1, destination=0),  # height to first axis
        _.call("astype", old_datatype),
    )


@validate_call()
def bounding_box_3d(
    arr: Annotated[np.ndarray, NumpyArray, AfterValidator(is_ndim(ndim=3))],
) -> tuple[int, int, int, int, int, int]:
    """
    Compute bounding box of a 3D binary array

    Parameters
    ----------
    arr : np.ndarray
        3D binary array of boolean or numeric values. If numeric, 0 is
        considered background (i.e. False).

    Returns
    -------
    tuple[int, int, int, int, int, int]
        Bounding box coordinates of minimum and maximum values in each axis
        in the order of row, column, and depth

    Examples
    --------
    >>> a = np.zeros((10, 10, 10))
    >>> a[2:5, 3:7, 4:8] = 1
    >>> bounding_box_3d(a)
    (2, 4, 3, 6, 4, 7)
    """
    row = np.any(arr, axis=(1, 2))
    col = np.any(arr, axis=(0, 2))
    depth = np.any(arr, axis=(0, 1))

    row_min, row_max = np.where(row)[0][[0, -1]]
    col_min, col_max = np.where(col)[0][[0, -1]]
    depth_min, depth_max = np.where(depth)[0][[0, -1]]

    return row_min, row_max, col_min, col_max, depth_min, depth_max


@curry
def crop_to_bbox_3d(
    arr: Annotated[np.ndarray, NumpyArray, AfterValidator(is_ndim(ndim=3))],
    thresh: float | None = None,
):
    """
    Crop a 3D array to its bounding box, optionally thresholding the array first

    Parameters
    ----------
    arr : np.ndarray
        3D array to crop. Must be be binart if `thresh` is None.
    thresh : float, optional
        Threshold value to apply to the array before cropping if provided. If
        None, no thresholding is applied and `arr` is assumed to be binary. If
        provided, values greater than `thresh` are considered as True.

    Returns
    -------
    np.ndarray
        Cropped 3D array to its bounding box
    """
    return tz.pipe(
        arr,
        (_ > thresh) if thresh is not None else tz.identity,
        bounding_box_3d,
        star(
            lambda rmin, rmax, cmin, cmax, zmin, zmax: arr[
                :, rmin:rmax, cmin:cmax, zmin:zmax
            ]
        ),
    )
