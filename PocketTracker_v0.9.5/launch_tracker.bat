
@echo off
cd /d %~dp0\PocketTracker_v0.9.3

REM Start the local server
start "" python -m http.server 8080

REM Launch only the main control panel
start "" python main.py
