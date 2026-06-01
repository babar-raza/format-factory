# Next Worker Prompt
Generated: 2026-06-01T17:13:11.531773
Previous Sprint: FORMAT-FACTORY-R86-SUPERVISOR-TRUTH-POC-PRODUCT-FACTORY-DEEPENING-NETPBM-FODS-FODT-FOSS-DOGFOOD-MEGA-TRAIN-001
Previous Verdict: ACCEPTED
Previous Run: r86-real-sprint-validation
Autonomous Continue: True

## Read Before Execution
Read these files before taking any action:
- AGENTS.md
- GOVERNANCE.md
- plans/master-plan.md
- registry/format-registry.yaml
- reports/supervisor/session-resume.md
- reports/supervisor/latest-review.md
- .supervisor/policies.yaml

## Previously Accepted Items
- R86-SUP-TRUTH: Supervisor truth repair (D86-SUP-01 through D86-SUP-08) (ACCEPTED)
- R86-NETPBM-BINARY: .NET Netpbm binary write support (P4/P5/P6) (ACCEPTED)
- R86-FODS-HARDENING: FODS exporter edge-case hardening (ACCEPTED)
- R86-FODT-HARDENING: FODT exporter edge-case hardening (ACCEPTED)
- R86-PPM-WRITE: Python write_ppm (P3 ASCII) (ACCEPTED)
- R86-PBM-PPM-DOGFOOD: PBM to PPM dogfood export using FF write_ppm (ACCEPTED)
- R86-PPM-PACKAGE: PPM added to package matrix (ACCEPTED)

## System-Healing Lane (Priority 2)
Fix any system-level defects blocking automation:
- Ensure supervisor tools compile: `python -m py_compile tools/supervisor/*.py`
- Ensure tests pass: `python -m pytest tests/supervisor/ -v --tb=short`

## Product-Advancement Lane (Priority 3)
Advance Format Factory product work:
- Commercial .NET targets: FODS, FODT, Netpbm/QOI
- FOSS/reduced targets: ZST, PBM/PGM/PPM, SYLK/DIF
- Dogfood exports:
  - FODS -> CSV/HTML table
  - FODT -> TXT/Markdown/HTML
  - QOI/Netpbm -> PPM/PGM/PBM
  - SYLK/DIF -> CSV
- Evidence is support rail, not the main product

## Evidence-Hardening Lane (Priority 4)
- Ensure evidence directory is complete and validates
- Run `python tools/supervisor/supervisor_loop.py validate-declaration --declaration <path>`

## State/Taskcard/Memory Sync Lane (Priority 5)
- Update taskcards if present
- Update state/current-state.md if changed
- Memory sync handled by supervisor after review

## Independent Verification Lane (Priority 6)
- Run all tests: `python -m pytest tests/ -v --tb=short`
- Compile check: `python -m py_compile tools/supervisor/*.py`

## Hard Prohibitions
- No git push
- No PyPI/NuGet/GitHub release publication
- No Gate 8 or Gate 11 approval
- No commercial_product_ready=true
- No paid external AI API or web automation
- No MCP activation unless already authorized
- No destructive git cleanup

## Final Evidence Declaration Requirements
At sprint end, create:
- `.local/evidences/<run_id>/evidence-declaration.yaml`
- `.local/evidences/<run_id>/evidence-manifest.yaml`
- Include all evidence artifacts, test results, and changed files
- Run `python tools/supervisor/supervisor_loop.py autonomous-cycle --declaration <path>`
