# Recovery and Rollback Policy
## Sprint: FORMAT-FACTORY-EXPERT-MANUAL-SYSTEM-REVIEW-INVESTIGATE-AND-HEAL-001

**Rule:** Before any source file is edited, a rollback record must be created. No exceptions.

---

## Rollback Record Structure Per Fix

```
reports/expert-manual-system-review/fixes/<problem_id>/rollback/
  originals/<filename>           — exact copy of file before edit
  before-sha256.json             — SHA-256 of each file before edit
  rollback-instructions.md       — step-by-step restore instructions
```

---

## Rollback Rules

1. **No git reset, git clean, or git stash** — rollback via saved originals only
2. Apply reverse patch first (if diff/patch tool available)
3. If reverse patch fails: restore from `rollback/originals/<filename>`
4. Verify SHA-256 after restore matches `before-sha256.json`
5. If restore fails: set `execution-state.json current_state=UNSAFE_WORKSPACE` and stop immediately
6. After successful rollback: rerun targeted validation to confirm clean state
7. Record all rollback events in `coordinator/coordinator-log.md`

---

## Rollback Instructions Template

Each fix must write:

```
To undo fix <problem_id>:
1. Copy rollback/originals/<filename> back to <original_path>
2. Verify SHA-256 matches before-sha256.json entry for <filename>
3. Run: dotnet build <discovered_csproj_path>   (for .NET fixes)
   OR: pip install -e src/python/<package>/     (for Python fixes)
4. If build/install passes, rollback is complete.

DO NOT use git reset, git checkout, or git stash.
```

---

## UNSAFE_WORKSPACE Trigger

If rollback fails and the workspace is in an unknown state:
- Write `execution-state.json current_state=UNSAFE_WORKSPACE, terminal=false`
- Write explanation in `coordinator/coordinator-log.md`
- Stop immediately — do not apply any further fixes
- Report EXPERT_REVIEW_UNSAFE_WORKSPACE verdict

---

## Scope Constraint

- Rollback originals stored under `reports/expert-manual-system-review/fixes/` only
- Report directory changes are always safe to delete (no source files under reports/)
- Source file changes tracked in `coordinator/touched-files-ledger.jsonl`
