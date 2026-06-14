@echo off
REM ===== Starting Downloader =====

echo Checking dependencies...
pip install -r requirements.txt

echo.
echo Opening application...
python downloader.py

pause
