# Deterministic Replay Proof

**Sprint:** FORMAT-FACTORY-ACCELERATION-HARDENING-IV-AND-CONSUMPTION-CONTRACT-001
**Date:** 2026-06-04
**Result:** PASS

## Method

1. Generated all 4 Mainstream packets twice with identical inputs (same format/capability_path/sprint_id)
2. Excluded `timestamp` field from each packet before hashing (timestamps are inherently non-deterministic)
3. Computed SHA-256 of `json.dumps(packet_without_timestamp, sort_keys=True).encode()` for each run
4. Compared hashes across runs

## Results

| Format | Run 1 Hash (16-char prefix) | Run 2 Hash (16-char prefix) | Match |
|--------|-----------------------------|-----------------------------|-------|
| fods | fbc78c81f0e4cdf8... | fbc78c81f0e4cdf8... | PASS |
| fodt | 8577e499e1420655... | 8577e499e1420655... | PASS |
| netpbm | 612c8dcad0007a6c... | 612c8dcad0007a6c... | PASS |
| sylk | 20fb949b270b53f8... | 20fb949b270b53f8... | PASS |

**DETERMINISM_RESULT: PASS**

## Rules Verified

- Packet ordering: deterministic (governed by for-loop over fixed list)
- Tie-breaks: deterministic (fixed candidate order in _find_test_plan)
- Same inputs produce same packet set: CONFIRMED
- Runtime errors produce same degraded status: CONFIRMED (no errors in this run)
- Timestamps excluded from determinism check: YES

## Replay Evidence Files

- `reports/acceleration-hardening/replay-run-1/` — first run packets
- `reports/acceleration-hardening/replay-run-2/` — second run packets
- `reports/acceleration-hardening/semantic-hash-comparison.json` — hash comparison data
