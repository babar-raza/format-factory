# Format Factory — Task Scheduler Install Proposal Script (PowerShell)
# Sprint: FORMAT-FACTORY-AUTONOMOUS-ORCHESTRATOR-PERSISTENT-CONTINUATION-001
#
# STATUS: PROPOSAL ONLY — NOT EXECUTED
# Installing a Task Scheduler task requires governance approval.
# This script contains the install command for review/approval.
# Do NOT run this script without governance authorization.
#
# To install (after governance approval):
#   PowerShell -ExecutionPolicy Bypass -File scripts\install_format_factory_orchestrator_task.ps1

param([switch]$DryRun = $true)

$RepoRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$Script = Join-Path $RepoRoot "scripts\start_format_factory_orchestrator.ps1"

$TaskName = "FormatFactoryOrchestrator"
$TaskAction = "PowerShell.exe -ExecutionPolicy Bypass -File `"$Script`" -MaxCycles 3 -Backend local -Resume"

Write-Host "Task Scheduler Install Proposal"
Write-Host "Task name: $TaskName"
Write-Host "Action: $TaskAction"
Write-Host ""

if ($DryRun) {
    Write-Host "DRY RUN — Not installing. Set -DryRun:`$false after governance approval to install."
    exit 0
}

Write-Host "Installing task (requires admin)..."
schtasks /Create /TN $TaskName /TR $TaskAction /SC ONLOGON /RL HIGHEST /F
Write-Host "Exit: $LASTEXITCODE"
