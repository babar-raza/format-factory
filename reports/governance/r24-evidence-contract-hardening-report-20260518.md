# R24 Evidence Contract Hardening Report
# Sprint: FORMAT-FACTORY-R24-PARALLEL-CLOSURE-REPAIR-FORWARD-TRAIN-AND-AI-PLATFORM-PLAN-001
# Date: 2026-05-18
# Gate: 5 — Evidence contract hardening
# Lane: G

## Purpose

This report documents the hardening of evidence contracts and validation tooling
to prevent R23-class closure defects from recurring in future sprints.

## R23 Closure Defects (Classified and Repaired)

| Defect | Classification | Root Cause | Repair |
|--------|---------------|------------|--------|
| No final commit in git-log | EVIDENCE DEFECT | R23 closed in dirty state | R23 committed (b341d0d) before final bundle |
| git-status-final shows dirty | EVIDENCE DEFECT | Builder ran against dirty repo | Used .local/ metadata dir for bundle build |
| `emergency_blocker_bundle: true` | CONTRACT DEFECT | Exception mode used for pre-commit bundle | Closure contract uses `false` |
| `require_clean_git: false` bypasses check? | MISUNDERSTANDING | `require_clean_git: false` only bypasses "no file" warning | Documented; check still enforced |
| Package artifacts not proven | EVIDENCE GAP | .local/ gitignored, no manifest committed | Package artifact proof reports committed |

## New Test: test_final_bundle_closure_rules.py

**File:** tests/evidence/test_final_bundle_closure_rules.py
**Tests:** 16 tests / 16 PASS

### Rules Enforced

| Rule | Test Class | Tests |
|------|------------|-------|
| Dirty git-status always FAIL (unless emergency_blocker) | TestDirtyGitStatusFails | 5 |
| emergency_blocker_bundle=true allows dirty (not for final closure) | TestEmergencyBlockerBundle | 2 |
| Stale IN_PROGRESS with --check-no-pending FAIL | TestInProgressStaleStatus | 2 |
| Missing AUTHORITATIVE_TEST_RESULT FAIL | TestAuthoritativeTestResult | 2 |
| PENDING bundle validation marker FAIL | TestPendingBundleValidation | 1 |
| Closure contradiction FAIL | TestClosureContradiction | 1 |
| Metadata floor enforcement | TestMetadataFloor | 3 |

### Critical Rule Verified (R23 lesson)

```python
def test_require_clean_git_false_does_not_bypass_dirty_check(self, tmp_path):
    """require_clean_git: false only suppresses 'no git status file found' warning.
    It does NOT bypass the check when git-status-final.txt is present and dirty.
    This is the key invariant violated in the R23 pre-commit emergency bundle."""
    contract = _make_contract(tmp_path, require_clean_git="false")
    bundle = _make_bundle(tmp_path, git_status=_DIRTY_STATUS)
    result = validate_bundle(str(contract), str(bundle))
    assert result is False
```

## Evidence Contract Best Practices (Post-Hardening)

Based on R23 closure repair, these practices are now enforced by tests:

### DO
- Use a `.local/` (gitignored) metadata directory as `--metadata-dir` for bundle builds
- Commit all sprint files before building the final evidence bundle
- Set `emergency_blocker_bundle: false` in final closure contracts
- Include `AUTHORITATIVE_TEST_RESULT` in at least one metadata file
- Include `git-status-final.txt` showing "nothing to commit, working tree clean"
- Set `min_metadata_count >= 30` (RUN_CONTRACT_METADATA_FLOOR)
- Use `--check-no-pending` on the validator for final closure bundles

### DO NOT
- Use `emergency_blocker_bundle: true` for final closure contracts
- Rely on `require_clean_git: false` to bypass dirty-git checks
- Leave IN_PROGRESS gate status in final bundle metadata
- Omit AUTHORITATIVE_TEST_RESULT
- Build bundle from a committed metadata directory (builder overwrites files)
- Set `min_metadata_count` below 30 in run-specific contracts

## Evidence Contract Hardening: Key Insight on .local/ Metadata

The R23 closure sprint discovered that the bundle builder (`build_evidence_bundle.py`)
auto-updates several metadata files (git-status-final.txt, git-log.txt, bundle-manifest.yaml,
repo-tree.txt, metadata-identity-report.md) during the build process. If these files are
tracked by git (in `reports/r23-sprint-metadata-*/`), the builder modifies them and creates
dirty state, making the NEXT run of the validator fail.

**Solution:** Use a `.local/` copy of the metadata directory for bundle builds.
- Copy: `cp -r reports/r23-sprint-metadata-20260517/ .local/r23-closure-metadata-20260518/`
- Build: `--metadata-dir .local/r23-closure-metadata-20260518`
- The builder's side effects go to the gitignored `.local/` directory
- Git stays clean throughout the bundle build

This pattern must be followed for all future sprint bundles.

## Gate 5 Decision

| Check | Status |
|-------|--------|
| test_final_bundle_closure_rules.py created | DONE |
| All 16 tests pass | DONE |
| Evidence contract best practices documented | DONE |
| .local/ metadata pattern documented | DONE |

**Gate 5 — PASS**
**Lane G — Evidence Contract Hardening: COMPLETE**
