#!/usr/bin/env bash

set -e # stop script execution after failure of any command
set -x # print all executed commands

conda config --add channels conda-forge
conda config --set channel_priority strict
