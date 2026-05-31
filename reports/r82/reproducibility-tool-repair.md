# R82 Train F — Reproducibility Tool Repair

## Problem (D79-07)
`tools/repro/reproduce_format.py` used wrong import namespaces:
- `from aspose_format_factory_fods import ...` → WRONG
- `from aspose_format_factory_fodt import ...` → WRONG
- `from aspose_format_factory_zst import ...` → WRONG

FODT smoke script also used stale doc structure:
- `doc = {"body": {"blocks": []}}` → WRONG (pre-GAP-FODT-STRUCT-001-fix)

## Fix Applied
Canonical namespace table added to tool:
- `fods` → `import fods`
- `fodt` → `import fodt`
- `zst` → `import zst`

FODT smoke script updated:
- `doc = {"blocks": []}` (root-level blocks, GAP-FODT-STRUCT-001 compliant)

New CLI options added:
- `--package-artifacts-dir` — auto-discover wheel from directory
- `--no-network` — install from local artifacts only
- `--require-wheel` — fail (not skip) if wheel absent

## Verification
The fix is in `tools/repro/reproduce_format.py`.
New tests added in `tests/repro/test_r82_reproduce_format_import_names.py`.

REPRODUCIBILITY_TOOL_REPAIR: COMPLETE
