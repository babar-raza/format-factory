# FormatFactory.Markdown

.NET export-helper library for Markdown output generation. Used internally by FODT and FODS
exporters to produce Markdown renditions of documents.

## Classification

`export_helper_only` — Output-only export target. Not a parseable input format.
Not intended as a standalone product format.

## Usage

This library is consumed by other FormatFactory format libraries as an export target.
It is not designed for direct end-user consumption.

```csharp
// Used indirectly via FODT exporters:
var doc = FodtDocument.Load("document.fodt");
// Markdown export available through the owning document's export methods
```

## Gate Status

Not subject to Gate 11 approval — internal helper only.

## Installation

<!-- BEGIN:README-INSTALLATION generated=2026-06-28T08:14:29+00:00 source=package-metadata -->
```bash
dotnet add package FormatFactory.Markdown
```
<!-- END:README-INSTALLATION -->

## Package Info

<!-- BEGIN:README-PACKAGE_INFO generated=2026-06-28T08:14:29+00:00 source=repository-metadata -->
| Field | Value |
|---|---|
| Format | MARKDOWN |
| Track | dotnet |
| Package | FormatFactory.Markdown |
| Version | 0.1.0-mwp |
| License | unknown |
| Python | unknown |
| .NET | net10.0 |
| Spec | unknown |
| QName coverage | 0/0 implemented |
| Source files | 1 |
| Test files | 5 |
<!-- END:README-PACKAGE_INFO -->
