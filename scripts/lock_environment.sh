#!/usr/bin/env bash
set -e  # Exit on first error

# Optional: explicitly create the virtual environment in `.venv`
uv venv .venv

# Activate virtual environment
source .venv/bin/activate

# Lock dependencies (update uv.lock from pyproject.toml)
uv pip compile pyproject.toml --output-file=uv.lock

# Sync the virtual environment with the lock file
uv sync

echo "Environment ready using uv and uv.lock"