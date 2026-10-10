@echo off
setlocal
cd /d "%~dp0"
py -3 -m venv .venv
if errorlevel 1 goto error
.venv\Scripts\python.exe -m pip install -r requirements.txt
if errorlevel 1 goto error
.venv\Scripts\python.exe build.py %*
if errorlevel 1 goto error
echo SUCCESS - see the outputs folder next to this project.
pause
exit /b 0
:error
echo Build failed. Review the message above.
pause
exit /b 1
