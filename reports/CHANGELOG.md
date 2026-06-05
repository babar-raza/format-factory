# Changelog — Format Factory

---

## 2026-06-05 — FORMAT-FACTORY-DOTNET-DOGFOOD-ARCHITECTURE-GAP-INVESTIGATION-AND-PLANNING-001

**Verdict:** DOTNET_DOGFOOD_ARCHITECTURE_GAP_CONFIRMED_AND_ROUTED (exit 0, 18/18 ACCEPTED)

### tools/supervisor/select_poc_gaps.py (Lane F)
- Added `GAP_DOGFOOD_EXTERNAL_ARCHITECTURE_BLOCKED` to `GAP_STATUSES` set
- Added score entry `"GAP_DOGFOOD_EXTERNAL_ARCHITECTURE_BLOCKED": 40` to `ACTION_SCORE`
- Added `BLOCKED_GAP_IDS` frozenset containing 4 architecture-blocked gap IDs
- Added post-assignment reclassification guard in `_gap()` function
- py_compile PASS; 26 existing select_poc tests PASS

### tools/supervisor/generate_next_worker_prompt.py (Lane G)
- Added `BLOCKED_ARCHITECTURE_GAPS` frozenset constant (4 gap IDs)
- Added filter in G5 `actionable_dogfood` list comprehension to exclude blocked gaps
- py_compile PASS

### reports/supervisor/next-sprint.md (Lane G)
- TASK-009, 010, 011, 012 replaced with `[ARCHITECTURE_BLOCKED — DO NOT INVOKE /add-dogfood-export]`
  guardrail text including root cause, decision reference, and alternative work recommendation

### tests/supervisor/test_validate_dotnet_dogfood_architecture.py (Lane I — NEW)
- 12 regression tests validating all investigation artifacts
- All 12/12 PASS

### reports/dotnet-dogfood-architecture-gap/ (NEW — 31 files)
- Complete investigation artifact set: coordinator files, lane outputs A-K, ADR, writer library
  audit, blocked gap ledger, actionable alternatives, decision package, regression results, IV

### .local/evidences/dotnet-dogfood-architecture-gap/ (NEW)
- evidence-declaration.yaml (18 work items, 8 artifacts)
- evidence-manifest.yaml (33 files)

---

## 2026-06-01 — Prior Sprint

Date: 2026-06-01

## Changes

### tools/supervisor/autonomous_cycle.py
- Added `bridge_to_legacy_format()` function (Step 7 in cycle)
- Writes `evidence-review.json` + `contradictions.json` to `reports/supervisor/`
- Maps cycle review grades/counts to legacy JSON format

### tools/supervisor/supervisor_loop.py
- `cmd_autonomous_cycle()` now calls `cmd_next()` after cycle completes (exit 0 or 3)
- `cmd_run_on_latest()` prints deprecation warning to stderr

### tools/supervisor/evidence_declaration.py
- Added `_validate_jsonschema()` — optional runtime schema validation
- Called at top of `validate_schema()` before field-level checks

### tools/supervisor/discover_latest_evidence.py
- `main()` prints deprecation warning to stderr

### tools/supervisor/watch_for_bundle.py
- `main()` prints deprecation warning to stderr

### plans/master-plan.md
- Section 40.5 updated: `autonomous-cycle --declaration` replaces `run-on-latest --bundle`
- Section 41 added: Declaration-driven supervisor pipeline documentation

### .local/evidences/r86-real-sprint-validation/
- Created R86 evidence declaration for real-sprint validation
- Autonomous-cycle graded 7 items ACCEPTED, exit 0
- session-resume.md regenerated with R86 sprint data

## Test Commands
```bash
# Run all supervisor tests
.local/venv/Scripts/python -m pytest tests/supervisor/ -v --tb=short

# Run autonomous-cycle E2E
.local/venv/Scripts/python tools/supervisor/supervisor_loop.py autonomous-cycle \
  --declaration .local/evidences/r86-real-sprint-validation/evidence-declaration.yaml

# Verify deprecation warning
.local/venv/Scripts/python tools/supervisor/discover_latest_evidence.py --json 2>&1 | head -3
```

---

## 2026-06-05 — FORMAT-FACTORY-ROOT-README-REFRESH-PLAN-001

**Verdict:** README_REFRESH_PLAN_READY_FOR_EXECUTION (planning sprint — documentation only)

### New Files Created

**reports/readme-refresh-plan/**
- preflight.md — git state, supervisor state, constraint verification
- files-inspected.md — complete list of all files read during investigation
- current-readme-review.md — TC-001: section-by-section README gap analysis
- repo-state-map.md — TC-002: repo state with CONFIRMED/PROPOSED/UNVERIFIED markers
- repo-state-map.json — TC-002: machine-readable repo state (JSON valid)
- readme-target-outline.md — TC-003: 14-section target structure with evidence paths
- readme-content-plan.md — TC-004: per-section content plan with claims and risks
- readme-update-patch-plan.md — TC-005: FULL REPLACEMENT strategy with rollback and validation
- final-single-go-readme-update-prompt.md — TC-006: self-contained execution prompt for next agent
- validation-results.md — TC-007: 13 validation checks, self-review 57/60
- final-git-status.txt — TC-007: full git status capture
- review-package-proof.md — TC-008: review package SHA-256 and absolute path

**.local/evidences/readme-refresh-plan/**
- evidence-declaration.yaml — sprint evidence declaration (8 work items)
- evidence-manifest.yaml — artifact manifest (14 artifacts)

**reports/PLAN_SOURCES.md, PLAN_INDEX.md, TASK_BACKLOG.md** — appended new sprint rows

### Validation

- git diff -- README.md: NO CHANGES (README not edited — planning only)
- git diff -- src/: NO CHANGES
- git diff -- tests/: NO CHANGES
- git diff -- poc-targets.yaml: NO CHANGES
- All 9 output .md files: EXIST with headings
- repo-state-map.json: JSON VALID
- No commit, push, Gate approval, or external tool install
