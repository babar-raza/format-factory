# Export Target Writer Policy Audit — R118

**Sprint:** FORMAT-FACTORY-UNIFIED-POC-AUTHORITY-RECONCILIATION-R118-001

---

## Policy Under Review

> "No claiming export/dogfood support unless reusable target writer support exists."
> "No accepting product-local serialization as Format Factory target writer support."

---

## Inventory: Reusable Target Writer Libraries

| Library | Exists? | Location |
|---------|---------|----------|
| FormatFactory.Csv (.NET) | NO | Not found in src/net/ or any project |
| FormatFactory.Html (.NET) | NO | Not found |
| FormatFactory.Markdown (.NET) | NO | Not found |
| FormatFactory.Txt (.NET) | NO | Not found |

**Finding:** No Format Factory target writer libraries exist for CSV, HTML, Markdown, or TXT in the .NET codebase.

---

## FODS Export Implementation Audit

**Source:** `src/net/fods/FodsDocument.cs`

| Method | Implementation | Type |
|--------|---------------|------|
| `ExportSheetToCsv()` | Product-local `StringBuilder` in FodsDocument.cs (lines 871-897) | Product-local |
| `ExportSheetToHtml()` | Product-local in FodsDocument.cs | Product-local |
| `ExportSheetToMarkdown()` | Product-local in FodsDocument.cs | Product-local |
| `ExportSheetToJson()` | Product-local in FodsDocument.cs | Product-local |
| `ExportSheetToCsvFile()` | Calls ExportSheetToCsv() and writes to file | Product-local |

**Verdict:** All FODS export methods are product-local implementations. No FormatFactory.Csv library is invoked.

---

## FODT Export Implementation Audit

**Source:** `src/net/fodt/FodtDocument.cs`

| Method | Implementation | Type |
|--------|---------------|------|
| `ExportToMarkdown()` | Product-local `StringBuilder` in FodtDocument.cs (lines 546-569) | Product-local |
| `ExportToHtml()` | Product-local HTML generation (lines 577-599) | Product-local |
| `ExportToPlainTextFile()` | Product-local file write | Product-local |
| `ExportToMarkdownFile()` | Calls ExportToMarkdown(), writes to file | Product-local |
| `ExportToHtmlFile()` | Calls ExportToHtml(), writes to file | Product-local |

**Verdict:** All FODT export methods are product-local implementations. No FormatFactory target writer is invoked.

---

## poc-targets.yaml Claims Assessment

The `poc-targets.yaml` already correctly classifies:
```yaml
dogfood_status:
  fods_to_csv_dotnet: GAP_DOGFOOD_EXTERNAL
  fods_to_html_dotnet: GAP_DOGFOOD_EXTERNAL
  target_ff_library_for_csv_dotnet: "format-factory-csv (when .NET CSV library exists)"
```

The `export_csv: PASS` refers to the **format export capability** (the format can produce CSV), NOT Format Factory pipeline dogfood. This distinction is correctly documented.

---

## Capability Delta Proposals

All capability delta proposals have:
```yaml
proposed_only: true
not_applied_to_poc_targets: true
```

No export dogfood claims have been applied to poc-targets.yaml.

---

## Policy Verdict

| Claim | Policy Status | Reason |
|-------|--------------|--------|
| FODS ExportSheetToCsv capability | PASS | Product-local feature; correctly documented in poc-targets as format export capability |
| FODS ExportSheetToCsvFile dogfood | RECLASS | This is product-local, not Format Factory target writer dogfood; capability delta correctly has proposed_only=true |
| FODT ExportToMarkdown capability | PASS | Product-local feature; correctly classified |
| FODT ExportToMarkdownFile dogfood | RECLASS | Same as above; proposed_only=true |
| poc-targets.yaml dogfood claims | PASS | `fods_to_csv_dotnet: GAP_DOGFOOD_EXTERNAL` correctly acknowledges missing target writer |

**No export target writer policy violations exist in poc-targets.yaml.**

The capability delta proposals correctly use `proposed_only: true, not_applied_to_poc_targets: true`.
The product-local export capabilities are valid product features, just not Format Factory target writer dogfood.

**Export Policy Result: PASS (with correct classification)**

---

## Impact on POC-Readiness

The absence of FormatFactory.Csv/.Html/.Markdown target writer libraries means:
- FODS/FODT "export pipeline dogfood" claims must be classified as `GAP_DOGFOOD_EXTERNAL`
- This is ALREADY the classification in poc-targets.yaml
- The POC-ready candidate does NOT require target writer libraries — it requires format read/edit/save capabilities
- Target writer libraries are a future enhancement, not a POC blocker

**Impact: None. POC-ready status is not blocked by this finding.**
