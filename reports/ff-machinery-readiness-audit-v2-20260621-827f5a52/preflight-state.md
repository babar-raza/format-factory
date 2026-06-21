# Preflight State — Format Factory Machinery Audit v2
# Sprint ID: ff-machinery-readiness-audit-v2-20260621-827f5a52

## Repository State

| Field | Value |
|-------|-------|
| Branch | main |
| HEAD | 827f5a52 |
| Commits ahead of origin/main | 49 |
| Prior audit HEAD | 23d1333f |
| Commits since prior audit | 17 |

## Git Status

### Modified Files (tracked, uncommitted)
| File | Classification | Risk |
|------|---------------|------|
| registry/source-structure-baseline.json | machinery source | LOW — cap update |
| src/python/fods/neutral_model.py | product source | MEDIUM — 2186 LOC modified |
| tests/specification-authority-layer/test_qname_structure_validator.py | machinery test | LOW |
| tests/supervisor/test_governance_validators.py | machinery test | LOW |
| tools/supervisor/governance_validator_runner.py | machinery source | LOW |
| tools/supervisor/governance_validators.py | machinery source | LOW |

### Untracked Files
| Path | Classification | Risk |
|------|---------------|------|
| .claude/commands/sal-pipeline-heal.md | new skill command | LOW |
| reports/r129-fodt-install-proof-sprint2/ | evidence report | LOW |
| reports/skills-r127/ | skills evidence | LOW |
| src/python/fods/Compat/ | product source (facades) | MEDIUM — uncommitted facades |

## Key State Files

| File | Status | Value |
|------|--------|-------|
| .local/supervisor/active-plan-lock.json | plan_path=keen-dancing-hopper.md | status=TERMINAL_CLOSED |
| .local/supervisor/continuation-signal.json | state=YES | autonomous_continue=True, iter=10, stop_reason=None |
| reports/supervisor/approval-gates.md | AUTONOMOUS_CONTINUE: YES | MODE 4 ACTIVE |

## Plan Lock Analysis

The `active-plan-lock.json` has `status: "TERMINAL_CLOSED"` for the keen-dancing-hopper plan.
This is a PRODUCT track plan lock (`track_type: product`). TERMINAL_CLOSED means it does NOT
block product-track continuation (by GAP-WF-004 fix).

The stale plan lock issue from the prior audit is RESOLVED.

## Run ID Context

Latest completed sprint: sal-skill-gov-20260621-3104e1c1 (ACCEPTED, 1490 tests)
Evidence bundle: .local/supervisor/reviews/sal-skill-gov-20260621-3104e1c1/

## Source Layout

### Python Products (src/python/)
abw, csv, dif, fodg, fodp, fods, fodt, gnumeric, ndjson, ods, odt, pbm, pgm, ppm, qoi, sylk, toml, tsv, xcf, zst
Plus: _shared/, _readme.md

### .NET Products (src/net/)
csv, fods, fodt, html, markdown, ndjson, netpbm, tsv, txt, zst

### Spec Roots
- .local/spec-cache/ — SAL workbench (fods/1.3/ normalized, workbench/)
- specs/ — NOT FOUND (no top-level specs/ directory)
- docs/specification-*.md — design docs only

### Test Roots
- tests/python/ — format tests
- tests/specification-authority-layer/ — SAL tests
- tests/supervisor/ — governance/machinery tests
- tests/evidence/ — evidence validation tests

### Validator Roots
- tools/validators/ — standalone validators
- tools/supervisor/governance_validators.py — integrated validators (~40 validators)

### Autonomous Supervisor Files
- tools/supervisor/autonomous_cycle.py — main sprint executor
- tools/supervisor/check_continuation.py — continuation checker
- tools/supervisor/governance_validators.py — 40 validators
- tools/supervisor/supervisor_loop.py — wrapper
- reports/supervisor/ — all supervisor outputs

### SAL Files
- tools/specification-authority-layer/ — 19 SAL tools
- .local/spec-cache/ — spec data and workbench facts

### Capability Layer Files
- reports/capability-layer/ — gap-ledger.json (958 gaps), capability maps
- tools/capability_layer/ — 2 tools
- tools/supervisor/capability_compiler.py — feature compiler

### Skills Directory
- .claude/commands/ — 29 slash commands
- .supervisor/skill-registry.yaml — skill registry
