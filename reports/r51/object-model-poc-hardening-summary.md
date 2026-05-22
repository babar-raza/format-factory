# R51 Object-Model POC Hardening Summary

**Sprint:** FORMAT-FACTORY-R51-INSTALLED-ARTIFACT-BASELINE-AND-AI-ACCELERATION-001
**Run:** R51
**Date:** 2026-05-22

---

## Status

`R51_OBJECT_MODEL_INSTALLED_WHEEL_PROVEN`

R50 added object-model POC for load/edit/save/reload in source form. R51 proves the same from **installed wheel artifacts**, not just source.

---

## FODS Python (Installed Wheel)

| Test | Result |
|------|--------|
| Install from bundled wheel | PASS |
| `from fods.csv_exporter import export_fods_to_csv` | PASS |
| Load sample FODS | PASS |
| Edit cell [0][0] (10.0 → 'EDITED_R51') | PASS |
| Save to temp file | PASS |
| Reload and verify edited value | PASS |
| CSV export from reloaded workbook | PASS |

**Result:** `FODS_PYTHON_INSTALLED_WHEEL_OBJECT_MODEL_EDIT_SAVE_RELOAD_CSV_PASS`

---

## FODT Python (Installed Wheel)

| Test | Result |
|------|--------|
| Install from bundled wheel | PASS |
| Load sample FODT | PASS (7 blocks) |
| Edit first paragraph block | PASS (→ 'EDITED_R51_FODT') |
| Save to temp file | PASS |
| Reload and find edited value | PASS |

**Result:** `FODT_PYTHON_INSTALLED_WHEEL_OBJECT_MODEL_EDIT_SAVE_RELOAD_PASS`

---

## FODS .NET (From Bundled nupkg)

| Test | Result |
|------|--------|
| Pack FODS nupkg | PASS (sha256=1f81b3cf...) |
| Run POC from artifacts dir | FODS_DOTNET_OBJECT_MODEL_EDIT_SAVE_RELOAD_PASS |

**Result:** `FODS_DOTNET_OBJECT_MODEL_EDIT_SAVE_RELOAD_PASS`

---

## FODT .NET (From Bundled nupkg)

| Test | Result |
|------|--------|
| Pack FODT nupkg | PASS (sha256=a9b2426d...) |
| Run POC from artifacts dir | FODT_DOTNET_OBJECT_MODEL_EDIT_SAVE_RELOAD_PASS |

**Result:** `FODT_DOTNET_OBJECT_MODEL_EDIT_SAVE_RELOAD_PASS`

---

## Preservation Gaps (Outstanding)

The following are known gaps from TC taskcards — not yet implemented:

| Gap | Taskcard | Priority |
|-----|----------|----------|
| Formula cells lose formula on write | TC-0054 | HIGHEST (AI confirmed, data integrity) |
| Style metadata preservation FODS | TC-0055 | HIGH |
| Column definitions preservation FODS | TC-0056 | MEDIUM |
| Inline spans lost on FODT write | TC-0057 | HIGH |
| Table preservation FODT | TC-0058 | HIGH |
| List preservation FODT | TC-0059 | HIGH |
| Paragraph style FODT | TC-0060 | MEDIUM |

All gaps are taskcardentered and acknowledged. Python object-model is `alpha-foss-preview` tier.

---

## Object-Model Strategy

Per `docs/product-object-model-edit-save-export-strategy.md`:
- Python track: streaming write, partial preservation (FODS/FODT)
- .NET track: full DOM-backed, high fidelity
- Formula preservation is next implementation milestone (TC-0054)
