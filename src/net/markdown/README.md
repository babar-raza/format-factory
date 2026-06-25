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
