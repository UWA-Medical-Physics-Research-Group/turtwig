import tempfile
from datetime import date

import h5py
import numpy as np

import os
import sys

dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.realpath(f"{dir_path}/../../../turtwig"))

from turtwig.data import dict_to_h5, dict_from_h5


dataset = { "0":
    {
        "patient_id": 5,
        "volume": np.zeros((10, 10, 10)),
        "dimension_original": (10, 10, 10),
        "spacings": (1.0, 1.0, 1.0),
        "modality": "CT",
        "manufacturer": "GE",
        "scanner": "Optima",
        "study_date": date(2021, 1, 1),
        "masks": {
            "organ1": np.ones((10, 10, 10)),
            "organ2": np.zeros((10, 10, 10)),
        },
    },
    "1": {
        "patient_id": 6,
        "volume": np.ones((10, 10, 10)),
        "dimension_original": (10, 10, 10),
        "spacings": (1.0, 1.0, 1.0),
        "modality": "CT",
        "manufacturer": "GE",
        "scanner": "Optima",
        "study_date": date(2021, 1, 1),
        "masks": {
            "organ1": np.zeros((10, 10, 10)),
            "organ2": np.ones((10, 10, 10)),
        },
    },
}


class TestDictToH5:
    def test_create_group_with_different_datatypes(self, tmp_path):
        test_path = tmp_path / "test.h5"
        dataset2 = {
            "patient_id": 5,
            "volume": np.zeros((10, 10, 10)),
            "spacings": (1.0, 1.0, 1.0),
            "modality": "CT",
            "study_date": date(2021, 1, 1),
            "masks": {
                "organ1": np.ones((10, 10, 10)),
                "organ2": np.zeros((10, 10, 10)),
                "list": [
                    np.array([1, 2, 3]),
                    np.array([1.0, 2.0, 3.0]),
                ],
            },
            "list": [1, 2, 3],
            "list2": [
                np.array([1, 2, 3]),
                np.array([1.0, 2.0, 3.0]),
            ],
        }

        with h5py.File(test_path, "w") as f:
            group = f.create_group("test_group")
            dict_to_h5(dataset2, group)
            
            assert "test_group" in f
            assert f["test_group"]["patient_id"][()] == 5  # type: ignore
            assert np.array_equal(f["test_group"]["volume"][()], np.zeros((10, 10, 10)))  # type: ignore
            assert f["test_group"]["spacings"][()].tolist() == [1.0, 1.0, 1.0]  # type: ignore
            assert f["test_group"]["modality"][()].decode() == "CT"  # type: ignore
            assert f["test_group"]["study_date"][()].decode() == "2021-01-01"  # type: ignore
            assert np.array_equal(f["test_group"]["masks/organ1"][()], np.ones((10, 10, 10)))  # type: ignore
            assert np.array_equal(f["test_group"]["masks/organ2"][()], np.zeros((10, 10, 10)))  # type: ignore
            assert np.array_equal(f["test_group"]["masks/list"][()], np.array([[1.0, 2.0, 3.0] for _ in range(2)]))  # type: ignore
            assert np.array_equal(f["test_group"]["list"][()], np.array([1, 2, 3]))  # type: ignore
            assert np.array_equal(f["test_group"]["list2"][()], np.array([[1.0, 2.0, 3.0] for _ in range(2)]))  # type: ignore


    # Successfully saves single dictionary with all fields to H5 file
    def test_save_dict(self):
        with tempfile.NamedTemporaryFile() as tmp:
            test_path = tmp.name

            dict_to_h5(dataset, test_path)

            # Verify file exists and contents
            assert os.path.exists(test_path)

            with h5py.File(test_path, "r") as f:
                for i in range(2):
                    patient = f[str(i)]
                    assert patient["patient_id"][()] == dataset[str(i)]["patient_id"]  # type: ignore
                    assert np.array_equal(patient["volume"][()], dataset[str(i)]["volume"])  # type: ignore
                    assert patient["modality"][()].decode() == "CT"  # type: ignore
                    assert np.array_equal(patient["masks/organ1"][()], dataset[str(i)]["masks"]["organ1"])  # type: ignore


class TestDictFromH5:

    # Successfully loads dict with all fields from H5 file
    def test_load_dataset(self):
        with tempfile.NamedTemporaryFile() as tmp:
            test_path = tmp.name
            
            dict_to_h5(dataset, test_path)
            loaded = dict_from_h5(test_path)

            assert len(loaded.keys()) == 2

            for i, data in loaded.items():
                assert data["patient_id"] == dataset[i]["patient_id"]
                assert np.array_equal(data["volume"], dataset[i]["volume"])
                assert data["modality"] == "CT"
                assert data["masks"]["organ1"].shape == (10, 10, 10)
                assert np.array_equal(
                    data["masks"]["organ1"], dataset[i]["masks"]["organ1"]
                )
                assert np.array_equal(
                    data["masks"]["organ2"], dataset[i]["masks"]["organ2"]
                )
                assert data["study_date"] == "2021-01-01"
                assert data["dimension_original"].tolist() == [10, 10, 10]
                assert data["spacings"].tolist() == [1.0, 1.0, 1.0]
                assert data["manufacturer"] == "GE"
                assert data["scanner"] == "Optima"

