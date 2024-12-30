"""
Datatype definitions for validation.
"""

from datetime import date
from typing import Annotated, Any, TypedDict, get_args, get_origin

import h5py
import numpy as np
from pydantic import GetCoreSchemaHandler
from pydantic_core import CoreSchema, core_schema

MaskDict = dict[Annotated[str, "organ name"], np.ndarray]


PatientScan = TypedDict(
    "PatientScan",
    {
        "patient_id": int,
        "volume": np.ndarray,
        "dimension_original": tuple[int, int, int],
        "spacings": tuple[float, float, float],
        "modality": str,
        "manufacturer": str,
        "scanner": str,
        "study_date": date,
        "masks": np.ndarray | MaskDict,
        "organ_ordering": list[str],
    },
)


class NumpyArray:
    """
    Pydantic core schema for numpy arrays.

    You can either annotate using `NumpyArray` for a numpy array
    of any type, or `NumpyArray[type]` for a numpy array of a
    specific type.

    Examples
    --------
    >>> import numpy as np
    >>> from pydantic import validate_call
    >>> from typing import Annotated
    >>> @validate_call()
    ... def test(
    ...     a: Annotated[np.ndarray, NumpyArray],
    ...     b: Annotated[np.ndarray, NumpyArray[np.int64]],
    ...     c: Annotated[np.ndarray, NumpyArray[np.bool | np.int64]]
    ... ):
    ...     return a, b, c
    >>> test(np.array(['a']), np.array(1), np.array([True, 4]))  # no error
    (array(['a'], dtype='<U1'), array([1]), array([1, 4]))
    >>> test(np.array([5.0]), np.array([1]), np.array([]))  # no error
    (array([5.]), array([1]), array([], dtype=float64))
    >>> test(np.array(['a']), np.array(['a']), np.array([True, 4]))  # error
    >>> test(np.array(['a']), np.array('a'), np.array([True, 4]))  # error
    >>> test([1, 3], [1, 3], [1, 3])  # error
    """

    def __class_getitem__(cls, type_: type):  # type: ignore
        """
        Dynamically create a subclass of NumpyArray with the specified type.
        """

        class TypedNumpyArray(cls):
            # If type is annotated, get first argument (i.e. the wrapped type)
            type__: type | None = (
                type_ if not get_origin(type_) is Annotated else get_args(type_)[0]
            )

        TypedNumpyArray.__name__ = f"TypedNumpyArray[{type_}]"
        return TypedNumpyArray

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: GetCoreSchemaHandler
    ) -> CoreSchema:
        def all_are_type(arr: np.ndarray):
            if arr.ndim == 0:
                arr = np.atleast_1d(arr)
            if (
                not hasattr(cls, "type__")  # means cls is not typed
                or cls.type__ is None  # type: ignore
                or all(isinstance(i, cls.type__) for i in arr.ravel())  # type: ignore
            ):
                return arr
            raise ValueError(f"All items must be of the type {cls.type__}")  # type: ignore

        return core_schema.json_or_python_schema(
            json_schema=core_schema.chain_schema(
                [
                    core_schema.is_instance_schema(np.ndarray),
                    core_schema.list_schema(),
                    core_schema.no_info_plain_validator_function(all_are_type),
                ]
            ),
            python_schema=core_schema.chain_schema(
                [
                    core_schema.is_instance_schema(np.ndarray),
                    core_schema.no_info_plain_validator_function(all_are_type),
                ],
            ),
            serialization=core_schema.plain_serializer_function_ser_schema(
                lambda instance: instance.tolist()
            ),
        )


class _NumpyNumberAnnotation:
    """
    Pydantic core schema for numpy numbers.
    """

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: GetCoreSchemaHandler
    ) -> CoreSchema:
        return core_schema.json_or_python_schema(
            json_schema=core_schema.is_instance_schema(np.number),
            python_schema=core_schema.is_instance_schema(np.number),
            serialization=core_schema.plain_serializer_function_ser_schema(
                lambda instance: instance
            ),
        )


NumpyNumber = Annotated[np.number, _NumpyNumberAnnotation]


class _H5FileAnnotation:
    """
    Pydantic core schema for h5 files.
    """

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: GetCoreSchemaHandler
    ) -> CoreSchema:
        return core_schema.json_or_python_schema(
            json_schema=core_schema.is_instance_schema(h5py.File),
            python_schema=core_schema.is_instance_schema(h5py.File),
            serialization=core_schema.plain_serializer_function_ser_schema(
                lambda instance: instance
            ),
        )


H5File = Annotated[h5py.File, _H5FileAnnotation]


class _H5GroupAnnotation:
    """
    Pydantic core schema for h5 groups.
    """

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: GetCoreSchemaHandler
    ) -> CoreSchema:
        return core_schema.json_or_python_schema(
            json_schema=core_schema.is_instance_schema(h5py.Group),
            python_schema=core_schema.is_instance_schema(h5py.Group),
            serialization=core_schema.plain_serializer_function_ser_schema(
                lambda instance: instance
            ),
        )


H5Group = Annotated[h5py.Group, _H5GroupAnnotation]
