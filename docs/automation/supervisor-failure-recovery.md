# Supervisor Failure Recovery

## Declaration Validation Failure (Exit 1)

**Cause:** Declaration YAML is missing, malformed, or missing required fields.

**Recovery:**
1. Check the declaration file exists at the declared path.
2. Validate YAML syntax (indentation, missing colons, etc.).
3. Check all required fields are present (see schema).
4. Fix and re-run `validate-declaration --declaration PATH`.

## Path Validation Failure (Exit 1)

**Cause:** Declared evidence_root or evidence_paths do not exist.

**Recovery:**
1. Check `evidence_root` directory exists.
2. Check each `evidence_paths` entry in every work item.
3. Create missing files or correct paths in the declaration.
4. Re-run validation.

## Critical Rework (Exit 3)

**Cause:** OVERCLAIMED or REJECTED items found during grading.

**Recovery:**
1. Read `rework-items.yaml` in the review directory.
2. For OVERCLAIMED: create the missing evidence at declared paths.
3. For REJECTED: fix the fundamentally wrong evidence.
4. Update the declaration if paths changed.
5. Re-run `autonomous-cycle --declaration PATH`.

## Unexpected Error (Exit 9)

**Cause:** Python exception during cycle execution.

**Recovery:**
1. Check the error traceback in the output.
2. Common causes: file permission errors, import failures, malformed YAML.
3. Fix the underlying issue.
4. Re-run the cycle.

## Idempotent Re-run

The autonomous cycle is idempotent. Running it again on the same declaration overwrites previous review outputs. This is safe and expected.

## Rollback Strategy

### Schemas (.supervisor/schemas/)
These are new files. Rollback = delete them. No existing functionality depends on them.

### Tools (tools/supervisor/)
- **New files** (evidence_declaration.py, inspect_declared_evidence.py, grade_declared_work.py, generate_next_worker_prompt.py, autonomous_cycle.py): Delete to rollback.
- **Modified file** (supervisor_loop.py): Revert to prior commit. The new commands are additive — legacy commands still work.

### Tests (tests/supervisor/)
- **test_evidence_declaration.py**: New file. Delete to rollback. No other tests depend on it.

### Evidence directories (.local/evidences/)
- These are local-only. Delete the run directory to rollback.

### Review outputs (.local/supervisor/reviews/)
- These are local-only. Delete the review directory to rollback.

### Reports (reports/supervisor/)
- latest-*.md files are overwritten each cycle. Prior content is in git history.

## Partial Failure

If the cycle fails partway through (e.g., grading succeeds but prompt generation fails):
1. Review outputs up to the failure point are valid.
2. Fix the failing step.
3. Re-run the full cycle (idempotent).
