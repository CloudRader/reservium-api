#!/usr/bin/env bash

set -e  # Exit immediately if a command exits with a non-zero status

# Optional: set poetry environment name
env_name="buk-reservation"

# Ensure poetry is available (optional check)
if ! command -v poetry &> /dev/null; then
    echo "Poetry is not installed. Please install it first."
    exit 1
fi

# Disable poetry creating virtualenvs in project dir (optional)
poetry config virtualenvs.in-project false

# Install dependencies from pyproject.toml and poetry.lock
poetry install

echo "Environment '$env_name' created or updated using Poetry."