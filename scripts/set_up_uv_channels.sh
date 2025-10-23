#!/usr/bin/env bash

set -e  # stop on error
set -x  # print commands

# Note: uv does not have direct config commands like poetry.
# You manage your pyproject.toml, uv.lock, and venv manually.

# Optional: create virtual environment (if not already created)
uv venv .venv

# Optional: print installed uv version (debugging)
uv --version

# Lock dependencies from pyproject.toml into uv.lock
uv pip compile pyproject.toml --output-file=uv.lock

# Sync the environment to install packages exactly as locked
uv sync

# There is no uv equivalent for managing multiple repos like poetry source add
# For that, modify pyproject.toml repositories section directly if needed