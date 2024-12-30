import os
import sys

import numpy as np

dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.realpath(f"{dir_path}/../../../turtwig"))

from turtwig.data import bounding_box3d, make_isotropic, map_interval


class TestMapInterval:
    # correctly maps values from one range to another
    def test_correctly_maps_values_from_one_range_to_another(self):
        from_range = (0, 10)
        to_range = (0, 100)
        array = np.array([0, 5, 10])
        expected = np.array([0.0, 50.0, 100.0])

        result = map_interval(array, from_range, to_range)
        np.testing.assert_array_almost_equal(result, expected)

    # handles empty arrays
    def test_handles_empty_arrays(self):
        from_range = (0, 10)
        to_range = (0, 100)
        array = np.array([])
        expected = np.array([])

        result = map_interval(array, from_range, to_range)
        np.testing.assert_array_equal(result, expected)

    # handles negative integer ranges
    def test_handles_negative_integer_ranges(self):
        from_range = (-10, 10)
        to_range = (0, 100)
        array = np.array([-10, 0, 10])
        expected = np.array([0.0, 50.0, 100.0])

        result = map_interval(array, from_range, to_range)
        np.testing.assert_array_almost_equal(result, expected)

    # handles floating point ranges
    def test_handles_floating_point_ranges(self):
        from_range = (0.0, 1.0)
        to_range = (0.0, 100.0)
        array = np.array([0.0, 0.5, 1.0])
        expected = np.array([0.0, 50.0, 100.0])

        result = map_interval(array, from_range, to_range)
        np.testing.assert_array_almost_equal(result, expected)

    # processes multi-dimensional arrays correctly
    def test_processes_multi_dimensional_arrays_correctly(self):
        from_range = (0, 10)
        to_range = (0, 100)
        array = np.array([[0, 5, 10], [1, 6, 11]])
        expected = np.array([[0.0, 50.0, 100.0], [10.0, 60.0, 110.0]])

        result = map_interval(array, from_range, to_range)
        np.testing.assert_array_almost_equal(result, expected)

    # handles arrays with a single element
    def test_handles_single_element_array(self):
        from_range = (0, 10)
        to_range = (0, 100)
        array = np.array([5])
        expected = np.array([50.0])

        result = map_interval(array, from_range, to_range)
        np.testing.assert_array_almost_equal(result, expected)

    # handles arrays with all elements the same
    def test_handles_arrays_with_all_elements_the_same(self):
        from_range = (0, 10)
        to_range = (0, 100)
        array = np.array([5, 5, 5])
        expected = np.array([50.0, 50.0, 50.0])

        result = map_interval(array, from_range, to_range)
        np.testing.assert_array_almost_equal(result, expected)


class TestMakeIsotropic:
    # Interpolates a 2D array with given spacings to an isotropic grid with 1 unit spacing
    def test_interpolates_2d_array_to_isotropic_grid(self, mocker):
        import numpy as np

        # Define input array and spacings
        array = np.array([[1.0, 2.0], [3.0, 4.0]])
        spacings = [2, 2]

        # Expected output after interpolation

        expected_output = np.array(
            [
                [1.0, 1.5, 2.0, 0.0],
                [2.0, 2.5, 3.0, 0.0],
                [3.0, 3.5, 4.0, 0.0],
                [0.0, 0.0, 0.0, 0.0],
            ]
        )

        # Call the function
        result = make_isotropic(array, spacings)

        # Assert the result is as expected
        np.testing.assert_array_almost_equal(result, expected_output)
        assert result.dtype == array.dtype

    def test_interpolates_integer_array(self, mocker):
        import numpy as np

        # Define input array and spacings
        array = np.array([[1, 2], [3, 4]])
        spacings = [2, 2]

        # Expected output after interpolation

        expected_output = np.array(
            [
                [1, 1, 2, 0.0],
                [2, 2, 3, 0.0],
                [3, 3, 4, 0.0],
                [0, 0, 0, 0],
            ]
        )

        # Call the function
        result = make_isotropic(array, spacings)

        # Assert the result is as expected
        np.testing.assert_array_almost_equal(result, expected_output)

        assert result.dtype == array.dtype


class TestBoundingBox3d:

    # Function correctly computes bounding box coordinates for a 3D binary array with clear boundaries
    def test_bounding_box_computation(self):
        # Create a 3D binary array with clear boundaries
        img = np.zeros((10, 10, 10))
        img[2:5, 3:7, 4:8] = 1

        # Call the function
        rmin, rmax, cmin, cmax, zmin, zmax = bounding_box3d(img)

        # Assert the correct bounding box coordinates
        assert rmin == 2
        assert rmax == 4
        assert cmin == 3
        assert cmax == 6
        assert zmin == 4
        assert zmax == 7

    def test_bounding_box_oval_volume(self):
        def generate_binary_3d_oval_with_bbox(
            volume_shape=(100, 100, 100), center=(50, 50, 50), radii=(30, 20, 10)
        ):
            z, y, x = np.indices(volume_shape)
            # Normalized distances for the ellipsoid
            normalized_distances = (
                ((x - center[0]) / radii[0]) ** 2
                + ((y - center[1]) / radii[1]) ** 2
                + ((z - center[2]) / radii[2]) ** 2
            )
            binary_volume = (normalized_distances <= 1).astype(np.uint8)
            # Compute bounding box: find the min/max indices where binary volume is 1
            non_zero_indices = np.argwhere(binary_volume)
            min_z, min_y, min_x = non_zero_indices.min(axis=0)
            max_z, max_y, max_x = non_zero_indices.max(axis=0)

            bounding_box = ((min_z, min_y, min_x), (max_z, max_y, max_x))

            return binary_volume, bounding_box

        # Generate binary 3D oval and bounding box
        volume_shape = (100, 100, 100)
        center = (50, 50, 50)
        radii = (30, 20, 10)

        binary_oval, bbox = generate_binary_3d_oval_with_bbox(
            volume_shape, center, radii
        )
        rmin, cmin, zmin = bbox[0]
        rmax, cmax, zmax = bbox[1]

        # Call the function
        rmin_, rmax_, cmin_, cmax_, zmin_, zmax_ = bounding_box3d(binary_oval)

        # Assert the correct bounding box coordinates
        assert rmin == rmin_
        assert rmax == rmax_
        assert cmin == cmin_
        assert cmax == cmax_
        assert zmin == zmin_
        assert zmax == zmax_
