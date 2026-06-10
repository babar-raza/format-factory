# FODT Implementation Verification (TC-A-002)
Sprint: FORMAT-FACTORY-MAINSTREAM-R114-PRODUCT-EXECUTION-DIRTY-STATE-COMMIT-AND-BREADTH-SPRINT-001
Generated: 2026-06-04

---

## Actual Method Signatures (verified from source)

### FodtDocument.cs (instance methods)

| Method | Line | Signature |
|--------|------|-----------|
| ExportToMarkdown | 522 | `public string ExportToMarkdown()` |
| ExportToMarkdownFile | 660 | `public void ExportToMarkdownFile(string filePath)` |
| GetPlainText | 161 | `public string GetPlainText()` |
| ExportToPlainTextFile | 647 | `public void ExportToPlainTextFile(string filePath)` |
| GetPlainTextRange | 180 | `public string GetPlainTextRange(int startIndex, int endIndex)` |

### FodtMarkdownExporter.cs (static class — file-to-file API)

| Method | Signature |
|--------|-----------|
| ExportToMarkdown (overload 1) | `public static FodtMarkdownExportResult ExportToMarkdown(string fodtPath, string mdPath, long maxFileSizeBytes = ...)` |
| ExportToMarkdown (overload 2) | `public static FodtMarkdownExportResult ExportToMarkdown(FodtDocument doc, string sourcePath, string mdPath)` |

### FodtTxtExporter.cs (static class — file-to-file API)

| Method | Signature |
|--------|-----------|
| ExportTxt (overload 1) | `public static FodtTxtExportResult ExportTxt(string fodtPath, string txtPath, long maxFileSizeBytes = ...)` |
| ExportTxt (overload 2) | `public static FodtTxtExportResult ExportTxt(FodtDocument doc, string sourcePath, string txtPath)` |

**NOTE: Method name is `ExportTxt`, NOT `ExportToTxt`. The handoff YAML had the wrong name.**

---

## Test File Analysis

### FodtR112MarkdownExportDogfoodTests.cs (8 tests, R112)
- Uses: `doc.ExportToMarkdown()` (instance method) — CORRECT
- Uses: `doc.ExportToMarkdownFile(path)` (instance method) — CORRECT
- Tests: headings, paragraphs, after-replace, save/reload roundtrip, file creation, HTML export, plain text
- Status: TEST FILE EXISTS, TESTS USE CORRECT API

### FodtR113TxtDogfoodTests.cs (6 tests, R113)
- Uses: `doc.GetPlainText()`, `doc.ExportToMarkdown()`, `doc.ExportToHtml()`, `doc.ExportToPlainTextFile()` (all instance methods)
- Tests: plain text after append, markdown after heading, HTML after append, TXT file save/reload, metadata access, word count
- Status: TEST FILE EXISTS, TESTS USE CORRECT API

---

## Capability Status

| Capability | Sprint Implemented | Test File | Status |
|-----------|-------------------|-----------|--------|
| FODT ExportToMarkdown (instance method) | R108+ | FodtR108ExportToMarkdownFileTests.cs, FodtR112MarkdownExportDogfoodTests.cs | ALREADY_IMPLEMENTED |
| FODT ExportToMarkdownFile (instance method) | R108+ | FodtR108DogfoodMarkdownExportTests.cs | ALREADY_IMPLEMENTED |
| FODT FodtMarkdownExporter (static, file-to-file) | R23 | Pre-R94 | ALREADY_IMPLEMENTED |
| FODT GetPlainText (instance method) | R107+ | FodtR107ExportToPlainTextFileTests.cs | ALREADY_IMPLEMENTED |
| FODT ExportToPlainTextFile (instance method) | R107+ | FodtR107ExportToPlainTextFileTests.cs | ALREADY_IMPLEMENTED |
| FODT FodtTxtExporter (static, file-to-file) | R22+ | Pre-R94 | ALREADY_IMPLEMENTED |

---

## Handoff Repair Required

### fodt-markdown-handoff.yaml
- Claimed: `public void ExportToMarkdown(string outputPath)` — WRONG (non-existent signature)
- Actual API used by tests: `doc.ExportToMarkdown()` (no args, returns string) + `doc.ExportToMarkdownFile(path)` (void)
- Also available: `FodtMarkdownExporter.ExportToMarkdown(string fodtPath, string mdPath)` (static, file-to-file)
- Action: Update to reflect ALREADY_IMPLEMENTED status; update mode to `verify`; correct signature

### fodt-txt-handoff.yaml
- Claimed: method name `ExportToTxt` — WRONG (name should be `ExportTxt`)
- Actual: `FodtTxtExporter.ExportTxt(string fodtPath, string txtPath)` or instance `doc.GetPlainText()`
- Action: Fix method name; update to ALREADY_IMPLEMENTED; mode `verify`

---

## Conclusion

Both FODT Markdown and FODT TXT capabilities are ALREADY_IMPLEMENTED as of the R94–R113 accumulated sprints.
The handoffs were written against hypothetical signatures and need repair to reflect actual source code.
No new implementation is needed for these capabilities — only handoff correction and verification.
