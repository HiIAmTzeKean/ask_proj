@ECHO OFF
ECHO Creating Virtual Environment...
python -m venv ../venv
call ..\venv\Scripts\activate.bat
python -m pip install --upgrade pip
ECHO Virtual Environment created.
ECHO Installing modules from requirements.txt
python -m pip install pip-tools
pip-sync
ECHO Modules installed.