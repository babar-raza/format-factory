# R42 POC Product Matrix

**Sprint:** R42
**Date:** 2026-05-21
**Status:** POC_READY (local release candidates, not commercially approved)

---

## Python FOSS POC Artifacts

| Package | Wheel File | Version | Import Name | Smoke Result |
|---------|-----------|---------|-------------|--------------|
| FODS | `aspose_format_factory_fods-0.1.0.dev0-py3-none-any.whl` | 0.1.0.dev0 | `import fods` | PASS |
| FODT | `aspose_format_factory_fodt-0.1.0.dev0-py3-none-any.whl` | 0.1.0.dev0 | `import fodt` | PASS |

### FODS Python Smoke (R42)
```
install: clean venv (Python 3.13.2), pip install wheel — success
format_id:    fods
spec_version: ODF 1.3
version:      0.1.0
samples parsed: 4/4 (formula-basic, minimal-spreadsheet, multi-sheet-basic, typed-values-basic)
parse_fods_strict: returns structured sheet/row/cell data
CSV export: demonstrated via consumer-side helper (19 deepening tests PASS)
```

### FODT Python Smoke (R42)
```
install: clean venv (Python 3.13.2), pip install wheel — success
format_id:    fodt
spec_version: ODF 1.3
version:      0.1.0
samples parsed: 4/4 (headings-and-paragraphs, list-basic, minimal-document, table-basic)
parse_fodt_strict: returns blocks[], lists[], tables[]
plain-text extraction: demonstrated via consumer-side helper (19 deepening tests PASS)
```

---

## .NET Commercial POC Artifacts

| Package | NuGet File | Version | Test Count | Smoke Result |
|---------|-----------|---------|------------|--------------|
| FODS | `FormatFactory.Fods.0.1.0-tier0.nupkg` | 0.1.0-tier0 | 157 | PASS |
| FODT | `FormatFactory.Fodt.0.1.0-tier0.nupkg` | 0.1.0-tier0 | 145 | PASS |

### FODS .NET Smoke (R42)
```
dotnet test tests/net/fods/: Passed 157, Failed 0, Skipped 0
build: FormatFactory.Fods.dll (net10.0) — clean build
package: FormatFactory.Fods.0.1.0-tier0.nupkg in .local/pack-output/
```

### FODT .NET Smoke (R42)
```
dotnet test tests/net/fodt/: Passed 145, Failed 0, Skipped 0
build: FormatFactory.Fodt.dll (net10.0) — clean build
package: FormatFactory.Fodt.0.1.0-tier0.nupkg in .local/pack-output/
```

---

## POC Readiness Assessment

| Dimension | FODS Python | FODT Python | FODS .NET | FODT .NET |
|-----------|------------|------------|-----------|-----------|
| Gates 1-10 | PASS | PASS | PASS | PASS |
| Gate 11 | NOT_STARTED (G11-G) | NOT_STARTED (G11-G) | NOT_STARTED (G11-G) | NOT_STARTED (G11-G) |
| Clean venv install | PASS | PASS | N/A | N/A |
| Sample parsing | 4/4 PASS | 4/4 PASS | via tests | via tests |
| Test count | 85 (66+19) | 134 (115+19) | 157 | 145 |
| commercial_product_ready | false | false | false | false |
| POC local readiness | LOCAL_POC_READY | LOCAL_POC_READY | LOCAL_POC_READY | LOCAL_POC_READY |

**Gate 11 blocker:** G11-G requires Babar Raza written approval. NOT_STARTED.
**Push blocker:** No artifacts pushed; all local only (.local/, gitignored).

---

## Artifact Locations

All artifacts are in `.local/` (gitignored). SHA-256 hashes documented in `reports/r42/package-artifact-manifest.yaml`.

```
.local/package-builds/python-foss/aspose-format-factory-fods/dist/
  aspose_format_factory_fods-0.1.0.dev0-py3-none-any.whl

.local/package-builds/python-foss/aspose-format-factory-fodt/dist/
  aspose_format_factory_fodt-0.1.0.dev0-py3-none-any.whl

.local/pack-output/
  FormatFactory.Fods.0.1.0-tier0.nupkg
  FormatFactory.Fodt.0.1.0-tier0.nupkg
```
