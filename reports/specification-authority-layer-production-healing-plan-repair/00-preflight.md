# Preflight — Specification Authority Layer Production Healing Plan Repair
Sprint ID: FORMAT-FACTORY-SPECIFICATION-AUTHORITY-LAYER-PRODUCTION-HEALING-PLAN-REPAIR-001
Date: 2026-06-04

## PYTHON Setup

```
PYTHON_DETECTED: .local/venv/Scripts/python
PYTHON_VERSION:  Python 3.13.2
PYTHON_STATUS:   READY
```

## REPO_ROOT

```
REPO_ROOT: C:/Users/prora/OneDrive/Documents/GitHub/format-factory
```

Note: All file paths in this sprint use REPO_ROOT-relative notation. Absolute paths are
derived at runtime using: `REPO_ROOT=$(git rev-parse --show-toplevel)`

## PYTHON Variable (Bash)

```bash
if [ -f ".local/venv/Scripts/python" ]; then
  PYTHON=".local/venv/Scripts/python"
elif [ -f ".local/venv/bin/python" ]; then
  PYTHON=".local/venv/bin/python"
else
  PYTHON="python"
fi
$PYTHON --version  # Must succeed
REPO_ROOT="$(git rev-parse --show-toplevel)"
ZIP_PATH="$REPO_ROOT/.local/supervisor/reviews/specification-authority-layer-production-healing-plan-repair/declaration-review-package.zip"
```

## PYTHON Variable (PowerShell)

```powershell
if (Test-Path ".local/venv/Scripts/python.exe") { $PYTHON = ".local/venv/Scripts/python.exe" }
elseif (Test-Path ".local/venv/bin/python") { $PYTHON = ".local/venv/bin/python" }
else { $PYTHON = "python" }
& $PYTHON --version
if ($LASTEXITCODE -ne 0) { Write-Error "ERROR: Python not found. Abort."; exit 1 }
$REPO_ROOT = (git rev-parse --show-toplevel)
$ZIP_PATH = "$REPO_ROOT/.local/supervisor/reviews/specification-authority-layer-production-healing-plan-repair/declaration-review-package.zip"
```

## Git State

```
Branch: main
Last commit: 3a86a05 feat(r93): context-pack, D92 defect repair, governed acceleration
```

## Governance Reads

| File | Status | Key Value |
|------|--------|-----------|
| CLAUDE.md | PRESENT | Session instructions loaded |
| AGENTS.md | MISSING (caveat) | — |
| docs/governance/ai-authority-boundary.md | PRESENT | "AI thinks and drafts. Evidence decides." |
| plans/master-plan.md | PRESENT | R93 complete; autonomous continue YES |
| reports/supervisor/session-resume.md | PRESENT | Last sprint: LOCAL-MEMORY-SYNC, ACCEPTED |
| reports/supervisor/approval-gates.md | PRESENT | autonomous-continue: TRI-LANE sprint (see note) |
| .supervisor/policies.yaml | PRESENT | — |
| .supervisor/schemas/evidence-declaration.schema.json | PRESENT | schema loaded |
| tools/supervisor/autonomous_cycle.py | PRESENT | exit 0=accepted, 3=rework, other=error |
| tools/supervisor/build_declaration_review_package.py | PRESENT | ZIP builder available |

**Note on approval-gates.md:** The file is associated with sprint
FORMAT-FACTORY-TRI-LANE-INTEGRATION-REFRESH-AND-MAINSTREAM-READINESS-GATE-001.
This repair sprint (FORMAT-FACTORY-SPECIFICATION-AUTHORITY-LAYER-PRODUCTION-HEALING-PLAN-REPAIR-001)
is an independent plan-repair sprint. No AUTONOMOUS_CONTINUE: NO block detected for this sprint.
Proceeding.

## Dirty State Classification

| Path Pattern | Classification | Action |
|---|---|---|
| M src/net/fods/FodsDocument.cs | PRE_EXISTING_DOC_STATE | Do not modify |
| M src/net/fodt/FodtDocument.cs | PRE_EXISTING_DOC_STATE | Do not modify |
| M src/net/netpbm/Model/NetpbmImage.cs | PRE_EXISTING_DOC_STATE | Do not modify |
| M src/python/sylk/sylk_parser.py | PRE_EXISTING_DOC_STATE | Do not modify |
| M product-capability-matrix/poc-targets.yaml | PRE_EXISTING_DOC_STATE | Do not modify |
| M reports/supervisor/** | PRE_EXISTING_DOC_STATE | Do not modify |
| M tools/supervisor/** | PRE_EXISTING_DOC_STATE | Do not modify |
| M .supervisor/**, .claude/commands/**, plans/** | PRE_EXISTING_DOC_STATE | Do not modify |
| ?? tests/supervisor/test_tri_lane_integration_fabric.py | OTHER_RUNNING_SPRINT_DIRTY_STATE | Do not touch |
| ?? tests/supervisor/test_tri_lane_integration_refresh_readiness.py | OTHER_RUNNING_SPRINT_DIRTY_STATE | Do not touch |
| ?? tools/supervisor/tri_lane_integration.py | OTHER_RUNNING_SPRINT_DIRTY_STATE | Do not touch |
| ?? tools/supervisor/validate_tri_lane_contract.py | OTHER_RUNNING_SPRINT_DIRTY_STATE | Do not touch |
| ?? tools/supervisor/generate_mainstream_execution_packet.py | OTHER_RUNNING_SPRINT_DIRTY_STATE | Do not touch |
| ?? tests/net/**, tests/python/** | PRE_EXISTING_DOC_STATE | Do not modify |
| ?? examples/**, memory/**, docs/**, state/** | PRE_EXISTING_DOC_STATE | Do not modify |

**Overall verdict:** ALLOWED_DIRTY_STATE — all dirty files are pre-existing from previous sprints
or from the co-running TRI-LANE sprint. This repair sprint touches only its allowed write paths.
