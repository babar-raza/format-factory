# Rollback and Recovery Plan

## Rollback Categories

### 1. New Schemas (.supervisor/schemas/)
**Action:** Delete files.
**Risk:** None. No existing code depends on these schemas.
**Files:**
- evidence-declaration.schema.json
- evidence-manifest.schema.json
- item-grade.schema.json
- supervisor-review.schema.json
- next-work-items.schema.json
- supervisor-cycle-manifest.schema.json

### 2. New Tools (tools/supervisor/)
**Action:** Delete files.
**Risk:** None. No existing code imports these modules.
**Files:**
- evidence_declaration.py
- inspect_declared_evidence.py
- grade_declared_work.py
- generate_next_worker_prompt.py
- autonomous_cycle.py

### 3. Modified Tool (tools/supervisor/supervisor_loop.py)
**Action:** `git checkout HEAD -- tools/supervisor/supervisor_loop.py`
**Risk:** Low. New commands are additive. Legacy commands unchanged.
**Scope:** Revert docstring update and 7 new command functions.

### 4. New Tests (tests/supervisor/)
**Action:** Delete test_evidence_declaration.py.
**Risk:** None. Other test files do not import from this module.

### 5. New Docs (docs/automation/)
**Action:** Delete directory or individual files.
**Risk:** None. Documentation only.

### 6. New Reports (reports/supervisor-evidence-directory-spec/)
**Action:** Delete directory.
**Risk:** None. Report files only.

### 7. Evidence Directories (.local/)
**Action:** Delete `.local/evidences/<run_id>/` and `.local/supervisor/reviews/<run_id>/`.
**Risk:** None. Local-only, not committed.

### 8. Latest Summaries (reports/supervisor/latest-*.md)
**Action:** These are overwritten each cycle. Delete or let next cycle overwrite.
**Risk:** Low.

### 9. Policy/Config Updates (.supervisor/)
**Action:** Revert policies.yaml and config.yaml to prior commit.
**Risk:** Low. New sections are additive.

## Full Rollback Command

```bash
# Delete new files
git clean -fd .supervisor/schemas/
rm tools/supervisor/evidence_declaration.py
rm tools/supervisor/inspect_declared_evidence.py
rm tools/supervisor/grade_declared_work.py
rm tools/supervisor/generate_next_worker_prompt.py
rm tools/supervisor/autonomous_cycle.py
rm tests/supervisor/test_evidence_declaration.py
rm -rf docs/automation/
rm -rf reports/supervisor-evidence-directory-spec/

# Revert modified files
git checkout HEAD -- tools/supervisor/supervisor_loop.py
git checkout HEAD -- .supervisor/policies.yaml
git checkout HEAD -- .supervisor/config.yaml

# Clean local evidence
rm -rf .local/evidences/supervisor-evidence-directory-sprint-20260601/
rm -rf .local/evidences/synthetic-declaration-smoke-20260601/
rm -rf .local/supervisor/reviews/
```

## Partial Rollback

If only the R85 regression fixes need to be reverted:
```bash
git checkout HEAD -- tools/supervisor/validate_evidence_for_supervisor.py
git checkout HEAD -- tools/supervisor/compare_goal_to_evidence.py
git checkout HEAD -- tools/supervisor/sync_local_memory.py
```

## Recovery After Rollback

Re-run the sprint from the plan. The implementation is idempotent — all files can be recreated from the plan and schemas.
