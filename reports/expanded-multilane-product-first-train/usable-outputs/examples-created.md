# Usable Outputs — Sprint EXPANDED-MULTI-LANE-001

## Outputs Produced This Sprint

### ABW CSV Export Sample
Function: `export_to_csv(source)`
Format: CSV with single `text` column
Coverage: plain text, comma-escaped, quote-escaped paragraphs

### NDJSON append_record Sample
Function: `append_record(dest, record)`
Demonstrates: incremental file building, atomic append, non-destructive

### NDJSON filter_records Sample
Function: `filter_records(source, key, value)`
Demonstrates: key/value filtering on dict records, non-dict exclusion

### Gnumeric get_cell_value Sample
Function: `get_cell_value(model, sheet_index, row, col)`
Demonstrates: programmatic cell access by position

## Outputs Stored
See `.local/evidences/expanded-multilane-product-first-train/sample-outputs/` for generated samples.
