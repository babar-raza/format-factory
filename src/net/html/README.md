# FormatFactory.Html

.NET export-helper library for HTML output generation. Used internally by FODS, FODT, and NetPBM
exporters to produce HTML renditions of documents and images.

## Classification

`export_helper_only` — Output-only export target. Not a parseable input format.
Not intended as a standalone product format.

## Usage

This library is consumed by other FormatFactory format libraries as an export target.
It is not designed for direct end-user consumption.

```csharp
// Used indirectly via FODS/FODT exporters:
var doc = FodsDocument.Load("spreadsheet.fods");
// HTML export available through the owning document's export methods
```

## Gate Status

Not subject to Gate 11 approval — internal helper only.

## Installation

<!-- BEGIN:README-INSTALLATION generated=2026-06-28T08:14:29+00:00 source=package-metadata -->
```bash
dotnet add package FormatFactory.Html
```
<!-- END:README-INSTALLATION -->

## Package Info

<!-- BEGIN:README-PACKAGE_INFO generated=2026-06-28T08:14:29+00:00 source=repository-metadata -->
| Field | Value |
|---|---|
| Format | HTML |
| Track | dotnet |
| Package | FormatFactory.Html |
| Version | 0.1.0-mwp |
| License | unknown |
| Python | unknown |
| .NET | net10.0 |
| Spec | unknown |
| QName coverage | 0/0 implemented |
| Source files | 1 |
| Test files | 5 |
<!-- END:README-PACKAGE_INFO -->
