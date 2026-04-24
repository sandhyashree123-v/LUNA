@echo off
setlocal

cd /d "%~dp0"

start "LUNA Backend" cmd /k "cd /d %~dp0InnerVoice_Jelly && python -m uvicorn backend:app --reload --host 127.0.0.1 --port 8000"
start "LUNA Frontend" cmd /k "cd /d %~dp0 && npm.cmd run dev"
