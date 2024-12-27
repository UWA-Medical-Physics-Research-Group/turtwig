## Getting Started
- Install project dependencies via **one** of the options below...
    - [uv](https://docs.astral.sh/uv/) - fast Python dependency manager
    - [Nix](https://nixos.org/) - reproducible development shell

Instructions below assumes you are at the **top-level of the project directory** (i.e. folder containing `pyproject.toml` etc).

### uv
[uv](https://docs.astral.sh/uv/) manages and configures Python dependencies. First install it following the [installation guide](https://docs.astral.sh/uv/getting-started/installation/). Then, any Python commands can be run by appending `uv run` in front of your command which will automatically download project dependencies, e.g.

```bash
uv run python # equivalent to just running `python`
```

### Nix
**Warning: CUDA may not work due to the isolated nature of Nix shells!**

[Nix](https://nixos.org/) is a purely functional programming language *and* package manager used to create isolated and reproducible development shells. A `flake.nix` file defines project dependencies and environment which activates the shell defined in `shell.nix`. First, install Nix following the [installation guide](https://nixos.org/download/). Then, start a development shell by running...

```bash
# Enable experimental features `nix-command` and `flakes`, then run the `develop` command
# Or if you've already enabled these features, just run `nix develop`
nix --extra-experimental-features nix-command --extra-experimental-features flakes develop
# you can now run `uv run python ...` etc
```


#### Auto-activation with Direnv (Optional)

**Warning: `direnv` allow the execution of any arbitrary bash code in `.envrc`, please examine `.envrc` before you proceed!**

[`direnv`](https://direnv.net/) is used to automatically activate the Nix flake when you enter into the folder containing this repository. First, install it via the [official installation guide](https://direnv.net/docs/installation.html) and [hook it into your shell](https://direnv.net/docs/hook.html) (HINT: run `echo $SHELL` to see what shell you are using). Then, inside the project directory where `.envrc` is in the same folder, run...

```bash
direnv allow  # allow execution of .envrc automatically
direnv disallow # stop automatically executing .envrc upon entering the project folder
```
