# turtwig
Utility library and starter code for medical data analysis. See documentations [here](https://uwa-medical-physics-research-group.github.io/turtwig/).


## Installation

### `uv`
Ensure that you’ve run `uv init` or that a `pyproject.toml` file exists in the current directory. Then, run

```bash
uv add "turtwig @ git+https://github.com/UWA-Medical-Physics-Research-Group/turtwig/releases/latest/download/turtwig-0.1.0-py3-none-any.whl"
```

### `pip`
To install the package with pip, run

```bash
pip install https://github.com/UWA-Medical-Physics-Research-Group/turtwig/releases/latest/download/turtwig-0.1.0-py3-none-any.whl
```


### Nix Templates
You can quickly initialise a new project using the available templates if you have installed [Nix](https://nixos.org/). Run the command

```bash
# Or, run " nix flake init -t ..." if experimental features are enabled already
nix --extra-experimental-features flakes flake init -t github:UWA-Medical-Physics-Research-Group/turtwig#<template-name>
```

| `<template-name>` | Description |
| --- | --- |
| `python312` | Initialise a project with Python 3.12.7, uv, and `turtwig` installed |

(wow that's a lot of templates)
