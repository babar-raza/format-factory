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
