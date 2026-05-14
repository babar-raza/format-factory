---
document_type: replay_governance_strengthening_report
sprint: CONWAY-R7R8-MULTI-FORMAT-PLANNING-AND-STALENESS-SWARM-001
lane: E
date: "2026-05-14"
visibility: internal
---

# Replay Governance Strengthening Report — Lane E

**REPLAY_GOVERNANCE_STATUS: COMPLETE**

- Module: `tools/skills/replay_fingerprint.py`
- Tests: `tests/skills/test_replay_fingerprint.py` (23/23 PASS)

## Fingerprint Components

| Component | Method | Stable |
|-----------|--------|--------|
| Requirements | SHA-256(sorted IDs) | YES |
| Lanes | SHA-256(sorted selected + blocked) | YES |
| Prompt | SHA-256(normalized text) | YES |
| Stale | SHA-256(verdict + checks + blocker_count) | YES |
| Plan | SHA-256(slice IDs + taskcard IDs) | YES |

## Determinism Verified

- FODS: consecutive runs produce identical fingerprints ✓
- FODT: consecutive runs produce identical fingerprints ✓
- Cross-format: FODS ≠ FODT fingerprints (correct isolation) ✓

## Replay Safety

Both FODS and FODT have `replay_safe: True`.
All fingerprints are 16-char hex (SHA-256 truncated) — JSON-serializable.
`compare_fingerprints()` produces CONSISTENT | INCONSISTENT | PARTIAL verdicts.
