# turtwig
Utility library and starter code for medical data analysis. See documentations [here](https://uwa-medical-physics-research-group.github.io/turtwig/).


## Installation

Install via **one** of the options below

### `uv`
Ensure that you’ve run `uv init` or that a `pyproject.toml` file exists in the current directory. Then, run

```bash
uv add "turtwig @ git+https://github.com/UWA-Medical-Physics-Research-Group/turtwig"
```

### `pip`
To install the package with pip, run

```bash
pip install https://github.com/UWA-Medical-Physics-Research-Group/turtwig/releases/latest/download/turtwig-0.1.0-py3-none-any.whl
```


### Nix Templates
You can quickly initialise a new Python 3.12.7 project if you have installed [Nix](https://nixos.org/). Initialise a folder for your project, `cd` into it and run

```bash
# If experimental features are enabled
nix flake init -t git+https://github.com/UWA-Medical-Physics-Research-Group/turtwig.git#python312

# if experimental features are NOT enabled
nix --extra-experimental-features flakes flake init -t git+https://github.com/UWA-Medical-Physics-Research-Group/turtwig.git#python312
```

Then, run **one** of the commands below to install `turtwig`

```bash
# remember to add --extra-experimental-features flags if they are not enabled
nix develop -c uv sync  # use if uv is NOT installed, OR you want to use nix still
uv sync   # use if uv IS installed
```

See the list of templates [here](file:///home/tin/Documents/UWA/turtwig/docs/_build/html/nix-templates.html).