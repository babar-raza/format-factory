# .NET Dogfood Architecture Gap Report
# Sprint: FORMAT-FACTORY-MAINSTREAM-PRODUCT-DEEPENING-DOGFOOD-GAP-RESOLUTION-001
# Generated: 2026-06-04
# authority_state: ai_draft (advisory)

---

## Summary

Four .NET dogfood export capabilities are classified as GAP_DOGFOOD_EXTERNAL in
`product-capability-matrix/poc-targets.yaml` (R106). These gaps cannot be closed this sprint
because the required Format Factory target writer libraries do not yet exist for .NET.
The `/add-dogfood-export` stop condition fires for all four.

---

## Gap Table

| Gap ID | Format | Capability Path | Current Status | Target FF Library | Why Not Closeable |
|--------|--------|----------------|----------------|-------------------|-------------------|
| commercial-net-fods-dogfood-status-fods-to-csv-dotnet | FODS | dogfood_status.fods_to_csv_dotnet | GAP_DOGFOOD_EXTERNAL | format-factory-csv (when .NET CSV library exists) | No FF CSV library for .NET; FodsCsvExporter.cs writes directly, not via FF target writer |
| commercial-net-fods-dogfood-status-fods-to-html-dotnet | FODS | dogfood_status.fods_to_html_dotnet | GAP_DOGFOOD_EXTERNAL | format-factory-html (when .NET HTML library exists) | No FF HTML library for .NET; FodsHtmlExporter.cs writes directly |
| commercial-net-fodt-dogfood-status-fodt-to-markdown-dotnet | FODT | dogfood_status.fodt_to_markdown_dotnet | GAP_DOGFOOD_EXTERNAL | format-factory-markdown (when .NET Markdown library exists) | No FF Markdown library for .NET; FodtMarkdownExporter.cs writes directly |
| commercial-net-fodt-dogfood-status-fodt-to-txt-dotnet | FODT | dogfood_status.fodt_to_txt_dotnet | GAP_DOGFOOD_EXTERNAL | format-factory-txt (when .NET TXT library exists) | No FF TXT library for .NET; FodtTxtExporter.cs writes directly |

---

## Root Cause

A Format Factory dogfood export requires that the write backend is another Format Factory
library (e.g., `format-factory-csv` for CSV output). This enforces the internal consumption
model where FF libraries use each other.

The .NET exporters (`FodsCsvExporter.cs`, `FodsHtmlExporter.cs`, `FodtMarkdownExporter.cs`,
`FodtTxtExporter.cs`) currently write output directly using .NET standard library calls.
No Format Factory target writer library exists for CSV, HTML, Markdown, or TXT in .NET.

Evidence from `poc-targets.yaml` (R106):
```yaml
dogfood_status:
  fods_to_csv_dotnet: GAP_DOGFOOD_EXTERNAL
  target_ff_library_for_csv_dotnet: "format-factory-csv (when .NET CSV library exists)"
  notes: ".NET FodsCsvExporter writes directly"
```

The `/add-dogfood-export` stop condition fires: "A Format Factory target writer does not exist."

---

## /add-dogfood-export Stop Condition Verification

Skill `add-dogfood-export` requires handoff field `target_ff_library` to reference an existing
Format Factory library. For all four gaps, the target library is `(when .NET X library exists)` —
the library does not exist. The stop condition fires immediately.

---

## This Sprint Decision: ACCEPT_AS_ARCHITECTURE_GAP

All four gaps are accepted as architecture-blocked external gates. No source changes will be
made for these. In the evidence declaration they will be listed as `blocked_external_gate`.

---

## Escalation Path (Future Sprint)

Option A: Create a new `format-factory-csv` .NET library as a standalone Format Factory product,
then use `/add-dogfood-export` to wire FODS→CSV through it.

Option B: Accept these as permanent EXTERNAL exports (not dogfood) and update the
poc-targets.yaml classification from `GAP_DOGFOOD_EXTERNAL` to `IMPLEMENTED_EXTERNAL`
with explicit governance noting that no FF internal writer exists.

This decision requires explicit user authorization. It is NOT made autonomously in this sprint.

---

## Confirmed: Python Dogfood Paths Are IMPLEMENTED

For reference, the Python-side dogfood exports ARE correctly implemented (using FF libraries):
- `fods_to_csv_python`: IMPLEMENTED (uses `format-factory-csv` Python model)
- `fodt_to_txt_python`: IMPLEMENTED (uses `document_to_text` from FF FODT library)
- `pbm_to_pgm_python`: IMPLEMENTED (uses `write_pgm` from format-factory-pgm)
- `pbm_to_ppm_python`: IMPLEMENTED (uses `write_ppm` from format-factory-ppm)

The .NET gaps are a .NET-specific architecture constraint, not a product gap in the Python track.
