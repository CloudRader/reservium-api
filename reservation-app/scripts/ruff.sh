#!/usr/bin/env bash
set -e  # Exit on error

usage() {
  echo "Usage: $0 [-f max_errors] [dirs...]
    -f    Fail if more than max_errors are found (optional)
    dirs  Optional list of directories to lint (default: app tests)"
}

dirs=("app" "tests")
USE_FAIL_UNDER=0
FAIL_UNDER_LIMIT=0

while getopts "f:" opt; do
  case ${opt} in
  f)
    USE_FAIL_UNDER=1
    FAIL_UNDER_LIMIT="$OPTARG"
    ;;
  *)
    usage
    exit 1
    ;;
  esac
done

shift $((OPTIND - 1))

if [ "$#" -gt 0 ]; then
  dirs=("$@")
fi

# Run Ruff and capture the output
ruff_output=$(ruff check "${dirs[@]}" || true)

echo "$ruff_output"

# Count number of errors (lines containing error codes like [E501])
error_count=$(echo "$ruff_output" | grep -cE '^[^ ]+:\d+:\d+: [A-Z]\d+')

if [ $USE_FAIL_UNDER -eq 1 ]; then
  echo "Found $error_count issues (limit: $FAIL_UNDER_LIMIT)"
  if [ "$error_count" -gt "$FAIL_UNDER_LIMIT" ]; then
    echo "❌ Too many linting issues"
    exit 1
  fi
fi

echo "✅ Ruff check completed."
