<!--plan_identity:
  schema_version: "1.1"
  plan_id: "csvr118-dotnet-failure-tracking-hardening"
  mission_id: "DOTNET-FAILURE-TRACKING-HEAL-001"
  plan_type: "hardening_addendum"
  created_at: "2026-06-28"
  status: "COMPLETE"
-->

# CsvR118 Fix + .NET Failure Tracking System Healing
**Plan:** csvr118-dotnet-failure-tracking-hardening
**Mission:** Fix 2 pre-existing CsvR118 test failures, log them, and heal .NET failure tracking gap
**Created:** 2026-06-28

---

## Root Cause Analysis

### CsvR118 Test Failures (2 tests)

1. **`GetColumn_ByIndex_NegativeIndex_ThrowsArgumentOutOfRange`** (line 72):
   - Test expects `ArgumentOutOfRangeException`
   - Source (`CsvDocument.cs:121`) throws `CsvReaderException("Column index must be non-negative.")`
   - Fix: Change source to throw `ArgumentOutOfRangeException` (standard .NET convention for invalid index args)

2. **`GetColumn_ByName_MissingHeader_ThrowsOrEmpty`** (lines 108-121):
   - Test catches `ArgumentException || KeyNotFoundException`
   - Source (`CsvDocument.cs:130`) throws `CsvReaderException("Header 'X' not found.")`
   - Fix: Change source to throw `KeyNotFoundException` (standard .NET convention for missing key lookup)

### Why These Were Never Logged

- `registry/known-failure-ledger.yaml` has ZERO .NET test entries (only Python/supervisor tests)
- `tools/test_runner.py` has ZERO references to dotnet/xunit/FormatFactory — the entire .NET test subsystem is absent
- Sprint closeout pipeline only runs Python tests; .NET test failures are invisible to governance

---

## Taskcard Register

### TC-FIX-001: Fix CsvDocument.GetColumn exception types

```yaml
taskcard_id: TC-FIX-001
title: Fix CsvDocument.GetColumn to throw standard .NET exceptions
status: completed_verified
priority: HIGH

required_implementation:
  - CsvDocument.cs:121: Change CsvReaderException to ArgumentOutOfRangeException(nameof(index))
  - CsvDocument.cs:128: Change CsvReaderException to InvalidOperationException (no headers)
  - CsvDocument.cs:130: Change CsvReaderException to KeyNotFoundException

required_verification:
  - dotnet test tests/net/csv/ --filter CsvR118 -- 0 failures
  - dotnet test tests/net/csv/ -- no regressions in other tests

acceptance_criteria:
  - CsvR118GetColumnTests all pass
  - No new test failures introduced

machine_state: OPEN
```

### TC-FIX-002: Log CsvR118 failures in known-failure-ledger.yaml

```yaml
taskcard_id: TC-FIX-002
title: Add .NET test failure entries to known-failure-ledger.yaml
status: completed_verified
priority: HIGH

required_implementation:
  - Add 2 entries for the CsvR118 failures with category=exception_type_mismatch
  - Mark them as resolved_by=TC-FIX-001

acceptance_criteria:
  - known-failure-ledger.yaml has .NET entries
  - Entries reference the fix commit

machine_state: OPEN
```

### TC-HEAL-001: Root cause — .NET test failure detection absent from sprint closeout

```yaml
taskcard_id: TC-HEAL-001
title: Add .NET test failure detection to known-failure-ledger
status: completed_verified
priority: MEDIUM

root_cause: >
  tools/test_runner.py has no .NET/dotnet/xunit/FormatFactory references.
  Sprint closeout only runs Python pytest. .NET failures are invisible.
  known-failure-ledger.yaml schema only covers Python test paths.

required_implementation:
  - Add .NET section to known-failure-ledger.yaml schema (dotnet_known_failures)
  - Document the .NET detection gap in the ledger header

acceptance_criteria:
  - known-failure-ledger.yaml schema supports .NET test entries
  - Gap is documented for future automation

machine_state: OPEN
```

---

## Execution Order

1. TC-FIX-001 first (fix source code)
2. TC-FIX-002 second (log the failures + resolution)
3. TC-HEAL-001 third (document the systemic gap)

---
