.. _installation:

Installation
============

Options to install ``turtwig`` as a library.

Nix Template
-------------
To initialise a project with Python 3.12.7 and ``uv`` using the ``python312`` template, run

.. code-block:: bash

    mkdir myproject && cd myproject # optional
    nix flake init -t github:UWA-Medical-Physics-Research-Group/turtwig#python312

Then, depending if you have ``uv`` installed or not... install ``turtwig`` with

.. code-block:: bash
    
    nix develop -c uv sync # uv is not installed
    # 
    uv sync                # uv is installed

See :ref:`nix-templates` for a list of available templates.

.. admonition:: Nix experimental features not enabled?
    :class: tip
    
    If you haven't enabled the experimental features, run below instead of ``nix develop -c uv sync``:
    
    .. code-block:: bash
    
        nix --extra-experimental-features nix-command --extra-experimental-features flakes develop -c uv sync


``uv``
------
Ensure that you've run ``uv init`` or that a ``pyproject.toml`` file exists in the current directory. Then, run

.. code-block:: bash

    uv add "turtwig @ git+https://github.com/UWA-Medical-Physics-Research-Group/turtwig"



``pip``
-------
To install the package with ``pip``, run

.. code-block:: bash

    pip install https://github.com/UWA-Medical-Physics-Research-Group/turtwig/releases/latest/download/turtwig-0.1.0-py3-none-any.whl"
