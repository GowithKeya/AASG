@echo off
title Agent Firewall Console
cd /d "%~dp0"
echo ==============================================
echo  Launching Agent Firewall & Dashboard Services
echo ==============================================
if exist guard-fw\.venv\Scripts\activate.bat (
    call guard-fw\.venv\Scripts\activate.bat
)
python scripts\run_web.py
pause
