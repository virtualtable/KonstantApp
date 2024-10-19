@echo off
TITLE Konstant setup
SET "PYTHON_EXE=python"
SET "PYTHON_URL=https://www.python.org/ftp/python/3.10.9/python-3.10.9-amd64.exe"
SET "PYTHON_INSTALLER=python_installer.exe"

where %PYTHON_EXE% >nul 2>nul
IF ERRORLEVEL 1 (
    echo Python is not installed. Downloading installer...
    powershell -command "Invoke-WebRequest -Uri %PYTHON_URL% -OutFile %PYTHON_INSTALLER%"
    echo Installing Python...
    start /wait %PYTHON_INSTALLER% /quiet InstallAllUsers=1 PrependPath=1
    del %PYTHON_INSTALLER%
) ELSE (
    echo Python is already installed.
)

pip --version >nul 2>nul
IF ERRORLEVEL 1 (
    echo Pip is not installed. Installing Pip...
    python -m ensurepip
)

echo Installing PyQt5 and requests...
pip install PyQt5 requests

echo Setup complete.
call run.bat
