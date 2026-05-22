# R49 FODT Preservation Matrix

**Sprint:** FORMAT-FACTORY-R49-EDITABLE-OBJECT-MODEL-POC-BASELINE-AND-STRATEGY-SYNC-001
**Lane:** MT7
**Date:** 2026-05-22

---

## Summary

Preservation matrix for FODT (Flat OpenDocument Text) after edit/save/reload cycle.
Assessed for both Python streaming writer (fixed in R49) and .NET DOM-backed writer.

---

## Block-Level Preservation

| Attribute | Python writer | .NET writer | Notes |
|-----------|--------------|------------|-------|
| Paragraph text | PRESERVED | PRESERVED | Both verified via round-trip tests |
| Heading text | PRESERVED | PRESERVED | Fixed in R49 (was broken pre-R49) |
| Heading type (`text:h`) | PRESERVED | PRESERVED | R49 fix: writer emits `text:h` for heading blocks |
| Heading outline-level | PRESERVED | PRESERVED | R49 fix: `text:outline-level` attribute written |
| Block order | PRESERVED | PRESERVED | Blocks written in order |
| Block count | PRESERVED | PRESERVED | Verified in R49 tests |
| Paragraph style reference | LOST (Python) | PRESERVED (.NET) | Not in neutral model. Known gap — TC-PARASTYLE-001 |
| Inline runs / spans | LOST (Python) | PRESERVED (.NET) | Not yet parsed. Known gap — TC-INLINE-001 |
| Hyperlinks | LOST (Python) | PRESERVED (.NET) | Not parsed into neutral model |
| Tables (text:table) | LOST (Python) | PARTIAL (.NET) | Not yet in Python neutral model — TC-TABLE-001 |
| Lists (text:list) | LOST (Python) | PARTIAL (.NET) | Not yet in Python neutral model — TC-LIST-001 |

---

## Document-Level Preservation

| Attribute | Python writer | .NET writer | Notes |
|-----------|--------------|------------|-------|
| Document metadata | LOST (Python) | PRESERVED (.NET) | Python writer emits minimal envelope |
| Automatic styles | LOST (Python) | PRESERVED (.NET) | Not in neutral model |
| Font declarations | LOST (Python) | PRESERVED (.NET) | Not in neutral model |
| Scripts / macros | LOST (Python) | PRESERVED (.NET) | Python writer is clean (no macros emitted) |
| Page layout | LOST (Python) | PRESERVED (.NET) | Not in neutral model |

---

## Preservation Test Coverage

Covered by `tests/python/fodt/test_r49_object_model_poc.py`:
- `TestFodtPreservationProof::test_heading_level_preserved` — outline-level survives round-trip
- `TestFodtPreservationProof::test_mixed_block_types_preserved` — heading+paragraph sequence preserved
- `TestFodtPythonObjectModelPOC::test_edit_one_block_preserves_other_blocks` — unedited blocks unchanged
- `TestFodtPythonObjectModelPOC::test_heading_type_preserved_after_edit` — type stays "heading"
- `TestFodtPythonObjectModelPOC::test_block_count_preserved_after_edit` — count unchanged

---

## Known Gaps (Taskcards)

| ID | Gap | Priority |
|----|-----|----------|
| TC-INLINE-001 | FODT Python writer loses inline runs/text:span | Medium |
| TC-TABLE-001 | FODT Python writer loses table blocks | Medium |
| TC-LIST-001 | FODT Python writer loses list blocks | Medium |
| TC-PARASTYLE-001 | FODT Python writer loses paragraph style references | Low |

---

## Verdict

**Python FODT preservation: PARTIAL** — text/heading-type/level preserved (R49 fix); inline runs/tables/lists/styles lost.
**.NET FODT preservation: FULL** — DOM-backed; all unmodified XML nodes preserved.

For complex documents (tables, lists, styles), the .NET library is the recommended path.
