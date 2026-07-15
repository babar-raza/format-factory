# Parser Notes: Jupyter Notebook

## Parsing Strategy
- **Primary module:** json (stdlib)
- **Reuse pattern:** JSON-based codec pattern (similar to ndjson codec)
- **Estimated LOC:** 200-300

## Detection (Probe)
Check for `.ipynb` extension. Validate by parsing as JSON and checking for `nbformat` key at the top level with integer value >= 4.

## Loading
Load the entire file as JSON using `json.load()`. Extract the `cells` list and iterate, building a structured model with cell type, source content, and outputs. Validate against nbformat v4.5 schema constraints (cell_type enum, output type enum).

## Writing
Serialize the model back to JSON with `json.dump()`, preserving the nbformat version fields and metadata. Write support planned.

## Dependencies
- stdlib only (json module)
- No new external dependencies required
