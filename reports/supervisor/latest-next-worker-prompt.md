# Next Worker Prompt
Generated: 2026-06-01T15:07:08.873278
Previous Sprint: FORMAT-FACTORY-SUPERVISOR-EVIDENCE-DIRECTORY-EXECUTION-SPEC-AND-CONTROLLED-IMPLEMENTATION-001
Previous Verdict: ACCEPTED
Previous Run: supervisor-evidence-directory-sprint-20260601
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
- TC-SUP-DIR-001: Preflight and context reconciliation (ACCEPTED)
- TC-SUP-DIR-003: Evidence declaration schema (ACCEPTED)
- TC-SUP-DIR-004: Evidence manifest schema (ACCEPTED)
- TC-SUP-DIR-005: Declared evidence validator (ACCEPTED)
- TC-SUP-DIR-006: Declared evidence inspector (ACCEPTED)
- TC-SUP-DIR-007: Item-level grading engine (ACCEPTED)
- TC-SUP-DIR-008: Next-worker prompt generator (ACCEPTED)
- TC-SUP-DIR-009: Autonomous cycle orchestrator (ACCEPTED)
- TC-SUP-DIR-013: Tests and regression coverage (ACCEPTED)
- TC-SUP-DIR-014: Demo run with declared evidence directory (ACCEPTED)
- TC-SUP-DIR-011: Product-factory forward-work policy (ACCEPTED)
- TC-SUP-DIR-002: Plan normalization (ZIP-first to directory-first) (ACCEPTED)
- TC-SUP-DIR-010: R85 quality regression repair (ACCEPTED)
- TC-SUP-DIR-012: Memory and state sync enhancements (ACCEPTED)
- TC-SUP-DIR-015: Final evidence directory and self-declaration (ACCEPTED)

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
