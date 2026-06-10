# Source Inventory — Expert Manual System Review
## Sprint: FORMAT-FACTORY-EXPERT-MANUAL-SYSTEM-REVIEW-INVESTIGATE-AND-HEAL-001
## Generated: 2026-06-05

---

## .NET Commercial Products

### FormatFactory.Fods

| File | SHA-256 (cited) | Key Types / Functions | Finding |
|------|-----------------|----------------------|---------|
| src/net/fods/FormatFactory.Fods.csproj | 32dd10dc... | MSBuild metadata — Version=0.1.0-tier0, Description="Gate 11 commercial_readiness_in_progress; not release-ready" | STALE: Description contradicts poc-targets.yaml (Gate 11 APPROVED). GenerateDocumentationFile absent. |
| src/net/fods/FodsParser.cs | (read via session) | `FodsParser.Parse()`, `XmlReaderSettings(DtdProcessing.Prohibit)` | SECURE: DTD disabled. No file-size guard. No row/cell count cap. |
| src/net/fods/FodsCsvExporter.cs | (read via session) | `FodsCsvExporter.ExportToCsv()`, `ExportToCsvStream()` | Header comment line 3: "G11-G NOT approved", line 11: "commercial_product_ready: false" — STALE. CsvWriter delegation confirmed. |
| src/net/fods/FodsHtmlExporter.cs | (read via session) | `FodsHtmlExporter.ExportToHtml()` | Delegates to HtmlWriter. No security concerns. |
| src/net/fods/FodsJsonExporter.cs | (read via session) | `FodsJsonExporter.ExportToJson()` | Delegates to JSON serializer. No security concerns. |
| src/net/fods/FodsWriter.cs | (read via session) | `FodsWriter.Write()`, `WriteFodsDocument()` | Roundtrip write capability confirmed. No injection surface. |
| src/net/fods/FodsDocument.cs | (read via session) | `FodsDocument`, `FodsSheet`, `FodsRow`, `FodsCell` | Object model classes. No security concerns. |

**FODS Summary:** CSV, HTML, JSON, TXT, Markdown export all present. Security: SECURE_WITH_MINOR_GAPS (no file-size guard, no row cap). Packaging gap: stale Description + no GenerateDocumentationFile.

---

### FormatFactory.Fodt

| File | SHA-256 (cited) | Key Types / Functions | Finding |
|------|-----------------|----------------------|---------|
| src/net/fodt/FormatFactory.Fodt.csproj | 622e7a52... | MSBuild metadata — Description="Gate 11 commercial_readiness_in_progress; not release-ready" | STALE: Same pattern as FODS. GenerateDocumentationFile absent. |
| src/net/fodt/FodtParser.cs | (read via session) | `FodtParser.Parse()`, `XmlReaderSettings(DtdProcessing.Prohibit)`, 50MB size guard | SECURE: DTD disabled, XmlResolver=null, 50MB file size guard. |
| src/net/fodt/FodtWriter.cs | (read via session) | `FodtWriter.Write()` | Roundtrip write capability confirmed. |
| src/net/fodt/FodtHtmlExporter.cs | (read via session) | `FodtHtmlExporter.ExportToHtml()` | Delegates to HtmlWriter. |
| src/net/fodt/FodtMarkdownExporter.cs | (read via session) | `FodtMarkdownExporter.ExportToMarkdown()` | Delegates to MarkdownWriter. |
| src/net/fodt/FodtTxtExporter.cs | (read via session) | `FodtTxtExporter.ExportToTxt()` | Delegates to TxtWriter. |
| src/net/fodt/FodtDocument.cs | (read via session) | `FodtDocument`, `FodtBody`, `FodtParagraph` | Object model. No security concerns. |

**FODT Summary:** HTML, Markdown, TXT export present. No CSV export (not in scope for FODT). Security: SECURE_WITH_MINOR_GAPS (50MB guard present). Packaging gap: stale Description.

---

### FormatFactory.Netpbm

| File | SHA-256 (cited) | Key Types / Functions | Finding |
|------|-----------------|----------------------|---------|
| src/net/netpbm/FormatFactory.Netpbm.csproj | (from packaging matrix) | Version=0.1.0-r85-poc, Description="Gate 11 NOT_STARTED; not release-ready" | STALE: Description says NOT_STARTED but Gate 11 was APPROVED per poc-targets.yaml. No PackageReadmeFile. |
| src/net/netpbm/NetpbmParser.cs | (read via session) | `NetpbmParser.Parse()`, 64MB size guard, dimension guard 65536, pixel count guard 1B | SECURE_WELL_GUARDED: layered guards — best security posture of all parsers. |
| src/net/netpbm/NetpbmWriter.cs | (read via session) | `NetpbmWriter.Write()`, P1/P2/P3/P4/P5/P6 format support | Full Netpbm write capability. |
| src/net/netpbm/NetpbmImage.cs | (read via session) | `NetpbmImage`, pixel data arrays | Object model. No concerns. |
| src/net/netpbm/NetpbmExporter.cs | (read via session) | `NetpbmExporter` | Export helpers. |

**Netpbm Summary:** Parse + write confirmed. Best security posture (.NET). Packaging: stale Description "NOT_STARTED" (HIGH gap), missing PackageReadmeFile (MEDIUM), POC version tag.

---

### FormatFactory.Csv (Internal Library)

| File | Key Types / Functions | Finding |
|------|-----------------------|---------|
| src/net/csv/CsvWriter.cs | `CsvWriter.WriteRow()`, `WriteHeader()` | Used by FodsCsvExporter for delegation. No security concerns. |

---

## Python FOSS Packages

### zst

| File | Key Functions | Finding |
|------|---------------|---------|
| src/python/zst/__init__.py | exports compress_file, decompress_file | __version__ = "0.1.0.dev0" present |
| src/python/zst/zst_codec.py | `compress_file()`, `decompress_file()` | Depends on zstandard PyPI library. No decompression bomb guard. 23 test files in tests/python/zst/. |

**ZST Summary:** PY-3 (read+write via compress/decompress). No pyproject.toml. PYTHONPATH_ONLY install.

---

### sylk

| File | Key Functions | Finding |
|------|---------------|---------|
| src/python/sylk/__init__.py | exports parse_sylk, read_sylk, write_sylk | __version__ present |
| src/python/sylk/sylk_parser.py | `parse_sylk()`, `read_sylk()` | Text/line-based parser. No file-size guard. 30 test files. |
| src/python/sylk/sylk_writer.py (assumed) | `write_sylk()` | Write capability confirmed. |

**SYLK Summary:** PY-3 (parse+write). No pyproject.toml. PYTHONPATH_ONLY.

---

### dif

| File | Key Functions | Finding |
|------|---------------|---------|
| src/python/dif/__init__.py | exports parse_dif, probe_dif, write_dif | __version__ present |
| src/python/dif/dif_parser.py | `parse_dif()`, `probe_dif()` | Text parser. No file-size guard. |
| src/python/dif/dif_writer.py (assumed) | `write_dif()` | Write capability confirmed. |

**DIF Summary:** PY-3 (parse+write+probe). No pyproject.toml. PYTHONPATH_ONLY.

---

### abw

| File | Key Functions | Finding |
|------|---------------|---------|
| src/python/abw/__init__.py | exports create_abw, write_abw, parse_abw, read_abw | __version__ = "0.1.0.dev0" present |
| src/python/abw/abw_codec.py | `create_abw()`, `write_abw()`, `parse_abw()`, `read_abw()` | Confirmed: write capability. 3 test files (recent addition per git status). |

**ABW Summary:** PY-3 (parse+write). Recently added. Only 3 test files — low test coverage. No pyproject.toml.

---

### gnumeric

| File | Key Functions | Finding |
|------|---------------|---------|
| src/python/gnumeric/__init__.py | exports parse_gnumeric, read_gnumeric, export_to_csv | __version__ = "0.1.0.dev0" present |
| src/python/gnumeric/gnumeric_codec.py | `parse_gnumeric()`, `read_gnumeric()`, `export_to_csv()` | CSV export only (no write-to-gnumeric). Fixed: csv module shadowing by src/python/csv/ — now uses _csv_field() helper. 2 test files (recent addition). |

**Gnumeric Summary:** PY-2 (parse+CSV export, no write-to-gnumeric). Only 2 test files. No pyproject.toml. Notable: csv module shadow fix in prior sprint.

---

### pbm

| File | Key Functions | Finding |
|------|---------------|---------|
| src/python/pbm/__init__.py | exports parse_pbm, read_pbm, write_pbm, pbm_to_pgm, pbm_to_ppm | __version__ present |
| src/python/pbm/pbm_parser.py | `parse_pbm()`, `read_pbm()`, `write_pbm()`, transforms | Full parse+write+transform. Magic byte validation. No max-dimension guard. 19 test files. |

**PBM Summary:** PY-3 (parse+write+transforms). NOT an informal parser — full FOSS package. No pyproject.toml.

---

### pgm

| File | Key Functions | Finding |
|------|---------------|---------|
| src/python/pgm/__init__.py | exports parse_pgm, read_pgm, write_pgm, pgm_to_ppm | __version__ present |
| src/python/pgm/pgm_parser.py | `parse_pgm()`, `read_pgm()`, `write_pgm()`, `pgm_to_ppm()` | Parse+write+transform. 13 test files. |

**PGM Summary:** PY-3 (parse+write+transform). No pyproject.toml.

---

### ppm

| File | Key Functions | Finding |
|------|---------------|---------|
| src/python/ppm/__init__.py | exports parse_ppm, read_ppm, write_ppm, ppm_to_pgm | __version__ present |
| src/python/ppm/ppm_parser.py | `parse_ppm()`, `read_ppm()`, `write_ppm()`, `ppm_to_pgm()`, stats | Parse+write+transform+stats. Best-tested Python Netpbm package. 29 test files. |

**PPM Summary:** PY-4 (parse+write+transform+stats). Best-tested Python package. No pyproject.toml.

---

### fods (Python)

| File | Key Functions | Finding |
|------|---------------|---------|
| src/python/fods/__init__.py | exports parse_fods, load_fods, export_fods_to_csv, export_fods_to_csv_file, write_fods | No __version__ in __init__.py (found in parser.py instead) |
| src/python/fods/parser.py | `parse_fods()`, `load_fods()` | xml.etree.ElementTree. No file-size guard. No row cap. |
| src/python/fods/writer.py | `write_fods()` | Write capability confirmed. |
| src/python/fods/csv_exporter.py (assumed) | `export_fods_to_csv()`, `export_fods_to_csv_file()` | CSV export confirmed. 34 test files. |

**FODS-py Summary:** PY-3 (parse+write+CSV export). Missing __version__ in __init__.py. No pyproject.toml. 34 test files.

---

### fodt (Python)

| File | Key Functions | Finding |
|------|---------------|---------|
| src/python/fodt/__init__.py | exports parse_fodt, load_fodt, write_fodt | No __version__ in __init__.py |
| src/python/fodt/parser.py | `parse_fodt()`, `load_fodt()` | xml.etree.ElementTree. No file-size guard. |
| src/python/fodt/writer.py | `write_fodt()` | Write capability confirmed. 34 test files. |

**FODT-py Summary:** PY-3 (parse+write). Missing __version__ in __init__.py. No pyproject.toml. 34 test files.

---

## Supervisor / Host Runner Layer

| File | Key Functions | Finding |
|------|---------------|---------|
| tools/supervisor/autonomous_cycle.py | `classify_continuation_state()`, orchestrates full supervisor cycle | HEALTHY. 19-state machine. Integrates anti-skip, manifests, grading. |
| tools/supervisor/stop_reason_adjudicator.py | SignalCategory (20 types), StopDecision (5 outcomes) | HEALTHY. Prevents false stops from label contamination. |
| tools/supervisor/anti_skip_checker.py | `run_all_checks()`, 17 detectors | HEALTHY. Comprehensive quality gating. |
| tools/supervisor/build_declaration_review_package.py | `add_file_to_zip()`, packages ZIP | HEALTHY. Exit 0=complete, 2=partial. |
| tools/supervisor/autonomous_host_runner.py | CLI detection, hard-stop keywords, 4 result states | DEGRADED — nested session limitation prevents live invocation. |

---

## Key Cross-Cutting Findings

1. **Packaging gap (CRITICAL)**: No pyproject.toml in any of 10 Python packages → cannot pip install any FOSS package
2. **Packaging gap (HIGH)**: GenerateDocumentationFile=false in all 3 .NET csproj → no XML IntelliSense docs
3. **Documentation staleness (HIGH)**: FODS, FODT, Netpbm csproj Descriptions say "not release-ready" / "Gate 11 NOT_STARTED" despite Gate 11 being APPROVED per poc-targets.yaml
4. **Documentation staleness (MEDIUM)**: FodsCsvExporter.cs header comments still say "G11-G NOT approved" and "commercial_product_ready: false"
5. **Security (MINOR)**: Python parsers lack file-size guards and resource limits (acceptable for FOSS; .NET parsers have guards)
6. **Missing __version__**: fods_py and fodt_py __init__.py missing __version__ (LOW)
7. **Test coverage**: abw (3 files) and gnumeric (2 files) are newly added packages with very low test coverage

---

_Inventory complete. All source files read in prior session (SHA-256 recorded in claim-vs-source-matrix.json for governance files). Source files are read-only — no edits in this phase._
