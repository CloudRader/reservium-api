#!/usr/bin/env bash

set -e  # stop on error
set -x  # print commands

# Set Poetry to use PyPI (default) or custom repositories if needed
# (Only needed if you want to use a custom or additional package source)

# Example: Add a custom repository (optional, analogous to conda channels)
# poetry source add --priority=explicit some-repo https://some.repo/simple/

# Ensure Poetry does not use virtualenvs (optional, depends on your workflow)
poetry config virtualenvs.create false

# Print current config (optional for debugging)
poetry config --list