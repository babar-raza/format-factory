# Target Writer Registry Model
Sprint: FORMAT-FACTORY-AUTHORITY-LAYERS-AND-TARGET-WRITER-MEGA-TRAIN-R119-001

## Model Schema (Proposed)

```yaml
writer_id: string           # Unique writer ID (e.g., ff-csv-writer-net-001)
target_format: string       # Format written (e.g., csv, html, txt, markdown)
library_name: string        # Assembly name (e.g., FormatFactory.Csv)
language: dotnet | python
library_path: string        # Relative path to csproj/pyproject
api_entrypoint: string      # Main class (e.g., FormatFactory.Csv.CsvWriter)
public_methods:             # List of public API methods
  - string
tests:                      # List of test files
  - string
source_products_consuming:  # Products that use this writer
  - product: string
    exporter: string
    wired: boolean
    tests: string
status: enum                # MWP_IMPLEMENTED_NOT_RELEASE_READY | PRODUCTION_READY | BLOCKED
commercial_product_ready: boolean
gate_11_approved: boolean
notes: string
```

## Current Registry State (As-Built)

| writer_id | target_format | library_name | wired_to | tests | status |
|-----------|--------------|-------------|---------|-------|--------|
| ff-csv-writer-net-001 | csv | FormatFactory.Csv | FodsCsvExporter | 15 | MWP |
| ff-html-writer-net-001 | html | FormatFactory.Html | FodsHtmlExporter | 12 | MWP |
| ff-txt-writer-net-001 | txt | FormatFactory.Txt | FodtTxtExporter | 8 | MWP |
| ff-md-writer-net-001 | markdown | FormatFactory.Markdown | FodtMarkdownExporter | 11 | MWP |

## Where to Register
Proposed location: `registry/format-registry.yaml` → `target_writers:` section
OR: New file `registry/target-writer-registry.yaml`
Decision: requires human approval per AGENTS.md.
