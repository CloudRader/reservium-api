#!/usr/bin/env bash

set -e  # Exit on error

# Check if pre-commit is installed
if ! command -v pre-commit &> /dev/null; then
    echo "pre-commit is not installed."
    echo "Please install it independently using one of these commands:"
    echo "  pip install pre-commit"
    echo "  brew install pre-commit (on macOS)"
    exit 1
fi

# Install the git hooks
echo "Installing git hooks..."
pre-commit install

# Run pre-commit on all files
echo "Running pre-commit on all files..."
pre-commit run --all-files

echo "Pre-commit checks completed and hooks are installed."
