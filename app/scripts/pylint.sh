#!/usr/bin/env bash
set -e # stop script execution after failure of any command

usage() {
  echo "Usage: $0 [-f value] args
    -f - fail under specified score limit"
}

dirs=("app/*.py" "app/**/*.py" "tests/*.py" "tests/**/*.py")

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
    exit 0
    ;;
  esac
done

processed_args=$((OPTIND - 1))
shift $processed_args

if [ -n "$*" ]; then
  dirs=()
  for dir in "$@"; do
    if [ -d "$dir" ]; then
      dirs+=("$dir/*.py")
      dirs+=("$dir/**/*.py")
    else
      echo "Directory $dir does not exists. Skipping."
    fi
  done
fi

pylint_args+=("-v" "${dirs[@]}")

if [ $USE_FAIL_UNDER -eq 1 ]; then
  pylint_args+=("--fail-under=$FAIL_UNDER_LIMIT")
fi

pylint "${pylint_args[@]}"