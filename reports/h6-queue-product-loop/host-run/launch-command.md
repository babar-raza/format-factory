# H6Q Queue-First Launch Command

## Local Queue-First Run (direct)

```bash
cd c:/Users/prora/OneDrive/Documents/GitHub/format-factory
$env:CLAUDECODE=''
.local/venv/Scripts/python tools/supervisor/autonomous_orchestrator.py \
  --max-cycles 3 --backend local --queue-first --json
```

## Via PowerShell Script (External Host, CLAUDECODE cleared)

```powershell
powershell -ExecutionPolicy Bypass -File scripts\start_format_factory_orchestrator.ps1 `
  -MaxCycles 3 -Backend local -Resume -QueueFirst
```

## Detached External Host (Start-Process)

```powershell
$env:CLAUDECODE='';
Start-Process powershell -ArgumentList `
  "-NoProfile -ExecutionPolicy Bypass -File scripts\start_format_factory_orchestrator.ps1 -MaxCycles 3 -Backend local -QueueFirst" `
  -WorkingDirectory "C:\Users\prora\OneDrive\Documents\GitHub\format-factory" `
  -PassThru -Wait
```

## Result

Run ID: 3ec7eca5
Cycles: 3
Stop code: MAX_CYCLES_REACHED
Queue items consumed: 3 (h6q-product-001, h6-q-001, h6-q-003)
Product source mutated: NO
