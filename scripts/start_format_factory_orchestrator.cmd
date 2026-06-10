@echo off
REM Format Factory — Autonomous Orchestrator Launcher (CMD)
REM Sprint: FORMAT-FACTORY-AUTONOMOUS-ORCHESTRATOR-PERSISTENT-CONTINUATION-001
REM
REM Run from an EXTERNAL command prompt (NOT inside Claude Code).
REM Unsets CLAUDECODE for H6 external host proof.
REM
REM Usage: scripts\start_format_factory_orchestrator.cmd [max_cycles] [backend]

set CLAUDECODE=
echo CLAUDECODE cleared (external host mode)

set REPO_ROOT=%~dp0..
set VENV_PYTHON=%REPO_ROOT%\.local\venv\Scripts\python.exe
set ORCHESTRATOR=%REPO_ROOT%\tools\supervisor\autonomous_orchestrator.py

set MAX_CYCLES=%1
if "%MAX_CYCLES%"=="" set MAX_CYCLES=3

set BACKEND=%2
if "%BACKEND%"=="" set BACKEND=local

echo Repo: %REPO_ROOT%
echo Starting orchestrator: --max-cycles %MAX_CYCLES% --backend %BACKEND%
echo.

cd /d "%REPO_ROOT%"
"%VENV_PYTHON%" "%ORCHESTRATOR%" --max-cycles %MAX_CYCLES% --backend %BACKEND%
echo Orchestrator exited with code: %ERRORLEVEL%
