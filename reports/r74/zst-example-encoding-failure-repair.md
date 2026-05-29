# R74 ZST Example Encoding Failure Repair

**Sprint:** FORMAT-FACTORY-R74-R73-CLEAN-CLOSURE-VALIDATOR-HARDENING-PRODUCT-READINESS-MEGA-TRAIN-001
**Date:** 2026-05-29
**Train:** D

---

## Root Cause

File: `examples/python/zst/compress_decompress_file.py`

Lines 41, 45, 70, 72 contained `→` (U+2192 RIGHTWARDS ARROW), which cannot be encoded
by Windows cp1252. When the test runner captures subprocess stdout with `text=True` (using
the default system encoding), the print statements failed with:

```
UnicodeEncodeError: 'charmap' codec can't encode character '\u2192' in position N: character maps to <undefined>
```

Test: `tests/examples/test_python_examples_smoke.py::test_zst_example_runs_without_crash`

This test ran the example as a subprocess and asserted `returncode == 0`. The return code
was non-zero due to the UnicodeEncodeError.

---

## Fix

Replaced all 4 occurrences of `→` with ASCII `->`:

```diff
-    print(f"  → {len(compressed)} bytes compressed")
+    print(f"  -> {len(compressed)} bytes compressed")
-    print(f"  → {len(decompressed)} bytes decompressed (round-trip OK)")
+    print(f"  -> {len(decompressed)} bytes decompressed (round-trip OK)")
-        print(f"  → VALID: {valid}")
+        print(f"  -> VALID: {valid}")
-        print(f"  → Error: {e}")
+        print(f"  -> Error: {e}")
```

---

## Test Result

`tests/examples/test_python_examples_smoke.py::test_zst_example_runs_without_crash` → PASS

---

## Encoding Safety Policy

All example scripts must use ASCII-safe characters in print statements.
Unicode decorators in output are NOT acceptable for cross-platform scripts.
The test `test_python_examples_smoke.py` already enforces this via subprocess runs,
which will catch any future encoding regressions on Windows cp1252.

ZST_ENCODING_FIX: PASS
