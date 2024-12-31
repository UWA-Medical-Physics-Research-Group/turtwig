.. _tutorials:

Tutorials
=========

Tutorials and usage examples using functions from ``turtwig``.

Working with DICOM Files
------------------------
`DICOM <https://www.dicomstandard.org/>`_ is the standard dataset 
for medical imaging. Unfortunately, working with DICOM files sucks. 
Fortunately, most of the (tedious) work have been done. Functions
from :ref:`turtwig-api.data` will load DICOM files, flip
the arrays to the correct orientation, make the spacings isotropic,
and convert the pixel values to Hounsfield Units (HU) for CT scans.

Ensure you have a folder of ``.dcm`` files, OR a folder of these folders
for the example below.


.. code-block:: python

    from turtwig.data import load_patient_scan, load_all_patient_scans, load_roi_names

    dicom_dir = "path/to/dicom/folder"  # contains .dcm files
    scan = load_patient_scan(dicom_dir) # load a single scan

    print(scan.keys())   # dict_keys(['patient_id', 'volume', 'masks', ...])
    print(scan['volume'].shape)  # (512, 512, 250)
    # masks are loaded as a dictionary
    print(scan['masks'].keys())  # dict_keys(['organ1', 'organ1_observerX', ...])

    dicom_collection_dir = "path/to/dicom/collection/folder"  # contains folders of dicom folders
    scans = load_all_patient_scans(dicom_collection_dir)  # load all scans, scans is an iterator
    print(next(scans)['patient_id'])  # "Patient0"

    names = load_roi_names(dicom_collection_dir)  # load the names of the masks
    print(next(names)) # ['organ1', 'organ1_observerX', ...]


.. admonition:: More on the DICOM Format
    :class: info

    DICOM files are read with ``pydicom`` and a DICOM dataset has several 
    attributes which you can search `here <https://dicom.innolitics.com/ciods#>`_.
    Some attributes of interest include:
    
        - ``SOPClassUID``: identifies the type of DICOM file, e.g. whether it is a CT image, 
          a RT structure set (defining various contours to extract masks from), a RT dose file, 
          or a RT plan
        - ``pixel_array``: the actual image data, *often* in the `LPS orientation <https://www.slicer.org/wiki/Coordinate_systems>`_
        - ``Modality``: Imaging modality, e.g. CT, MR

.. admonition:: TIP: Saving Your Data to HDF5 Format
    :class: tip

    As opposed to saving the loaded DICOM dictionaries as pickle files,
    it's better to save them in the `HDF5 <https://www.hdfgroup.org/solutions/hdf5/>`_ 
    format which offers better compression and extremely faster read/write
    speeds. For example,

    .. code-block:: python

        from turtwig.data import load_all_patient_scans, dict_to_h5
        import h5py

        scans = load_all_patient_scans("path/to/dicom/collection/folder")
        dict_to_h5(scans, "path/to/save/hdf5/file.h5")

        with h5py.File("path/to/save/hdf5/file.h5", "r") as f:
            print(f.keys())  # ['Patient0', 'Patient1', ...]
            print(f['Patient0'].keys())  # ['volume', 'masks', ...]


Validating Function Arguments
-----------------------------

Decorate a function with ``@pydantic.validate_call`` to check the type of the 
input arguments to a function.

To use classes and validation functions from :ref:`turtwig-api.validation`,
annotate specific parameters using ``typing.Annotated``.

.. code-block:: python

    from pydantic import validate_call, AfterValidator
    from typing import Annotated
    import numpy as np
    from turtwig.validation import is_ndim, NumpyArrayAnnotation

    # Check that 'a' is 1) a numpy array, 2) have 3 dimensions
    # Note that np.ndarray is not supported by pydantic, so we need NumpyArrayAnnotation
    @validate_call()
    def test(
        a: Annotated[np.ndarray, NumpyArrayAnnotation, AfterValidator(is_ndim(ndim=3))],
        b: int
    ) -> np.ndarray:
        return a, b

    test(np.zeros((10, 10, 10)), 6)  # Passes
    test(np.zeros((10, 10)), 6)  # Raises ValidationError: Parameter 'a' must have 3 dimensions
    test([4], 6)  # Raises ValidationError: Parameter 'a' must be of type 'numpy.ndarray'
    test(np.zeros((10, 10, 10)), "6")  # Raises ValidationError: Parameter 'b' must be of type 'int'