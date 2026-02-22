@echo off
setlocal

set VENV_DIR=venv

echo Starting Local RAG App Setup...

REM Check if python is installed
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo Error: Python not found. Please install Python 3.10 or 3.11.
    pause
    exit /b 1
)

REM Create venv if not exists
if not exist %VENV_DIR% (
    echo Creating virtual environment...
    python -m venv %VENV_DIR%
    if %errorlevel% neq 0 (
        echo Failed to create virtual environment.
        pause
        exit /b 1
    )
    echo Virtual environment created.
)

REM Activate venv
call %VENV_DIR%\Scripts\activate.bat

REM Update pip
python -m pip install --upgrade pip

REM Install dependencies
if exist requirements.txt (
    echo Installing dependencies...
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo Failed to install dependencies.
        pause
        exit /b 1
    )
) else (
    echo requirements.txt not found!
    pause
    exit /b 1
)

REM Run app
echo Starting Streamlit App...
streamlit run app/main.py

endlocal
