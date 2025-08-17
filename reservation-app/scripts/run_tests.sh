#!/usr/bin/env bash

set -e # stop script execution after failure of any command

src_dir="../app"

usage() {
  echo "Usage: $0 [-c] [-r] [-f value] args
    -c - run with coverage
    -r - run with coverage and generate coverage report
    -f - fail under specified percentage"
}

RUN_COVERAGE=0
GENERATE_COVERAGE_REPORT=0
USE_FAIL_UNDER=0
COVERAGE_LIMIT_PERCENTAGE=0

while getopts "crf:" opt; do
  case ${opt} in
  r)
    GENERATE_COVERAGE_REPORT=1
    ;;
  c)
    RUN_COVERAGE=1
    ;;
  f)
    USE_FAIL_UNDER=1
    COVERAGE_LIMIT_PERCENTAGE="$OPTARG"
    ;;
  *)
    usage
    exit 0
    ;;
  esac
done

cd tests
if [ $GENERATE_COVERAGE_REPORT -eq 1 ]; then
  if [ $USE_FAIL_UNDER -eq 1 ]; then
    pytest --cov=$src_dir --cov-report=term --cov-branch --cov-report=html:coverage --cov-report=xml:coverage.xml --cov-fail-under="$COVERAGE_LIMIT_PERCENTAGE"
  else
    pytest --cov=$src_dir --cov-report=term --cov-branch --cov-report=html:coverage --cov-report=xml:coverage.xml
  fi
elif [ $RUN_COVERAGE -eq 1 ]; then
  if [ $USE_FAIL_UNDER -eq 1 ]; then
    pytest --cov=$src_dir --cov-report=term --cov-branch --cov-fail-under="$COVERAGE_LIMIT_PERCENTAGE"
  else
    pytest --cov=$src_dir --cov-report=term --cov-branch
  fi
else
  pytest
fi
