# Task Scheduler Proposal
Sprint: FORMAT-FACTORY-AUTONOMOUS-ORCHESTRATOR-PERSISTENT-CONTINUATION-001

## Status: PROPOSAL ONLY — Not Installed

Installing a Windows Task Scheduler task requires governance approval.
This document is the install proposal only.

## Proposed Task Configuration

Name: FormatFactoryOrchestrator
Trigger: On logon, or on schedule (every 30 minutes)
Action: PowerShell.exe -ExecutionPolicy Bypass -File "C:\Users\prora\OneDrive\Documents\GitHub\format-factory\scripts\start_format_factory_orchestrator.ps1"

## Install Command (Future Sprint — Governance Required)

```powershell
schtasks /Create /TN "FormatFactoryOrchestrator" `
  /TR "PowerShell.exe -ExecutionPolicy Bypass -File '$env:USERPROFILE\OneDrive\Documents\GitHub\format-factory\scripts\start_format_factory_orchestrator.ps1' -MaxCycles 3 -Backend local -Resume" `
  /SC ONLOGON /RL HIGHEST
```

## Current Classification

PROPOSAL_ONLY — not installed this sprint.
Governance required before scheduling.
