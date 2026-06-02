---
sprint: R91
generated_by: r91-worker
---

# R91 Mainstream Product Work Plan

## Overview

All product changes go through governed skills from `.supervisor/skill-registry.yaml`. No ad-hoc edits outside skill invocations.

## Work Items

### WI-G: FODS .NET — SetCellValue API

- **Format:** FODS (.NET)
- **API:** `SetCellValue(sheet, row, col, value)`
- **Capability:** Same-format cell edit — read FODS, modify cell, write FODS
- **Skill:** `/add-dotnet-api`
- **Commercial POC value:** HIGH — demonstrates round-trip edit of spreadsheet format
- **Source files:** `src/net/fods/FodsDocument.cs`
- **Test file:** `tests/net/fods/FodsSetCellValueTests.cs`
- **Target:** 8+ new tests

---

### WI-H: FODT .NET — SaveToFile API

- **Format:** FODT (.NET)
- **API:** `SaveToFile(path)`
- **Capability:** Same-format save after edit — load FODT, modify, save to disk
- **Skill:** `/add-dotnet-api`
- **Commercial POC value:** HIGH — demonstrates round-trip edit of document format
- **Source files:** `src/net/fodt/FodtDocument.cs`
- **Test file:** `tests/net/fodt/FodtSaveToFileTests.cs`
- **Target:** 8+ new tests

---

### WI-I: Netpbm .NET — SetPixelColor API

- **Format:** Netpbm (.NET, PPM/PGM/PBM)
- **API:** `SetPixelColor(x, y, color)`
- **Capability:** Pixel edit — load image, modify pixel, write back
- **Skill:** `/add-dotnet-api`
- **Commercial POC value:** MEDIUM — demonstrates pixel-level image editing
- **Source files:** `src/net/netpbm/Model/NetpbmImage.cs`
- **Test file:** `tests/net/netpbm/NetpbmSetPixelColorTests.cs`
- **Target:** 8+ new tests

---

### WI-J: Python Netpbm — PPM Installed Package Example

- **Format:** PPM (Python)
- **Type:** Installed package example script
- **Capability:** Shows `import ppm` workflow after `pip install` — FOSS POC proof
- **Skill:** `/add-installed-package-example`
- **FOSS POC value:** HIGH — demonstrates installability for open-source users
- **Output file:** `examples/python/ppm/ppm_example.py`
- **Target:** Working example that runs in clean venv with installed wheel

---

### WI-P: SYLK — CSV Export Hardening

- **Format:** SYLK (Python)
- **Type:** Test hardening + edge case coverage
- **Capability:** `sylk_to_csv` with Unicode, empty cells, large sheets
- **Skill:** `/add-python-api`
- **Target:** 6+ new tests covering edge cases

---

### WI-R: FODT .NET TXT Dogfood Bridge

- **Format:** FODT → TXT (.NET)
- **Type:** Dogfood export
- **Capability:** Export FODT document text content to plain TXT via .NET
- **Skill:** `/add-dogfood-export`
- **Commercial POC value:** HIGH — demonstrates cross-format export in .NET
- **Test file:** `tests/net/fodt/FodtTxtDogfoodTests.cs`
- **Target:** 6+ new tests

---

## Product Work Summary Table

| ID | Format | Track | Skill | POC Value | Target Tests |
|----|--------|-------|-------|-----------|-------------|
| WI-G | FODS | .NET | `/add-dotnet-api` | HIGH | 8+ |
| WI-H | FODT | .NET | `/add-dotnet-api` | HIGH | 8+ |
| WI-I | Netpbm | .NET | `/add-dotnet-api` | MEDIUM | 8+ |
| WI-J | PPM | Python FOSS | `/add-installed-package-example` | HIGH | — |
| WI-P | SYLK | Python | `/add-python-api` | MEDIUM | 6+ |
| WI-R | FODT→TXT | .NET dogfood | `/add-dogfood-export` | HIGH | 6+ |

## Constraint

All product work is gated behind plan healing completion (Train F). No product work begins before `PLAN_HEALING: COMPLETE` is recorded in `reports/r91/plan-healing-before-execution.md`.
