
# How to Package and Distribute a Python Project

There are two aspects of this, which are orthogonal

- working with a virtual environment
- packaging the project such that it can be installed with pip

Packaging is independent of the concept of virtual environment and vice versa.

## Working with a Virtual Environment

Working with a virtual environment for a Python project means that all 
dependencies for that project are installed locally to the project,
and thefore do not affect other projects. Below is shown how to do
this in command line mode. If you work with an IDE such as PyCharm or 
VS, the IDE will have support for this.

First enable working with virtual environments in command line mode:

```
pip install virtualenv
```

In the directory of the project type:

```
python -m venv .venv
```

The name `.venv` can in fact be any name and does not need to start with `.`, this is just
common.

Then activate it:

```
source .venv/bin/activate
```

Do the following to see what the environment contains:

```
pip list
```

Now install various packages needed in the virtual environment, e.g.:

```
pip install dotmap
```

You can also see what dependencies are needed for export by:

```
pip freeze
```

This lists the dependencies in such a format that can be directly used when creating a package for
distribution with a `pyproject.toml` file (see below).

Deactivate the virtual environemt as follows when no longer needed

```
deactivate
```

## Packaging a Project for Distribution and Using it

### Packaging the Project

This section shows how to package a project such that a user can install it with `pip`,
and automatically get all the dependencies installed. Note that the user can install
the project in a virtual environment or not. These two things are orthogonal.

First create a `pyproject.toml` file. A minimal example is shown below:

```toml
# pyproject.toml

[build-system]
requires      = ["setuptools>=61.0.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "fuzz"
version = "1.0.0"
description = "A package for fuzz testing command driven flight software."
readme = "README.md"
authors = [
    { name = "Tracy Clark", email = "tracy.a.clark@jpl.nasa.gov"},
    { name = "Klaus Havelund", email = "klaus.havelund@jpl.nasa.gov"},
    { name = "Vivek Reddy", email = "vivek.j.reddy@jpl.nasa.gov"}
]
license = { file = "LICENSE" }
dependencies = [
  "dotmap >= 1.3.30",
  "future >= 1.0.0",
  "z3 >= 0.2.0",
  "z3-solver >= 4.13.2.0"
]
requires-python = ">=3.6"

[project.urls]
Homepage = "https://github.jpl.nasa.gov/lars/fuzzing"
```
If one needs to point out special packages in the distribution one can do this with a (needs investigation):

```
packages = ["dir1", "dir2"] 
```

Make sure you have the right tools at hand for creating a package:

```
pip install build setuptools wheel
```

Now build the project:

```
python -m build
```

Apparently not when in virtual mode (should be checked).

### Using the Project

Now another project can install this project:

```
pip install /path/to/fuzz
```

