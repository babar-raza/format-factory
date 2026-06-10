# R105 Repair + Advancement Plan

## Repairs

### R105-FIX-01: Inspector :: suffix resolution (CRITICAL)
- **Root cause:** `inspect_declared_evidence.py` lines 96-110 treated `tests/...py::test_fn` as file paths, but Path resolution fails due to `::` suffix → "file not found" → tests_empty_or_stub
- **Fix:** Strip `::` suffix before resolving file path: `file_part = t.split("::")[0]`
- **Impact:** All R104 items downgraded from ACCEPTED_VERIFIED to ACCEPTED_WITH_LIMITATIONS
- **Test:** test_inspector_resolves_pytest_node_ids

### R105-FIX-02: Ledger hash failures (RESOLVED EXTERNALLY)
- **Root cause:** .NET files (FodsDocument.cs, FodtDocument.cs, NetpbmImage.cs) modified but ledger not updated
- **Status:** Resolved — ledger was updated by another stream. 686/686 supervisor tests now pass.

## Advancement

### R105-ADV-01: Comprehensive grade transition tests
- 11 new tests covering all grade paths:
  - Inspector :: resolution (3 tests)
  - Grade transitions with concrete proof (3 tests)
  - Stream identity (1 test)
  - R104 regrading simulation (1 test)
  - Ledger classification (1 test)
  - Continuation signal (1 test)
  - Materializer non-src diffs (1 test)
