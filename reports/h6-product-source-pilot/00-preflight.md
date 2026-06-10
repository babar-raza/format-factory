# Sprint 8 Preflight — FORMAT-FACTORY-H6-QUEUE-DRIVEN-PRODUCT-SOURCE-PILOT-001

## Package 114 Baseline

- **Package 113 SHA-256**: `c8823920925e6d6f4022cddef4c04e6d821f41effd34d0b5f50ae424988229ee`
- **Package 113 verdict**: `COMPLETE_QUEUE_DRIVEN_H6_MULTI_ACTION_PROVEN`
- **Package 113 tests**: 138 pass / 0 fail
- **Baseline git HEAD**: f76d845bd3b1d61d53619fadd0f5a34a1832c8d1

## Sprint 8 Objective

Execute one bounded real product-source change through the durable action queue:
- Select a safe, bounded product-source task from the real repo state
- Extend product action guard for bounded source mutation (PRODUCT_SOURCE_PATCH_BOUNDED)
- Execute via queue-first orchestrator
- Verify no regressions; capture diff + rollback instructions

## Known Caveats from Sprint 7

- **Queue count inconsistency**: IV reports 4 items consumed; queue-consumption-result.json lists 3 (h6-q-002 missing)
- **Null action_type item**: `c31d2171` has `action_type=null` — must be quarantined/removed
- **Unsafe next-work wording**: `next-sprint-taskmaster.json` contains "Execute git commit" — must remain external-gate only
- **0 product gaps classified**: `poc-targets.yaml` has `gap_ids=null` on all targets (file at product-capability-matrix/poc-targets.yaml not repo root)
- **anti-skip caveats**: missing_sample_outputs, missing_raw_logs (non-blocking for pipeline work)

## Selected Product Task

**Task**: Add `probe_abw(path)` format-detection function to `src/python/abw/abw_codec.py`

**Rationale**:
- Bounded (1 function, ~20 lines)
- No new dependencies
- Genuinely useful capability (format detection without full parse)
- Reversible (delete function + revert __init__.py export)
- No structural change to existing code

## Lane Claims

See `lane-claims.json`

## Hard Rules

- No git commit, no git push, no Gate approval
- No MCP activation changes
- No destructive git operations
- Product source change limited to: `src/python/abw/abw_codec.py` + `src/python/abw/__init__.py`
