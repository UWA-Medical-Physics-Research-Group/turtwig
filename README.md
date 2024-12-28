# turtwig
Utility library and starter code for medical data analysis

## Content (TODO)

## Install
You can either 
1. install `turtwig` as a library for use in your own project, OR 
2. install only the project dependencies if you are developing the library

<details>
<summary>Install as a Library (TODO)</summary>
### Install as a Library (TODO)

- installing as library package
    - install via `uv`
    - `pip install`
    - `conda`/`mamba`
</details>

<details>
<summary>Installing Project Dependencies</summary>
### Installing Project Dependencies

- Install project dependencies via **one** of the options below...
    - [uv](https://docs.astral.sh/uv/) - fast Python dependency manager
    - [Nix](https://nixos.org/) - reproducible development shell

Instructions below assumes you are at the **top-level of the project directory** (i.e. folder containing `pyproject.toml` etc).

#### uv
[uv](https://docs.astral.sh/uv/) manages and configures Python dependencies. First install it following the [installation guide](https://docs.astral.sh/uv/getting-started/installation/). Then, any Python commands can be run by appending `uv run` in front of your command which will automatically download project dependencies, e.g.

```bash
uv run python # equivalent to just running `python`
```

#### Nix
**Warning: CUDA may not work due to the isolated nature of Nix shells!**

[Nix](https://nixos.org/) is a purely functional programming language *and* package manager used to create isolated and reproducible development shells. A `flake.nix` file defines project dependencies and environment which activates the shell defined in `shell.nix`. First, install Nix following the [installation guide](https://nixos.org/download/). Then, start a development shell by running...

```bash
# Enable experimental features `nix-command` and `flakes`, then run the `develop` command
# Or if you've already enabled these features, just run `nix develop`
nix --extra-experimental-features nix-command --extra-experimental-features flakes develop
# you can now run `uv run python ...` etc
```


<details>
<summary>Auto-activation with Direnv (Optional)</summary>
##### Auto-activation with Direnv (Optional)

**Warning: `direnv` allow the execution of any arbitrary bash code in `.envrc`, please examine `.envrc` before you proceed!**

[`direnv`](https://direnv.net/) is used to automatically activate the Nix flake when you enter into the folder containing this repository. First, install it via the [official installation guide](https://direnv.net/docs/installation.html) and [hook it into your shell](https://direnv.net/docs/hook.html) (HINT: run `echo $SHELL` to see what shell you are using). Then, inside the project directory where `.envrc` is in the same folder, run...

```bash
direnv allow  # allow execution of .envrc automatically
direnv disallow # stop automatically executing .envrc upon entering the project folder
```
</details>
</details>


### Tutorials (move to wiki)
Many parts of the code is written roughly in the **functional programming** paradigm. 

#### Pipe

Given a value `x`, `toolz.pipe` just passes `x` through a series of functions (it's just a for-loop...).

```python
import toolz as tz
from toolz import curried

# Below is equivalent to
# str(curried.get(5)(tz.identity([3, 4] * 4)))

do_nothing = True
tz.pipe(
    [3, 4],   # value
    lambda lst: lst * 4,
    tz.identity if do_nothing else tz.concat,   # tz.identity will be called here
    curried.get(5),  # get(5) is still a FUNCTION, see "curry" below
    str,
)   # OUTPUT: '4'
```

#### Curry

Yummy.

A function can by "curried" if it's decorated with `@curry`. A "curried" function can be called with *only some of the required arguments* (i.e. partially initialised). This is a **new function** that can be called with the remaining arguments.

```python
from uncertainty.utils import curry  # wrapper around toolz.curry

@curry
def add(a, b, c=3):
    return a + b + c

# If some positional arguments are not provided, a function is returned instead
# of raising an error
add_5 = add(5)  # equivalent to lambda b: 5 + b + 3
# We can call this function with the remaining argument
add_5(3) # 11
# You can also just use the function normally
add(5, 3)  # 11
# will also return a function because only one positional argument is provided
add(5, c=6)  # equivalent to lambda b: 5 + b + 6
```
#### Validation
- if function is curried, `@curry` MUST be the last decorator else validators will run and fail and :(



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
- test cases

- logging... by default, log using loguru to stderr instead of print?

- set up github pages for wiki, generate documents using `pdoc`
    - example usage/tutorials for each module
