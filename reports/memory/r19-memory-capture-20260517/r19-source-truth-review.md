# R19 Source Truth Review
**Sprint:** R19-MEMORY-CAPTURE-DEDICATED-001
**Date:** 2026-05-17

## Sources Inspected

| Source | Classification | Notes |
|--------|---------------|-------|
| `memory/00-index.md` | VERIFIED_CURRENT | Index entries stop at memory/26; entries 27-38 not listed in Files table |
| `memory/35-r18-*` | VERIFIED_HISTORICAL | R18 end state — authoritative R19 start point |
| `memory/36` | MISSING | Does not exist — to be created |
| `memory/37` | MISSING | Does not exist — R20 backfill (out of scope this sprint) |
| `memory/38-r21-*` | VERIFIED_CURRENT | R21 state — must not regress |
| `commit 2dcd7f8` | VERIFIED_HISTORICAL | R19 full commit: message, stat, file list |
| `.local/r19-bundle.zip` | VERIFIED_HISTORICAL | R19 evidence bundle exists |
| `.local/r19-metadata/` | VERIFIED_HISTORICAL | R19 bundle metadata exists |
| `tools/evidence/contracts/r19-high-throughput-acquisition-train-swarm.yaml` | VERIFIED_HISTORICAL | R19 contract exists |
| `reports/planning/r19-*.md` (12 files) | VERIFIED_HISTORICAL | All R19 decision and planning reports |
| `registry/format-registry.yaml` | VERIFIED_CURRENT | Current state reflects post-R22 gates |

## R19 Commit Details

- **Commit:** 2dcd7f869845e9c21b3de88f9776cdf9b989b74a
- **Date:** Sat May 16 13:56:52 2026 +0500
- **Author:** Babar Raza <babar.raza@aspose.com>
- **Message:** feat(acquisition): complete R19 high-throughput acquisition train (ZST G4-G7, FODP/FODG/Gnumeric/ABW G2-3, ORA deferred)

## R19 Scope (from commit message + stat)

**ZST Gates 4-7:**
- Gate 4 prototype approved (27/27 tests)
- Gate 5 waived (G-NORM-004: codec/no-DOM)
- Gate 6 oracle verified (27+1 tests)
- Gate 7 security/fuzz passed (27 tests, 5 malformed samples)

**Multi-Format Gates 2-3:**
- FODP/FODG: fast-path Gate 2 (ODF 1.3 cached) + Gate 3 corpus (3 synthetic samples each)
- Gnumeric/ABW: Gate 2 spec retrieval + Gate 3 corpus (3 synthetic samples each)

**ORA:** DEFERRED_BORDERLINE (6.8 < 7.0)
**FODS/FODT Gate 11:** Planning only (not approved)
**Evidence hygiene:** P-EVID-001 to P-EVID-004 established
**Registry:** 14 gate state transitions
**Tests:** 1181 passed, 8 skipped, 0 failed

## Contradiction Check

- memory/38 describes post-R21 state: ZST/FODP/FODG/Gnumeric/ABW at Gates 8-10 → NO CONTRADICTION (R19 was Gates 2-7 for those formats)
- memory/35 describes R18 end: ZST Gate 4 prototype_complete, multi-format Gate 1 PASSED → NO CONTRADICTION (R19 advanced from there)
- No source contradicts another

## Conclusion

All sources consistent. R19 memory/36 can be written from commit 2dcd7f8, memory/35 context, and R19 planning reports. Later R21 state (memory/38) is authoritative for post-R19 periods — memory/36 must not claim authority over R20+ events.
