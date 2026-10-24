@echo off
title AASG - CY-03 Agent Firewall Console
cd /d "%~dp0"
echo ==============================================
echo   Launching AASG Firewall & Dashboard Web Stack
echo ==============================================
if exist guard-fw\.venv\Scripts\activate.bat (
    call guard-fw\.venv\Scripts\activate.bat
)
python scripts\run_web.py
pause
