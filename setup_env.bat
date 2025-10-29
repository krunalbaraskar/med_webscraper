@echo off
REM This script creates a virtual environment and installs the necessary Python packages
REM to run the scraper notebook on Windows.

:: --- Configuration ---
set "VENV_NAME=venv_scraper"
set "PYTHON_EXE=python"
:: You can change the line above to "python3" if that's how you run Python

:: --- Main Script ---

echo [INFO] Looking for Python executable: %PYTHON_EXE%
where %PYTHON_EXE% >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] %PYTHON_EXE% command not found.
    echo [ERROR] Please ensure Python is installed and added to your PATH.
    goto :eof
)

echo [INFO] Using Python executable: %PYTHON_EXE%
echo [INFO] Checking for 'venv' module...
%PYTHON_EXE% -m venv --help >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] The '%PYTHON_EXE% -m venv' command failed.
    echo [ERROR] Please ensure the 'venv' module is available in your Python installation.
    goto :eof
)

:: 2. Create the virtual environment
if exist "%VENV_NAME%\" (
    echo [INFO] Virtual environment '%VENV_NAME%' already exists. Skipping creation.
) else (
    echo [INFO] Creating virtual environment '%VENV_NAME%'...
    %PYTHON_EXE% -m venv %VENV_NAME%
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to create virtual environment.
        goto :eof
    )
)

:: 3. Activate the virtual environment
echo [INFO] Activating virtual environment...
:: Removed quotes from the call path to avoid PowerShell interpretation issues
call %VENV_NAME%\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo [ERROR] Failed to activate virtual environment.
    goto :eof
)

:: 4. Install required packages
echo [INFO] Installing all necessary packages. This may take a few minutes...
pip install --upgrade pip
pip install ^
    jupyter ^
    selenium ^
    requests ^
    pandas ^
    beautifulsoup4 ^
    deep-translator ^
    tqdm ^
    lxml

if %errorlevel% neq 0 (
    echo [ERROR] Package installation failed.
    goto :eof
)

:: 5. Success message
echo.
echo [SUCCESS] Setup complete!
echo.
echo To activate the environment manually in the future, run:
echo   %VENV_NAME%\Scripts\activate.bat
echo.
echo Then, you can run your notebook with:
echo   jupyter notebook spanish_scraper.ipynb
echo.
pause

