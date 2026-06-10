# External Host Command
Sprint: FORMAT-FACTORY-SUPERPOWERS-AGENTIC-AUTONOMY-EXECUTION-001

## H4 Proof (Local Backend — achievable from inside session)
```
.local/venv/Scripts/python tools/supervisor/next_action_runner.py \
  --action reports/superpowers-agentic-autonomy/two-cycle-proof/next-action-cycle-001.json \
  --allow-write "reports/superpowers-agentic-autonomy/two-cycle-proof/"
```
**Status: PROVEN (H4 achieved)**

## H6 External Host Command (PowerShell — run OUTSIDE Claude Code)
```powershell
# Run from external PowerShell (NOT inside Claude Code session):
$env:CLAUDECODE = ''
python 'c:\Users\prora\OneDrive\Documents\GitHub\format-factory\tools\supervisor\autonomous_host_daemon.py' `
  --action 'reports/superpowers-agentic-autonomy/two-cycle-proof/next-action-cycle-001.json' `
  --max-cycles 2 `
  --backend local
```
**Status: NOT PROVEN — CLAUDECODE=1 inside current session. Run externally for H6.**
