# Distribution and platform verification

The default branch is tested on Linux (Python 3.11–3.13), Windows (3.13)
and macOS (3.13). The CI matrix is not a guarantee for all operating system
versions or filesystem configurations. Non-forced CSV publication requires
hard-link support; symbolic-link tests can skip when the runner lacks permission.

## Reproduce package checks

Run these commands from a clean checkout in a development environment:

```sh
python -m pip install build twine
python -m build
python -m twine check dist/*
python tools/check_distribution.py
```

The source archive includes the format schema, examples, documentation and
tests. The wheel contains the Python runtime and CLI, not the entire repository.
The verification script installs the local wheel without dependencies or index
access into a fresh virtual environment outside the checkout, checks its
metadata, runs the documented CLI, and compares CSV bytes to the golden fixture.
Building may require downloading build-time dependencies. No command publishes
a package to PyPI. The project remains distributed through GitHub only.

CI is the source of truth for the current commit; passing checks are necessary,
not sufficient, for a release.
