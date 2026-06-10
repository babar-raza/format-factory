# autonomous_external_host.ps1
# Format Factory External Autonomous Host Loop Bootstrap
#
# Run this script from PowerShell OUTSIDE of VS Code / Claude Code.
# It removes CLAUDECODE from the environment and starts the host loop.
#
# Usage:
#   cd "C:\Users\prora\OneDrive\Documents\GitHub\format-factory"
#   .\scripts\autonomous_external_host.ps1
#
# For dry-run (no Claude invocation):
#   .\scripts\autonomous_external_host.ps1 -DryRun
#
# For custom next-action:
#   .\scripts\autonomous_external_host.ps1 -NextAction "reports\...\next-action.json"

param(
    [switch]$DryRun,
    [string]$NextAction = "reports\autonomous-external-host-bootstrap\next-action.json",
    [string]$OutputDir = "reports\autonomous-external-host-bootstrap\host-loop"
)

$ErrorActionPreference = "Stop"

# ── 1. Navigate to repo root ────────────────────────────────────────────────
$RepoRoot = Split-Path -Parent $PSScriptRoot
Push-Location $RepoRoot
Write-Host "Repo root: $RepoRoot"

# ── 2. Remove CLAUDECODE from environment ───────────────────────────────────
if ($env:CLAUDECODE) {
    Write-Host "Removing CLAUDECODE from environment (was: $($env:CLAUDECODE))"
    Remove-Item Env:CLAUDECODE -ErrorAction SilentlyContinue
} else {
    Write-Host "CLAUDECODE not set (good — not running inside Claude Code)"
}

# ── 3. Detect Python ─────────────────────────────────────────────────────────
$Python = ".\.local\venv\Scripts\python.exe"
if (-not (Test-Path $Python)) {
    $Python = "python"
}
Write-Host "Python: $Python"
& $Python --version

# ── 4. Build command ─────────────────────────────────────────────────────────
$Args = @(
    "tools\supervisor\external_host_loop.py",
    "--next-action", $NextAction,
    "--output-dir", $OutputDir,
    "--repo-root", $RepoRoot
)
if ($DryRun) {
    $Args += "--dry-run"
    Write-Host "MODE: DRY RUN"
} else {
    Write-Host "MODE: LIVE (will invoke Claude CLI)"
}

# ── 5. Run host loop ─────────────────────────────────────────────────────────
Write-Host ""
Write-Host "Starting external host loop..."
Write-Host "Command: $Python $($Args -join ' ')"
Write-Host ""

& $Python @Args
$ExitCode = $LASTEXITCODE

# ── 6. Report result ─────────────────────────────────────────────────────────
Write-Host ""
if ($ExitCode -eq 0) {
    Write-Host "HOST LOOP: SUCCESS (exit 0)" -ForegroundColor Green
} else {
    Write-Host "HOST LOOP: FAILED or BLOCKED (exit $ExitCode)" -ForegroundColor Red
}

$ResultPath = Join-Path $RepoRoot "$OutputDir\host-loop-result.json"
if (Test-Path $ResultPath) {
    Write-Host "Result: $ResultPath"
    Get-Content $ResultPath | ConvertFrom-Json | ConvertTo-Json -Depth 3
}

Pop-Location
exit $ExitCode
