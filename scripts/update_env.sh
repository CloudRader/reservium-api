#!/usr/bin/env bash

set -e

# Optional: configure Poetry
poetry config virtualenvs.in-project false

# Update all dependencies to the latest allowed versions
poetry update

# (Optional) install those updated dependencies into the venv
poetry install

echo "Poetry dependencies updated and installed."