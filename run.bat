:: Script sets up the python virtual environment, installs needed python packages, and starts the game

@ECHO off

:: Set up python venv and activate it
ECHO Setting up the environment
CALL python -m venv .venv
CALL .venv\Scripts\activate.bat

:: Collect and install needed packages
ECHO Collecting and installing needed packages
CALL python -m pip install --upgrade pip
CALL python -m pip install -r .venv/requirements.txt

:: Start the game
ECHO Starting the game
CALL python ./src/main.py
