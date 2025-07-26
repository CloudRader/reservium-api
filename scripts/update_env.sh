#!/usr/bin/env bash

set -e
set -x  # optional: print commands for debugging

# Update the lockfile with latest allowed dependency versions
uv lock --upgrade

# Sync the environment: install updated dependencies
uv sync

echo "UV dependencies updated and installed."