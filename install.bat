@echo off
echo Checking for dependencies...
pip freeze > installed.txt
findstr /i "requests" installed.txt >nul
if %errorlevel% neq 0 (
    echo Installing dependencies...
    pip install -r requirements.txt
) else (
    findstr /i "rich" installed.txt >nul
    if %errorlevel% neq 0 (
        echo Installing dependencies...
        pip install -r requirements.txt
    ) else (
        echo Dependencies already satisfied.
    )
)
del installed.txt

echo.
echo Installing Lemon Package Manager...
pip install .
echo.
echo Lemon Package Manager has been successfully installed.
echo You can now use the 'lemon' or 'lpm' commands in your terminal.
pause
