# Format Factory — Autonomous Orchestrator Launcher (PowerShell)
# Sprint: FORMAT-FACTORY-AUTONOMOUS-ORCHESTRATOR-PERSISTENT-CONTINUATION-001
#
# Run this from an EXTERNAL PowerShell terminal (NOT inside Claude Code).
# This unsets CLAUDECODE so H6 external host proof is possible.
#
# Usage:
#   cd 'C:\Users\prora\OneDrive\Documents\GitHub\format-factory'
#   .\scripts\start_format_factory_orchestrator.ps1

param(
    [int]$MaxCycles = 3,
    [string]$Backend = "local",
    [switch]$Resume,
    [switch]$DryRun,
    [switch]$Once,
    [string]$SeedAction = "",
    [switch]$QueueFirst
)

$RepoRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$VenvPython = Join-Path $RepoRoot ".local\venv\Scripts\python.exe"
$Orchestrator = Join-Path $RepoRoot "tools\supervisor\autonomous_orchestrator.py"

# Remove CLAUDECODE to enable external host mode
$env:CLAUDECODE = ''
Write-Host "CLAUDECODE cleared (external host mode)"
Write-Host "Repo: $RepoRoot"
Write-Host "Python: $VenvPython"
Write-Host ""

if (-not (Test-Path $VenvPython)) {
    Write-Error "venv python not found: $VenvPython"
    exit 1
}

# Build args
$Args = @("--max-cycles", $MaxCycles, "--backend", $Backend)
if ($Resume) { $Args += "--resume" }
if ($DryRun) { $Args += "--dry-run" }
if ($Once) { $Args = @("--once", "--backend", $Backend) }
if ($SeedAction -ne "") { $Args += "--seed-action"; $Args += $SeedAction }
if ($QueueFirst) { $Args += "--queue-first" }

Write-Host "Starting orchestrator: $Args"
Write-Host "Press Ctrl+C to stop."
Write-Host ""

Push-Location $RepoRoot
try {
    & $VenvPython $Orchestrator @Args
    $ExitCode = $LASTEXITCODE
    Write-Host ""
    Write-Host "Orchestrator exited with code: $ExitCode"
    exit $ExitCode
} finally {
    Pop-Location
}
