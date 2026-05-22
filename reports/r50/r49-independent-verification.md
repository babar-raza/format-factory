# R50 — R49 Independent Verification

**Sprint:** FORMAT-FACTORY-R50-EVIDENCE-CLOSEOUT-AND-OBJECT-MODEL-HARDENING-001
**Lane:** 1A
**Date:** 2026-05-22

---

## R49 Corrected Status

**R49_EDITABLE_OBJECT_MODEL_POC_REAL_BUT_CLOSEOUT_EVIDENCE_STALE**

R49 is NOT discarded. Real product progress is preserved. Evidence caveats documented and corrected in R50.

---

## Claim-by-Claim Classification

| Claim | Classification | Evidence |
|-------|---------------|----------|
| FODS Python object-model edit/save/reload POC works | VERIFIED | 13 tests pass from src; installed-wheel confirmed in R49 |
| FODT Python parser/writer schema mismatch fixed | VERIFIED | writer.py accepts blocks key + text:h; 12 tests pass |
| FODT writer emits text:h with outline-level | VERIFIED | test_r49_object_model_poc.py TestFodtWriterBlocksKeyFix |
| FODS/FODT Python wheels install and smoke works | VERIFIED | version/track/commercial_ready from installed wheel |
| FODS typed-value roundtrip improved | VERIFIED | test_r48_writer_typed_values.py (inherited) |
| FODS .NET object-model POC (Load/SetText/Save/Reload) | VERIFIED | run_dotnet_object_model_poc.py PASS in R49 environment; rerun confirmed |
| FODT .NET object-model POC (Load/SetText/Save/Reload) | VERIFIED | run_dotnet_object_model_poc.py PASS in R49 environment; rerun confirmed |
| Memory entry 57 created | VERIFIED | memory/57-r49-object-model-edit-save-export-ai-acceleration-20260522.md exists |
| Product strategy doc created | VERIFIED | docs/product-object-model-edit-save-export-strategy.md exists |
| AI usage ledger NO_LIVE_AI_CALLS | VERIFIED | reports/r49/ai-usage-ledger.jsonl line 1 confirms zero calls |
| Export-format ranking doc created | VERIFIED | reports/r49/export-format-acquisition-ranking.md exists |
| Phase Audit 3 expanded to ZST/ODS/ODT | VERIFIED_CONDITIONAL | reports/r49/phase-audit/phase-03-expansion.md; CONDITIONAL_PASS only |
| ZST Python local RC wheel built + smoke | VERIFIED | SHA 328561e7... confirmed; smoke PASS |
| Final proof file fully resolved | FALSE | bundle-metadata proof has "(computed after pass 2 build)" x4 + "pass 2 SHA to follow" |
| Artifact manifest hashes correct | FALSE | 3/5 hashes mismatch actual ZIP bytes (FODT wheel, FODS nupkg, FODT nupkg) |
| Validation command log freshness | FALSE | log contained STATE_SNAPSHOT pre-final result as final |
| Preservation gap taskcards exist | FALSE | TC-FORMULA-001..TC-PARASTYLE-001 referenced in prose only; no taskcard files |
| Sdist in Python artifact set | FALSE | only .whl files; no .tar.gz in manifest; policy not explicit |

---

## Supersession

R49 is superseded by R50 for evidence closure only.
R49 product code and test progress is ACCEPTED and NOT re-implemented.

Previous R49 verdict: `R49_EDITABLE_OBJECT_MODEL_POC_BASELINE_COMPLETE` — SUPERSEDED
R50 reclassification: `R49_EDITABLE_OBJECT_MODEL_POC_REAL_BUT_CLOSEOUT_EVIDENCE_STALE`

---

## Root Causes

1. **Stale proof patterns** — validator PROOF_FILE_PLACEHOLDER_PATTERNS did not include `"computed after pass 2 build"`, `"pass 2 SHA to follow"`, `"Entries: (computed"`, `"Size: (computed"`, `"Validation: (computed"`.
2. **Manifest hash truncation** — hashes generated from `sha256[:32]` prefix display, not full 64-char hex.
3. **YAML `sha256:` not parsed** — validator text parser matched `SHA-256:` only.
4. **Pre-final state logged** — state snapshot run before final verdict was included in final metadata.
5. **Taskcard IDs in prose only** — gap IDs invented in preservation matrix without corresponding files.

---

## Corrective Actions in R50

1. Extend PROOF_FILE_PLACEHOLDER_PATTERNS with all R49 missed patterns (Lane 1B).
2. Rebuild artifact manifest from actual file bytes (Lane 2B).
3. Fix validator to parse lowercase YAML `sha256:` (Lane 1C).
4. Refresh validation command log after final state (Lane 1D).
5. Create actual taskcard files for all preservation gaps (Lane 3C).
6. Document Python artifact policy (Lane 2A).
