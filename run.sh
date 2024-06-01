#!/bin/bash
# Script sets up the python virtual environment, installs needed python packages, and starts the game

# Path to this directory
script_path=$(realpath "$0")
rootdir=$(dirname "$script_path")

# Set up python venv and activate it
echo Setting up the environment
python3 -m venv $rootdir/.venv      >/dev/null
source $rootdir/.venv/bin/activate  >/dev/null
python3 -m pip install --upgrade pip    >/dev/null
python3 -m pip install -r $rootdir/.venv/requirements.txt >/dev/null

# Start the game
echo Starting the game
python3 $rootdir/src/main.py
