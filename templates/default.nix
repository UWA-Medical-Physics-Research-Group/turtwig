# Initialise with
#   nix flake init -t github:UWA-Medical-Physics-Research-Group/turtwig#<template-name>
# files at `path` are copied when initialising flake
{
  python312 = {
    path = ./python312;
    description = "Initialise a Python 3.12.7 project using uv as the dependency manager";
    welcomeText = ''
      # Python 3.12.7 Project + uv

      ## Installing dependencies
      Install project dependencies via **one** of these options:
      ### 1. Using `uv`
      ```bash
      uv sync
      ```
      ### 2. Using `Nix`
      If you haven't enabled the experimental features, run:
      ```bash
      nix --extra-experimental-features nix-command --extra-experimental-features flakes develop
      ```
      Else, just run
      ```bash
      nix develop
      ```

      ## Activate Shell Automatically with `direnv`
      To automatically activate a Nix flake shell when you enter the project directory, install `direnv` and hook it into your shell. Then, run
      ```bash
      direnv allow
      ```

      ## More info
      - [uv](https://docs.astral.sh/uv/)
      - [Nix](https://nixos.org/)
      - [direnv](https://direnv.net/)
      - [Hooking direnv into your shell](https://direnv.net/docs/hook.html)
    '';
  };
}
