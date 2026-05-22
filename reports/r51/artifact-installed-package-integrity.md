# R51 Artifact + Installed Package Integrity

**Sprint:** FORMAT-FACTORY-R51-INSTALLED-ARTIFACT-BASELINE-AND-AI-ACCELERATION-001
**Run:** R51
**Date:** 2026-05-22

---

## Python Artifact Rebuild (R51)

R50 defect: FODS wheel built before `csv_exporter.py` was added — wheel lacked the new API.
R51 fix: All 3 Python wheels + sdists rebuilt after source changes.

### Package Artifacts (R51)

| Artifact | SHA-256 | Size | Status |
|----------|---------|------|--------|
| aspose_format_factory_fods-0.1.0.dev0-py3-none-any.whl | 7ffdb7d9cc0062c6287382671602c9585edd8cd1aa12d722dcb0bb2e182c24df | 14,525 B | NEW (includes csv_exporter.py) |
| aspose_format_factory_fods-0.1.0.dev0.tar.gz | 7d01b0cadaf2b48e6db51982505db329d4a64e23138b54bcd657492fc02e8468 | 1,252,980 B | NEW sdist |
| aspose_format_factory_fodt-0.1.0.dev0-py3-none-any.whl | 33cd5a3cae3a06004474450bc80e264120244751415d7657c6733a75cba646b1 | 14,602 B | UNCHANGED (no source changes) |
| aspose_format_factory_fodt-0.1.0.dev0.tar.gz | 548412c9cf8e6b3df8c74fd8a27f67ede88df8ce921cb4d8ea995eaec491ae50 | 1,400,806 B | NEW sdist |
| aspose_format_factory_zst-0.1.0.dev0-py3-none-any.whl | 328561e74bd7f89bf7743e429065ee12232b3d61ec6eb1373ebe02766be0c8e0 | 9,780 B | UNCHANGED |
| aspose_format_factory_zst-0.1.0.dev0.tar.gz | 180da7768d9a7246af366e463d2a5f138103ca902ebf9f2edbb29745811e36b9 | 9,704 B | NEW sdist |
| FormatFactory.Fods.0.1.0-tier0.nupkg | 1f81b3cf6d90cefd4deb3d91fd070347e168c854550f9593299a79ee2ea62a58 | 14,617 B | R51 fresh build |
| FormatFactory.Fodt.0.1.0-tier0.nupkg | a9b2426daa925f8e0ac751a7483c516ef96ff0648f9236b7e15c2e91a367a2dc | 13,670 B | R51 fresh build |

### FODS Wheel Content Verification

R50 FODS wheel contents (sha256=f5e89b3c...):
```
fods/README.md, fods/__init__.py, fods/constants.py, fods/exceptions.py,
fods/neutral_model.py, fods/parser.py, fods/writer.py
```
❌ MISSING: fods/csv_exporter.py

R51 FODS wheel contents (sha256=7ffdb7d9...):
```
fods/README.md, fods/__init__.py, fods/constants.py, fods/csv_exporter.py,
fods/exceptions.py, fods/neutral_model.py, fods/parser.py, fods/writer.py
```
✅ CONTAINS: fods/csv_exporter.py

### Python sdist Policy (Lane 2B)

**Decision:** For the local RC / object-model POC tier, sdists MUST be included alongside wheels.

Rationale:
- Source distributions allow inspection of full Python source without wheel extraction
- Local RC claims must include source proof, not just wheel bytes
- All 3 packages (FODS, FODT, ZST) include sdists in R51

Policy documented: local RC requires wheel + sdist for FODS/FODT/ZST.
Other formats (FODP/FODG/Gnumeric/ABW) remain wheel-only until they reach RC stage.

---

## Installed-Wheel Smoke Tests (Lane 2C / Lane 3A)

All tests run from a clean venv with ONLY the bundled wheel installed.

### FODS Installed-Wheel Tests

```
FODS_PYTHON_INSTALLED_WHEEL_CSV_EXPORT_PASS
  - Constructed workbook, exported to CSV
  - Verified RFC 4180 CRLF output: 'Name,Score\r\nAlice,95\r\nBob,87\r\n'

FODS_PYTHON_INSTALLED_WHEEL_OBJECT_MODEL_EDIT_SAVE_RELOAD_CSV_PASS
  - Parsed sample FODS
  - Edited cell [0][0]: 10.0 -> 'EDITED_R51'
  - Saved, reloaded, verified 'EDITED_R51' in reload
  - CSV export contained 'EDITED_R51'
```

### FODT Installed-Wheel Tests

```
FODT_PYTHON_INSTALLED_WHEEL_OBJECT_MODEL_EDIT_SAVE_RELOAD_PASS
  - Parsed sample FODT (7 blocks)
  - Edited first paragraph block: text -> 'EDITED_R51_FODT'
  - Saved, reloaded, verified 'EDITED_R51_FODT' found in blocks
```

---

## .NET Object-Model POC (Lane 4A)

Replayed from R51 artifacts (`FormatFactory.Fods.0.1.0-tier0.nupkg`, `FormatFactory.Fodt.0.1.0-tier0.nupkg`).

```
FODS_DOTNET_OBJECT_MODEL_EDIT_SAVE_RELOAD_PASS
FODT_DOTNET_OBJECT_MODEL_EDIT_SAVE_RELOAD_PASS
R49_DOTNET_OBJECT_MODEL_POC: PASS
```

---

## Summary

| Item | R50 Status | R51 Status |
|------|-----------|-----------|
| FODS wheel has csv_exporter.py | FALSE | PASS |
| FODS installed-wheel CSV export | FALSE | FODS_PYTHON_INSTALLED_WHEEL_CSV_EXPORT_PASS |
| FODS installed-wheel edit/save/reload | NOT_TESTED | PASS |
| FODT installed-wheel edit/save/reload | NOT_TESTED | PASS |
| Python sdists in bundle | MISSING | INCLUDED (FODS/FODT/ZST) |
| .NET POC from fresh artifacts | NOT_LOGGED | FODS+FODT PASS |
