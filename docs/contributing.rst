Contributing
============

Below list several concepts and details to help you read and contribute to the project.

Installing Project Dependencies
-------------------------------
You can install the project dependencies via *one* of the options below:

1. Installing via `uv <https://docs.astral.sh/uv/>`_
####################################################

`uv <https://docs.astral.sh/uv/>`_ manages and configures Python dependencies. 
Install it following the `installation guide <https://docs.astral.sh/uv/getting-started/installation/>`_
and append ``uv run`` in front of any Python commands which will automatically sync the dependencies.

.. code-block:: bash

    uv run python  # Will automatically sync dependencies and run python
    uv sync        # Or, sync the dependencies manually

2. Installing via `Nix <https://nixos.org/>`_
#############################################
`Nix <https://nixos.org/>`_ refers to both the functional programming language *and*
the package manager to create isolated, reproducible development shells. A ``flake.nix``
file defines project dependencies and is used to create a development shell. Install Nix
following the `Nix installation guide <https://nixos.org/download/>`_. Then, start a 
development shell with the command

.. code-block:: bash

    # Enable experimental features `nix-command` and `flakes`, then run `develop`
    # Or if already enabled, just run `nix develop`
    nix --extra-experimental-features nix-command --extra-experimental-features flakes develop
    # you can now run `uv run python ...` etc


.. admonition:: (Optional) Activate Shell Automatically with `direnv <https://direnv.net/>`_
    :class: tip
    
    `direnv <https://direnv.net/>`_ is used to automatically activate a Nix flake
    shell when you enter into the project directory. Install it following the
    `direnv installation guide <https://direnv.net/docs/installation.html>`_ and `hook
    direnv into your shell <https://direnv.net/docs/hook.html>`_ (HINT: run ``echo $SHELL``
    to determine your shell). Then, run

    .. code-block:: bash

        direnv allow   # Allow the .envrc file to be executed automatically
        direnv disallow  # stop automatically executing .envrc upon entering the directory
    
    .. warning::

        Direnv allow the execution of arbitrary code in the .envrc file. Please examine `.envrc` before enabling it!

3. Installing via `pip <https://pip.pypa.io/en/stable/>`_ (``venv``)
#####################################################################
First, create and activate a virtual environment, then install the dependencies with pip:

.. code-block:: bash
    
    pip -m venv .venv   # Create a virtual environment
    source .venv/bin/activate  # Activate the environment on linux (see online documentation for other systems)
    pip install -r ./requirements.txt


Testing
-------

Run the tests with the command

.. code-block:: bash

    uv run pytest

To create a new test file, create a file with the name ``test_<module_name>.py`` in the ``tests`` directory.
A template for a test file is shown below:

.. code-block:: python

    import os
    import sys

    # Add the project directory to the path so that the module can be imported
    dir_path = os.path.dirname(os.path.realpath(__file__))
    sys.path.append(os.path.realpath(f"{dir_path}/../../../turtwig"))

    from turtwig import some_function


    class TestSomeFunction:
    
        # MUST start with 'test_'
        def test_it_does_something_cool(self):
            # 1. initialise some test input
            # 2. call some_function with the test input
            # 3. assert the output is as expected
            # 4. ???
            # 5. profit


Validating Function Arguments
-----------------------------

Decorate a function with ``@pydantic.validate_call`` to validate its input arguments. 
To add a custom validation function ``my_validator``` to specific argument, annotate 
it with ``typing.Annotated[..., pydantic.AfterValidator(my_validator)]``.

>>> from pydantic import validate_call, AfterValidator
>>> from typing import Annotated
>>> 
>>> def my_validator(value):
...     """ Ensure that value is positive """
...     if value < 0:
...         raise ValueError("Value must be positive")
...     return value
... 
>>> @validate_call()
... def add(
...     a: Annotated[float, AfterValidator(my_validator)], 
...     b: int
... ) -> float:
...     return a + b
...
>>> add(0.5, 3)
3.5
>>> add(-0.5, 3) # ValueError: Value must be positive
>>> add(4, 3) # ValidationError: Parameter 'a' must be of type 'float'

.. tip::

    See `Pydantic Functional Validators <https://docs.pydantic.dev/latest/api/functional_validators/>`_ for other validators like ``AfterValidator``.

.. admonition:: Curried Validation Functions
    :class: warning

    A curried validation function must list all arguments apart from
    the input data as strictly keyword-only for curry to work. I.e. the 
    function signature must have the form ``my_validator(value, *, kwarg1, kwarg2, ...)``.


Functional Programming Concepts
-------------------------------
Many parts of the project are written roughly in the **functional programming** paradigm. Various
concepts related to this paradigm are listed below.

Pipe
####
``toolz.pipe`` is used extensively throughout the codebase. Given a value ``x`` and a list of functions, a pipe applies each function to the value. For example,
``pipe(x, f, g, h)`` is equivalent to ``h(g(f(x)))``.

>>> from toolz import pipe, identity, concat, curried
>>> 
>>> do_nothing = True
>>> pipe(
...     [3, 4],   # value to be passed along
...     lambda lst: lst * 4,
...     identity if do_nothing else concat,   # tz.identity will be called here
...     curried.get(5),  # get(5) is still a FUNCTION, see "curry" below
...     str,
... )
'4'
>>> str(curried.get(5)(identity([3, 4] * 4)))  # equivalent to the above
'4'

Curry
#####
Yummy.

A "curried" function (decorated with ``@curry``) can be called with
*only some of the required arguments* (i.e. partially parameterised).
If not all arguments are provided, a *new function* is returned which
can be called with the remaining arguments.

All functions in `turtwig` are curried, excluding those that only take in
one argument.

>>> from turtwig.futils import curry
>>> 
>>> @curry
... def add(a, b):
...     return a + b
... 
>>> add_5 = add(5)  # add_5 is equivalent to lambda b: 5 + b
>>> add_5(3) # call with remaining argument
8
>>> add(5, 3)  # You can also just use the function normally
8
>>> add(b=6)  # equivalent to lambda a: a + 6
<function add at 0x7f7b3c7b7d30>

.. admonition:: Using ``@curry`` with other decorators
    :class: warning

    If you are using ``@curry`` with other decorators, 
    ``@curry`` MUST be the last decorator. Otherwise the outer
    decorator will only be applied to the (possibly) partially 
    parameterised function. e.g. a function with both ``@curry`` 
    and ``@validate_call`` should be decorated as

    >>> @curry  # curry is the last decorator!
    ... @validate_call()
    ... def add(a, b):
    ...     return a + b
    ...
    >>> add(5)(3)  # validate_call only runs after all arguments are provided
    8
    >>> @validate_call()
    ... @curry  # curry is the last decorator!
    ... def add2(a, b):
    ...     return a + b
    ...
    >>> add2(5)(3)  # ValidationError: Parameter 'b' not provided



Useful Pre-Commit Hook
----------------------

Below is a useful sample pre-commit hook that

1. Dumps ``uv`` dependencies to ``requirements.txt``
2. Updates sphinx pages
3. Runs pytest
4. Runs code formatters (``black``, ``isort``)

.. code:: bash
    :number-lines:

    #!/usr/bin/env zsh

    set -e # Exit immediately if a command exits with a non-zero status

    echo "Dumping requirements.txt..."
    if [ -e "requirements.txt" ]; then
        rm requirements.txt
    fi
    uv pip compile pyproject.toml --quiet --output-file requirements.txt

    echo "Updating sphinx pages..."
    pushd ./docs
    make html
    popd

    uv run black .
    uv run isort .

    echo "Running pytest..."
    uv run pytest
    PYTEST_STATUS=$?  # capture exit status
    exit $PYTEST_STATUS
