#!/usr/bin/env bash

set -e # stop script execution after failure of any command

env_name="buk-reservation"
lock_file="conda-lock.yml"

conda-lock install -n $env_name $lock_file
