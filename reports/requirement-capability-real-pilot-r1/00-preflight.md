# RCA Real Pilot R1 — Preflight
# Sprint: FORMAT-FACTORY-REQUIREMENT-CAPABILITY-AUTHORITY-LAYER-REAL-PILOT-R1-001

## Python Resolver
```
PYTHON=.local/venv/Scripts/python
Resolved: .local/venv/Scripts/python (Python 3.13.2)
```

## Git State
```
HEAD: 3a86a05295cb4b82ed40a3408b0612a90f93643c
Branch: main
Dirty: yes (pre-existing M-tagged src/ files from R93; untracked sprint reports — classified NON_BLOCKING_SPRINT_ARTIFACTS)
```

## Governance Reads
- AGENTS.md: READ — MODE EXECUTION, no self-approval, no push
- session-resume.md: READ — Last sprint SPEC-AUTHORITY-R2 ACCEPTED, MCP ACTIVE MODE 4
- poc-targets.yaml: READ (read-only) — FODS/FODT/Netpbm COMMERCIAL_NET, ZST/DIF/SYLK FOSS_REDUCED
- reports/supervisor/approval-gates.md: NOT READ (will check autonomous-continue)

## Spec Authority R2 Status
- Status: ACCEPTED (evidence verdict from session-resume)
- Context packs present: ZST, Netpbm, DIF, FODS
- Context packs path: .local/evidences/spec-authority-real-pilot-r2/context-packs/
- FODT: NOT in R2 — fixture-backed input required
- SYLK: NOT in R2 — fixture-backed input required

## Product Source Discovery
| Product | Impl Path | Test Count | Examples |
|---------|-----------|-----------|----------|
| FODS .NET | src/net/fods/ (5 files) | 68 tests | examples/net/fods/ |
| FODT .NET | src/net/fodt/ (5 files) | 65 tests | examples/net/fodt/ |
| Netpbm .NET | src/net/netpbm/Model/NetpbmImage.cs | 58 tests | examples/net/netpbm/ |
| ZST Python | src/python/zst/zst_codec.py | 24 tests | examples/python/zst/ |
| DIF Python | src/python/dif/dif_parser.py | 21 tests | (none found) |
| SYLK Python | src/python/sylk/sylk_parser.py | present | examples/python/sylk/ |

## RCA Tool Layer
- tools/requirements_authority/ — 15 modules (13 + __init__ + models) — PRESENT

## Prohibitions Affirmed
- No git push
- No poc-targets.yaml mutation
- No registry/format-registry.yaml mutation
- No src/net/** or src/python/** edits
- No tests/net/** or tests/python/** edits
- No Spec Authority R2 evidence mutation
- No ai_draft as proof
- No file-existence as proof
- No export PASS without target writer

## Pilot Plan
- Pilot A: Netpbm (.NET) — strong product proof
- Pilot B: FODS (.NET) — overclaim prevention (blocked export)
- Pilot C: FODT (.NET) — overclaim prevention (blocked export)
- Pilot D: ZST (Python) — spec-backed roundtrip proof
- Pilot E: DIF (Python) — empirical/caveated requirement
