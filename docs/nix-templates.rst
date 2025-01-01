.. _nix-templates:

Nix Templates
=============

Quickly initialise a new project using `Nix <https://nixos.org/>`_.

Run the following to initialise a project using a template ``<template-name>``:

.. code-block:: bash

    # Or, run " nix flake init -t ..." if experimental features are enabled already
    nix --extra-experimental-features flakes flake init -t github:UWA-Medical-Physics-Research-Group/turtwig#<template-name>


Available Templates
--------------------

+---------------------+-----------------------------------------------------------+
| ``<template-name>`` | Description                                               |
+=====================+===========================================================+
| ``python312``       | Initialise a project with Python 3.12.7, ``uv``, and      |
|                     | ``turtwig`` added in ``pyproject.toml``                   |
+---------------------+-----------------------------------------------------------+

(wow that's a lot of templates)
