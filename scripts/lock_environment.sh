#!/usr/bin/env bash
set -e # stop script execution after failure of any command

env_file_path="environment-dev.yml"
lock_file_path="conda-lock.yml"

conda-lock -f $env_file_path --lockfile $lock_file_path --platform=linux-aarch64
