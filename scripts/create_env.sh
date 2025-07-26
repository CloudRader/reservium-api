#!/usr/bin/env bash

set -e  # Exit on error

env_name=".venv"  # Default venv directory name

# Ensure uv is available
if ! command -v uv &> /dev/null; then
    echo "uv is not installed. Please install it first: https://github.com/astral-sh/uv"
    exit 1
fi

# Create the virtual environment if it doesn't exist
if [ ! -d "$env_name" ]; then
    echo "Creating virtual environment in $env_name"
    uv venv "$env_name"
else
    echo "Virtual environment $env_name already exists"
fi

# Install dependencies from pyproject.toml and uv.lock
uv sync

echo "Environment '$env_name' is ready using uv."