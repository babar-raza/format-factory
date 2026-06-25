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
