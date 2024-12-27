# turtwig
Utility library and starter code for medical data analysis



# TODOS:
- `turtwig.logging` - add logging to project
- `turtwig.config` - read and configure functions via a configuration file
- `turtwig.validation` - validation decorators, e.g. array shape
- `turtwig.models` - preset models
- `turtwig.functils` - functional utilities
- `turtwig.metrics`
    - `classification`
    - `loss`
    - `uncertainty` + `risk`
- `turtwig.data`
    - `dicom`
    - `nifti` - maybe idk
    - `h5`
    - `_datatypes`
- `turtwig.array`
  - `processing` - functions for generic arrays, e.g. make arrays isotropic
  - sliding window - `extract_patches()`, `stitch_patches()`
  - `augmentation`
  
- `turtwig.learning`
    - `models`
    - `datasets`
    - `checkpoint` - set up checkpoint directory

- set up
    - via Nix shell + starter template via `nix template`
    - set up via `pip` and `uv`, optionally conda?
- set up github pages for wiki, generate documents using `pdoc`
    - example usage/tutorials for each module
- test cases

- logging... by default, log using loguru to stderr instead of print?
- +wiki documentaiton of APIs
