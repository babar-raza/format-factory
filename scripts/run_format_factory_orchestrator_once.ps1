# Format Factory — Run Orchestrator Once (PowerShell)
# Sprint: FORMAT-FACTORY-AUTONOMOUS-ORCHESTRATOR-PERSISTENT-CONTINUATION-001
#
# Runs exactly one orchestrator cycle, then stops.
# Used to test resume: run-once, stop, resume.

$RepoRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$VenvPython = Join-Path $RepoRoot ".local\venv\Scripts\python.exe"
$Orchestrator = Join-Path $RepoRoot "tools\supervisor\autonomous_orchestrator.py"

$env:CLAUDECODE = ''
Write-Host "Running ONE orchestrator cycle (external host mode)..."
Write-Host ""

Push-Location $RepoRoot
try {
    & $VenvPython $Orchestrator --once --backend local
    Write-Host "Exit code: $LASTEXITCODE"
    exit $LASTEXITCODE
} finally {
    Pop-Location
}
