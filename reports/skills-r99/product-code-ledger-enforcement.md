# Train G: Product-Code Ledger Enforcement Report
Sprint: FORMAT-FACTORY-SKILLS-R99-SKILL-REGISTRY-GOVERNED-EXECUTION-PARALLEL-MEGA-TRAIN-001
Date: 2026-06-03

## Validator Hardening

### New Checks Added

1. **BACKFILLED_PRE_GOVERNANCE rejection for post-R90 sprints**: Any entry with sprint >= R90 that uses BACKFILLED_PRE_GOVERNANCE classification is now rejected. This prevents workers from backdating governance compliance.

2. **Improved error messages**: Invalid source states now show the valid options in the error message.

3. **State validation**: Only "present" and "deleted" are valid source_file states. The R98 ledger entry used "modified" which is now properly rejected.

### Existing Checks (confirmed working)

| Check | Status |
|-------|--------|
| Duplicate entry_id detection | PASS |
| Missing entry_id | PASS |
| Invalid classification | PASS |
| Empty capability_refs | PASS |
| Empty api_symbols | PASS |
| Empty source_files | PASS |
| Non-src paths | PASS |
| Invalid source state | PASS (catches "modified") |
| Missing SHA-256 | PASS |
| Unledgered src change | PASS |
| Stale SHA-256 hash | PASS |
| Deleted file without deletion reference | PASS |

### Current Ledger Status

```
PRODUCT_CODE_LEDGER: FAIL
  ERROR: R98 "modified" state (pre-existing bug from R98 sprint)
  ERROR: 4 stale SHA-256 hashes (uncommitted R94-R98 changes)
  changed_src_files: 6
```

Note: These are pre-existing issues from the mainstream product sprints (R94-R98), not introduced by Skills R99. The validator correctly detects them.

### Enforcement Rules

1. No new `src/*` edit without a ledger entry and transcript
2. `BACKFILLED_PRE_GOVERNANCE` cannot be used for sprints >= R90
3. Ledger without transcript is a warning for new governed work
4. Every `GOVERNED_PRODUCT_CHANGE` entry must reference a skill or handoff
5. Source state must be "present" or "deleted" (not "modified" or other values)
