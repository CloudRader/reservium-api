#!/usr/bin/env bash
set -e  # stop script execution after failure of any command

# Lock dependencies based on pyproject.toml (generate or update poetry.lock)
poetry lock

# Optional: install the locked dependencies
poetry install