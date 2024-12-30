"""
Collection of functions to preprocess numpy arrays and patient scans
"""

from typing import Annotated, Iterable, Iterator, Literal, Optional, Sequence

import numpy as np
import SimpleITK as sitk
import toolz as tz
from loguru import logger
from toolz import curried
from pydantic import validate_call

from turtwig.validation.datatype import NumpyArray

from ..futils import call_method, curry, pmap, transform_nth
from ..validation import MaskDict, PatientScan



@curry
@validate_call()
def map_interval(
    array: Annotated[np.ndarray, NumpyArray[np.number]],
    from_range: tuple[np.number, np.number],
    to_range: tuple[np.number, np.number],
) -> Annotated[np.ndarray, NumpyArray[np.float64]]:
    """
    Map values in an `array` in range `from_range` to `to_range`
    """
    return tz.pipe(
        array,
        lambda a: np.array(
            (a - from_range[0]) / float(from_range[1] - from_range[0]), dtype=np.float64
        ),
        lambda arr_scaled: to_range[0] + (arr_scaled * (to_range[1] - to_range[0])),
    )


def z_score_scale(array: np.ndarray) -> np.ndarray:
    """
    Z-score normalise `array` to have mean 0 and standard deviation 1

    Calculated as (x - mean) / std
    """
    return (array - array.mean()) / array.std()


@curry
def make_isotropic(
    array: np.ndarray,
    spacings: Sequence[np.number],
    method: Literal["nearest", "linear", "b_spline", "gaussian"] = "linear",
) -> np.ndarray:
    """
    Return an isotropic array with uniformly 1 unit of spacing between coordinates

    Array can ONLY be **2D** or **3D**.

    Parameters
    ----------
    spacings : Sequence[np.number]
        Spacing of coordinate points for each axis
    array : np.nddarray
        Either a **2D** or **3D** array to interpolate
    method : str, optional
        Interpolation method, by default "linear"

    Returns
    -------
    np.ndarray
        Interpolated array on an isotropic grid
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
        lambda arr: arr.astype(np.float32),
        # sitk moves (H, W, D) to (D, W, H) >:( move axis here so img is (H, W, D)
        lambda arr: np.moveaxis(arr, 1, 0),  # width to first axis
        lambda arr: (
            np.moveaxis(arr, -1, 0) if len(arr.shape) == 3 else arr
        ),  # depth to first axis
        sitk.GetImageFromArray,
        call_method("SetOrigin", (0, 0, 0)),
        call_method("SetSpacing", spacings),
        lambda img: sitk.Resample(
            img,
            new_size,
            sitk.Transform(),
            interpolators[method],
            img.GetOrigin(),
            (1, 1, 1),  # new spacing
            img.GetDirection(),
            0,
            img.GetPixelID(),
        ),
        sitk.GetArrayFromImage,
        # arr is (D, W, H) move back to (H, W, D)
        lambda arr: (
            np.moveaxis(arr, 0, -1) if len(arr.shape) == 3 else arr
        ),  # move depth to last axis
        lambda arr: np.moveaxis(arr, 1, 0),  # height to first axis
        lambda arr: arr.astype(old_datatype),
    )


@curry
def filter_roi_names(
    roi_names: list[str],
    keep_list: list[str] = c.ROI_KEEP_LIST,
    exclusion_list: list[str] = c.ROI_EXCLUSION_LIST,
) -> list[str]:
    """
    Filter out ROIs based on keep and exclusion lists

    Parameters
    ----------
    roi_names : list[str]
        Array of ROI names
    keep_list : list[str]
        List of substrings to keep
    exclusion_list : list[str]
        List of substrings to exclude

    Returns
    -------
    list[str]
        Array of ROI names not in exclusion list and containing any substring in keep list
    """

    def is_numeric(name):
        try:
            float(name)
            return True
        except ValueError:
            return False

    def not_excluded(name):
        return not any(
            exclude in name for exclude in exclusion_list
        ) and not is_numeric(name)

    return tz.pipe(
        roi_names,
        curried.filter(not_excluded),
        curried.filter(lambda name: any(keep in name for keep in keep_list)),
        list,
    )


@curry
def find_organ_roi(organ: str, roi_lst: list[str]) -> Optional[str]:
    """
    Find a unique ROI name in the list that contains the organ names (possibly multiple)

    If more than one ROI name correspond to the organ, the shortest name is chosen.
    If multiple ROI names have the shortest length, the first one in alphabetical
    order is chosen. None is returned if no ROI name is found.
    """
    return tz.pipe(
        roi_lst,
        sorted,
        curried.filter(lambda name: name in c.ORGAN_MATCHES[organ]),
        list,
        # encase [min(...)] in list as we will use lst[0] later
        lambda names: [min(names, key=len)] if len(names) > 1 else names,
        lambda name: None if name == [] else name[0],
    )  # type: ignore


def _bounding_box3d(img: np.ndarray):
    """
    Compute bounding box of a 3d binary array
    """
    r = np.any(img, axis=(1, 2))
    c = np.any(img, axis=(0, 2))
    z = np.any(img, axis=(0, 1))

    rmin, rmax = np.where(r)[0][[0, -1]]
    cmin, cmax = np.where(c)[0][[0, -1]]
    zmin, zmax = np.where(z)[0][[0, -1]]

    return rmin, rmax, cmin, cmax, zmin, zmax


@curry
def crop_to_body(
    vol_mask: tuple[np.ndarray, np.ndarray],
    trim_border_px: int = 5,
    thresh: float = c.BODY_THRESH,
):
    """
    Crop both `x`, `y` to bounding box of the body using threshold thresh

    Parameters
    ----------
    vol_mask: tuple[np.ndarray, np.ndarray]
        Volume and mask arrays of shape (C, H, W, D)
    trim_border_px : int
        Number of pixels to crop from the borders before computing bounding box, used
        to avoid artefacts at the border
    thresh : float
        Threshold to use for body segmentation. After thresholding, 1 should represent
        the body region.
    """
    # crop borders to avoid high pixel values along image border
    vol, mask = tuple(
        arr[
            :,
            trim_border_px:-trim_border_px,
            trim_border_px:-trim_border_px,
            trim_border_px:-trim_border_px,
        ]
        for arr in vol_mask
    )
    body_mask = vol > thresh
    rmin, rmax, cmin, cmax, zmin, zmax = _bounding_box3d(body_mask[0])
    return tuple(arr[:, rmin:rmax, cmin:cmax, zmin:zmax] for arr in [vol, mask])


@logger.catch()
@curry
def preprocess_volume(
    volume: np.ndarray,
    spacings: tuple[float, float, float],
    interpolation: str = "linear",
) -> np.ndarray:
    """
    Return preprocessed volume of shape (1, H, W, D)

    Parameters
    ----------
    volume : np.ndarray
        Volume array of shape (H, W, D)
    spacings : tuple[float, float, float]
        Spacing of coordinate points for each axis
    interpolation : str
        Interpolation method, one of "nearest", "linear", "b_spline", "gaussian"
    """
    assert len(volume.shape) == 3, "Volume must be of shape (H, W, D)"
    return tz.pipe(
        volume,
        make_isotropic(spacings=spacings, method=interpolation),
        curry(np.expand_dims)(axis=0),  # Add channel dimension, now (C, H, W, D)
    )


@logger.catch()
@curry
def preprocess_mask(
    mask: MaskDict, spacings: tuple[float, float, float], organ_ordering: list[str]
) -> Optional[np.ndarray]:
    """
    Return preprocesed `mask` of shape (C, H, W, D) where C is the number of organs

    Parameters
    ----------
    mask : MaskDict
        Dictionary of masks for different organs
    spacings : tuple[float, float, float]
        Spacing of coordinate points for each axis
    organ_ordering : list[str]
        List of organ names in order to keep
    """
    # List of organ names to keep
    names = tz.pipe(
        mask.keys(),
        filter_roi_names,
        lambda mask_names: [
            find_organ_roi(organ, mask_names) for organ in organ_ordering
        ],
        curried.filter(lambda m: m is not None),
        list,
    )
    # If not all organs are present, return None
    if len(names) != len(c.ORGAN_MATCHES):
        return None

    return tz.pipe(
        mask,
        curried.keyfilter(lambda name: name in names),
        curried.valmap(make_isotropic(spacings=spacings, method="nearest")),
        # to (organ, height, width, depth)
        lambda mask: np.stack(list(mask.values()), axis=0),
    )  # type: ignore


@logger.catch()
@curry
def preprocess_patient_scan(
    scan: PatientScan,
    min_size: tuple[int, int, int],
    organ_ordering: list[str] = list(c.ORGAN_MATCHES.keys()),
) -> Optional[PatientScan]:
    """
    Preprocess a PatientScan object into (volume, masks) pairs of shape (C, H, W, D)

    Mask for multiple organs are stacked along the first dimension to have shape
    (organ, height, width, depth). Mask is `None` if not all organs are present.

    Parameters
    ----------
    scan : PatientScan
        PatientScan object
    min_size : tuple[int, int, int]
        Minimum size for volume and masks
    organ_ordering : list[str]
        List of organ names in order to keep
    """
    assert isinstance(scan["masks"], dict), "Masks must be a dictionary"
    old_mask_keys = scan["masks"].keys()

    scan = tz.pipe(
        scan,
        curried.update_in(
            keys=["volume"], func=preprocess_volume(spacings=scan["spacings"])
        ),
        curried.update_in(
            keys=["masks"],
            func=preprocess_mask(
                spacings=scan["spacings"], organ_ordering=organ_ordering
            ),
        ),
        curried.update_in(keys=["organ_ordering"], func=lambda _: organ_ordering),
    )
    if scan["masks"] is None:
        raise ValueError(
            f"Missing organs in {scan["patient_id"]} with required organs {organ_ordering}, "
            f"available organs: {old_mask_keys}",
        )

    scan["volume"], scan["masks"] = tz.pipe(
        (scan["volume"], scan["masks"]),
        crop_to_body,
        ensure_min_size(min_size=min_size),
        curried.map(lambda arr: arr.astype(np.float32)),
        # Z-score normalisation has to come after cropping
        # cropping uses thresholding, z-score before will change the intensities!
        transform_nth(0, z_score_scale),
        tuple,
    )

    return scan  # type: ignore


@curry
def preprocess_dataset(
    dataset: Iterable[PatientScan],
    min_size: tuple[int, int, int],
    organ_ordering: list[str] = list(c.ORGAN_MATCHES.keys()),
    n_workers: int = 1,
) -> Iterator[PatientScan]:
    """
    Preprocess a dataset of PatientScan objects into (volume, masks) pairs

    Mask for multiple organs are stacked along the first dimension to have
    shape (n_organs, height, width, depth). An instance is filtered out if
    not all organs are present.

    Parameters
    ----------
    dataset : Iterable[PatientScan | None]
        Dataset of PatientScan objects
    min_size : tuple[int, int, int]
        Minimum size for volume and masks
    organ_ordering : list[str]
        List of organ names in order to keep
    n_workers : int
        Number of parallel processes to use, set to <= 1 to disable, by default 1
    """
    mapper = pmap(n_workers=n_workers) if n_workers > 1 else curried.map
    preprocessor = tz.pipe(
        preprocess_patient_scan(min_size=min_size, organ_ordering=organ_ordering),
        logger.catch(),  # catch() don't work if the function is curried... wrap again
    )
    return tz.pipe(
        dataset,
        mapper(preprocessor),
        curried.filter(lambda scan: scan is not None),
    )  # type: ignore
