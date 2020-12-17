#!/bin/bash
echo "Creating Virtual Environment..."
python -m venv ../venv
python -m pip install --upgrade pip
echo "Virtual Environment created."
echo "Installing modules from requirements.txt"
python -m pip install pip-tools
pip-sync
echo "Modules installed."