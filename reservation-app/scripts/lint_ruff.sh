#!/usr/bin/env bash
set -e  # Exit on error

usage() {
  echo "Usage: $0 [--fix|--unsafe-fix] [-f max_errors] [dirs...]"
  echo "  --fix           Automatically fix linting issues"
  echo "  --unsafe-fix    Apply unsafe fixes as well"
  echo "  -f <num>        Fail if more than <num> issues are found"
  echo "  dirs            Optional list of directories to lint (default: src tests)"
}

dirs=("src" "tests")
USE_FAIL_UNDER=0
FAIL_UNDER_LIMIT=0
ruff_args=()

# Manual arg parsing for long opts + getopts for short
while [[ $# -gt 0 ]]; do
  case "$1" in
    --fix)
      ruff_args+=("--fix")
      shift
      ;;
    --unsafe-fix|--unsafe-fixes|-uf)
      ruff_args+=("--unsafe-fixes")
      shift
      ;;
    -f)
      USE_FAIL_UNDER=1
      FAIL_UNDER_LIMIT="$2"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    --) # end of options
      shift
      break
      ;;
    -*)
      echo "Unknown option: $1"
      usage
      exit 1
      ;;
    *) # positional (dirs)
      dirs=("$@")
      break
      ;;
  esac
done

# Run Ruff and capture the output
ruff_output=$(ruff check "${ruff_args[@]}" "${dirs[@]}" || true)

echo "$ruff_output"

error_count=$(grep -cE '^[^:]+:[0-9]+:[0-9]+: [A-Z][0-9]{3}' <<< "$ruff_output" || true)

if [ "$error_count" -gt "$FAIL_UNDER_LIMIT" ]; then
  echo "Found $error_count issues (limit: $FAIL_UNDER_LIMIT)"
  if [ "$error_count" -gt "$FAIL_UNDER_LIMIT" ]; then
    echo "❌ Too many linting issues"
    exit 1
  fi
fi

echo "✅ Ruff check completed."
exit 0
