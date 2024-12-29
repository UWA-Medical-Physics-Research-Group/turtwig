import os
import sys
from typing import Annotated

import numpy as np
import pytest
from pydantic import ValidationError, validate_call

dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.realpath(f"{dir_path}/../../../turtwig"))

from turtwig.validation import NumpyArray


class TestNumpyArray:

    # Validate numpy array with no type constraints
    def test_validate_untyped_array(self):

        @validate_call()
        def func(arr: Annotated[np.ndarray, NumpyArray]) -> np.ndarray:
            return arr

        func(np.array([1, "a", 3.14]))
        func(np.array(5))
        func(np.array([]))
        func(np.array([True, False, True]))

    # Validate array with incorrect element types
    def test_validate_typed_array_with_wrong_type(self):

        @validate_call()
        def func(arr: Annotated[np.ndarray, NumpyArray[np.int64]]):
            return arr

        with pytest.raises(ValidationError):
            func(np.array([1, "a", 3.14]))
        with pytest.raises(ValidationError):
            func(np.array([True, False, True]))

    def test_union_type(self):

        @validate_call()
        def func(arr: Annotated[np.ndarray, NumpyArray[np.int64 | np.bool]]):
            return arr

        func(np.array([1, 2, 3]))
        func(np.array([True, False, True]))
        func(np.array([1, 2, True]))
        with pytest.raises(ValidationError):
            func(np.array([1, "a", 3.14]))
        with pytest.raises(ValidationError):
            func(np.array([1, 2, 3.14]))
