#!/usr/bin/env bash
set -e # stop script execution after failure of any command

REPORT_OUTPUT_DIR="mypy_report"
GENERATE_HTML_REPORT=0
GENERATE_XML_REPORT=0

usage() {
  echo "Usage: $0 [-hx] args
    -h - generate html report
    -x - generate xml report"
}

while getopts "hx" opt; do
  case ${opt} in
  h)
    GENERATE_HTML_REPORT=1
    ;;
  x)
    GENERATE_XML_REPORT=1
    ;;
  *)
    usage
    exit 0
    ;;
  esac
done

processed_args=$((OPTIND - 1))
shift $processed_args

mypy_args=()
if [ $GENERATE_HTML_REPORT -eq 1 ]; then
  mypy_args+=("--html-report" "${REPORT_OUTPUT_DIR}_html")
fi

if [ $GENERATE_XML_REPORT -eq 1 ]; then
  mypy_args+=("--xml-report" "${REPORT_OUTPUT_DIR}_xml")
fi

# get additional args
mypy_args+=("$@")

mypy "${mypy_args[@]}"
