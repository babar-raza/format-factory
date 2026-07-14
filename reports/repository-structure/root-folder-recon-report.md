# Root Folder Reconnaissance Report — Production-Grade Redesign

**Plan:** playful-discovering-thunder
**Mission:** ROOT-RECON-001
**Date:** 2026-07-11
**Status:** COMPLETE

---

## Executive Summary

Root Folder Reconnaissance (TC-RR-001 through TC-RR-012) confirmed four root causes of
governance drift and implemented all eight change sets (C1-C8). V91 now surfaces 54 WARN
items (0 FAIL) on the real repo — all actionable, none sprint-blocking.

---

## Investigation Findings (TC-RR-001)

### state/ folder — DECISION_B (active producer found)

- Producer: `tools/state/state_snapshot.py` writes `state/current-state.{json,md}`
- Readers: `check_repo_invariants.py` (INV-002, INV-011) reads these files as invariants
- Content: stale sprint-R98 snapshot of 25 formats, gate summary, production blockers
- Resolution: Files moved to `.supervisor/state/`. Producer default redirected.
  INV-002/011 paths updated. `git rm -r state/` executed.

### DELETED registry entries on disk

| Entry | On Disk | Resolution |
|---|---|---|
| state/ | YES | Resolved (TC-RR-002) |
| skills/ | NO | No action needed |
| examples-docs-readiness/ | NO | No action needed |

---

## Changes Applied (C1-C8)

**C1** — V91 resurrection severity WARN -> FAIL. Test updated to assert FAIL+blocks_sprint=True.

**C2** — state/ deleted: producer redirected to .supervisor/state/, INV-002/011 paths updated,
git rm -r state/, registry entry marked deleted_executed: true.

**C3** — _check_source_test_parity() added to V91. In-memory check: src/python/<fmt>/ must
have tests/python/<fmt>/. No external file needed. 21 FORMAT_COVERAGE_GAP WARNs on real repo.

**C4** — _check_readme_content_floor() added to V91. Checks size >= 200 bytes, purpose
statement, producer declaration, actionable guidance. WARN-only. 16 WARNs on real repo.

**C5** — tools/supervisor/check_new_root_dirs.py created. Pre-commit check: reads git staging
area, detects unregistered top-level dirs. Fail-open when yaml unavailable.

**C6** — _check_registry_producer_integrity() added to V91. WARNs when all producers are
non-verifiable strings. 17 WARNs on real repo.

**C7** — Agent Navigation sections added to: src/README.md, tests/_readme.md, tools/_readme.md,
registry/README.md, plans/README.md, reports/_readme.md.

**C8** — This formal recon report (reports/repository-structure/root-folder-recon-report.md).

---

## Final V91 State

Result: WARN | blocks_sprint: False | FAIL items: 0 | WARN items: 54
  format_coverage_gap: 21 | readme_floor_fail: 16 | registry_producer_integrity: 17

Pre-change: state/ WARN tolerated in tests. Format coverage: silently skipped.
Post-change: resurrection = FAIL (sprint blocking). New WARNs surface real governance debt.

---

## Test Suite

14/14 PASS in tests/supervisor/test_validate_root_structure.py
  7 original tests (updated) + 7 new tests for C3/C4/C6 functions.

---

## Files Changed

tools/state/state_snapshot.py | default output-dir: state -> .supervisor/state
tools/evidence/check_repo_invariants.py | INV-002/011 paths: state/ -> .supervisor/state/
tools/supervisor/governance_validators_root_struct.py | C1/C3/C4/C6 helpers added
tools/supervisor/check_new_root_dirs.py | NEW (C5)
.pre-commit-config.yaml | check-root-dirs hook added (C5)
registry/repository-root-folders.yaml | state/ marked deleted_executed: true
tests/supervisor/test_validate_root_structure.py | 7 updated + 7 new tests
src/README.md | Agent Navigation added
tests/_readme.md | Agent Navigation added
tools/_readme.md | Agent Navigation added
registry/README.md | Agent Navigation added
plans/README.md | Agent Navigation added
reports/_readme.md | Agent Navigation added
