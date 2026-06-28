# FormatFactory.Txt

.NET export-helper library for plain text extraction. Used internally by FODT, FODS, and NetPBM
exporters to produce plain text renditions of documents and images.

## Classification

`export_helper_only` — Output-only export target. Plain text extraction helper.
Not a standalone parseable format. Not intended as a standalone product format.

## Usage

This library is consumed by other FormatFactory format libraries as an export target.
It is not designed for direct end-user consumption.

```csharp
// Used indirectly via FODT exporters:
var doc = FodtDocument.Load("document.fodt");
// Plain text export available through the owning document's export methods
```

## Gate Status

Not subject to Gate 11 approval — internal helper only.

## Installation

<!-- BEGIN:README-INSTALLATION generated=2026-06-28T08:14:30+00:00 source=package-metadata -->
```bash
dotnet add package FormatFactory.Txt
```
<!-- END:README-INSTALLATION -->

## Package Info

<!-- BEGIN:README-PACKAGE_INFO generated=2026-06-28T08:14:30+00:00 source=repository-metadata -->
| Field | Value |
|---|---|
| Format | TXT |
| Track | dotnet |
| Package | FormatFactory.Txt |
| Version | 0.1.0-mwp |
| License | unknown |
| Python | unknown |
| .NET | net10.0 |
| Spec | unknown |
| QName coverage | 0/0 implemented |
| Source files | 1 |
| Test files | 5 |
<!-- END:README-PACKAGE_INFO -->
