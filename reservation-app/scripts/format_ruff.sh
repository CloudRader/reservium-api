#!/usr/bin/env bash
set -e  # Exit on error

usage() {
  echo "Usage: $0 [--check] [--unsafe-fix] [dirs...]"
  echo "  --check         Only check formatting without changing files"
  echo "  --unsafe-fix    Apply unsafe fixes as well"
  echo "  dirs            Optional list of directories/files to format (default: src tests)"
}

dirs=("src" "tests")
ruff_args=()

# Parse arguments
while [[ $# -gt 0 ]]; do
  case "$1" in
    --check)
      ruff_args+=("--check")
      shift
      ;;
    --unsafe-fix|--unsafe-fixes|-uf)
      ruff_args+=("--unsafe-fixes")
      shift
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
    *) # positional args (dirs/files)
      dirs=("$@")
      break
      ;;
  esac
done

# Run ruff format with chosen args
echo "Running: ruff format ${ruff_args[*]} ${dirs[*]}"
ruff format "${ruff_args[@]}" "${dirs[@]}"

echo "✅ Ruff format completed."
