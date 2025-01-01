"""
Datatype definitions for validation.
"""

from datetime import date
from typing import Annotated, Any, Iterator, TypedDict, get_args, get_origin

import h5py
import numpy as np
from pydantic import GetCoreSchemaHandler
from pydantic_core import CoreSchema, core_schema

MaskDict = dict[Annotated[str, "organ name"], np.ndarray]


class DicomDict(TypedDict):
    """
    A dictionary containing information about a DICOM scan.
    """

    patient_id: int
    """Patient ID."""
    volume: np.ndarray
    """DICOM volume."""
    dimension_original: tuple[int, int, int]
    """Original dimensions of the volume at the time of loading the .dcm files."""
    spacings: tuple[float, float, float]
    """Original spacings of the volume at the time of loading the .dcm files."""
    modality: str
    """Modality of the scan, e.g. CT, MR."""
    manufacturer: str
    """Manufacturer of the scanner."""
    scanner: str
    """Scanner model name."""
    study_date: date
    """Date of the scan."""
    masks: np.ndarray | MaskDict
    """Masks for the volume; either a single numpy array with channels for each organ, or a dictionary with the organ names as keys and the masks as values."""
    organ_ordering: list[str]
    """Order of the organs in the masks."""


class NumpyArrayAnnotation:
    """
    Pydantic core schema for numpy arrays.

    You can either annotate using ``Annotation[np.ndarray, NumpyArrayAnnotation]``
    for a numpy array of any type, or ``Annotated[np.ndarray, NumpyArrayAnnotation[type]]``
    for a numpy array of a specific type.

    Examples
    --------
    >>> import numpy as np
    >>> from pydantic import validate_call
    >>> from typing import Annotated
    >>> @validate_call()
    ... def test(
    ...     a: Annotated[np.ndarray, NumpyArrayAnnotation],
    ...     b: Annotated[np.ndarray, NumpyArrayAnnotation[np.int64]],
    ...     c: Annotated[np.ndarray, NumpyArrayAnnotation[np.bool | np.int64]]
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
        Dynamically create a subclass of NumpyArrayAnnotation with the specified type.
        """

        class TypedNumpyArrayAnnotation(cls):
            # If type is annotated, get first argument (i.e. the wrapped type)
            type__: type | None = (
                type_ if not get_origin(type_) is Annotated else get_args(type_)[0]
            )

        TypedNumpyArrayAnnotation.__name__ = f"TypedNumpyArrayAnnotation[{type_}]"
        return TypedNumpyArrayAnnotation

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

    Examples
    --------
    >>> import numpy as np
    >>> from pydantic import validate_call
    >>> from typing import Annotated
    >>> from turtwig.validation import NumpyArrayAnnotation
    >>> @validate_call()
    ... def test(
    ...     a: Annotated[np.ndarray, NumpyArrayAnnotation[NumpyNumber]]
    ... ):
    ...     return a
    >>> test(np.array([1, 2, 3]))  # no error
    array([1, 2, 3])
    >>> test(np.array([1, 2, 3.0]))  # no error
    array([1., 2., 3.])
    >>> test(np.array([1, 2, '3']))  # error
    >>> test(np.array([True, 2, 3]))  # error
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
NumpyNumber.__doc__ = """
Pydantic schema for numpy numbers.

Examples
--------
>>> import numpy as np
>>> from pydantic import validate_call
>>> from typing import Annotated
>>> from turtwig.validation import NumpyArrayAnnotation
>>> @validate_call()
... def test(
...     a: Annotated[np.ndarray, NumpyArrayAnnotation[NumpyNumber]]
... ):
...     return a
>>> test(np.array([1, 2, 3]))  # no error
array([1, 2, 3])
>>> test(np.array([1, 2, 3.0]))  # no error
array([1., 2., 3.])
>>> test(np.array([1, 2, '3']))  # error
>>> test(np.array([True, 2, 3]))  # error
"""


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
H5File.__doc__ = """
Pydantic schema for h5 files.

Examples
--------
>>> import h5py
>>> from pydantic import validate_call
>>> from typing import Annotated
>>> @validate_call()
... def test(f: H5File):
...     return f
...
>>> with h5py.File('test.h5', 'w') as f:
...     test(f)  # no error
...
>>> test('test.h5')  # error
"""


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
H5Group.__doc__ = """
Pydantic schema for h5 groups. See ``turtwig.validation.H5File`` for examples.
"""


class IteratorAnnotation:
    """
    Pydantic core schema for iterators.

    Examples
    --------
    >>> from pydantic import validate_call
    >>> from typing import Annotated, Iterator
    >>> @validate_call()
    ... def test(
    ...     a: Annotated[Iterator, IteratorAnnotation]
    ... ):
    ...     return a
    >>> test(iter([1, 2, 3]))  # no error
    <list_iterator object at 0x7f7f3c7b5d00>
    >>> test([1, 2, 3])  # error
    """

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: GetCoreSchemaHandler
    ) -> CoreSchema:
        return core_schema.json_or_python_schema(
            json_schema=core_schema.is_instance_schema(Iterator),
            python_schema=core_schema.is_instance_schema(Iterator),
            serialization=core_schema.plain_serializer_function_ser_schema(
                lambda instance: list(instance)
            ),
        )
