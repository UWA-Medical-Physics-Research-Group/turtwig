import os
import sys
from typing import Annotated

import numpy as np
import pytest
from pydantic import AfterValidator, ValidationError, validate_call

dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.realpath(f"{dir_path}/../../../turtwig"))

from turtwig.validation import NumpyArray, is_ndim


class TestIsNdim:

    # Function correctly validates array with specified number of dimensions when ndim is int
    def test_validates_array_with_specified_ndim(self):
        arr = np.array([[1, 2], [3, 4]])
        result = is_ndim(arr, ndim=2)

        assert result is arr

    # Handle 0-dimensional numpy array validation
    def test_validates_zero_dim_array(self):
        arr = np.array(5)  # 0-dimensional array
        result = is_ndim(arr, ndim=0)

        assert result is arr

    def test_validate_using_pydantic(self):
        @validate_call()
        def func(
            arr: Annotated[np.ndarray, NumpyArray, AfterValidator(is_ndim(ndim=3))]
        ):
            return arr

        arr = np.ones((2, 5, 3))
        func(arr)

        with pytest.raises(ValidationError):
            arr = np.ones((2, 5))
            func(arr)

        with pytest.raises(ValidationError):
            arr = np.ones(5)
            func(arr)

    def test_multiple_ndims(self):
        @validate_call()
        def func(
            arr: Annotated[np.ndarray, NumpyArray, AfterValidator(is_ndim(ndim=[2, 5]))]
        ):
            return arr

        arr = np.ones((2, 5))
        func(arr)

        arr = np.ones((2, 5, 3, 4, 5))
        func(arr)

        with pytest.raises(ValidationError):
            arr = np.ones((2, 5, 3))
            func(arr)

        with pytest.raises(ValidationError):
            arr = np.ones(5)
            func(arr)

        with pytest.raises(ValidationError):
            arr = np.ones((2, 5, 3, 4))
            func(arr)
