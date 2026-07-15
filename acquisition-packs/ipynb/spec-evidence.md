# Spec Evidence: Jupyter Notebook

## Primary Specification
- **Title:** The Notebook file format (nbformat)
- **Version:** nbformat v4.5
- **URL:** https://nbformat.readthedocs.io/en/latest/format_description.html
- **Body:** Jupyter Project
- **Accessed:** 2026-07-14
- **License:** Apache 2.0/BSD/MIT

## Spec Availability Assessment
- Freely accessible: Yes
- Machine-readable schema: Yes (JSON Schema provided by nbformat package)
- Actively maintained: Yes

## Key Structural Facts
- The notebook is a JSON document with a top-level object containing `nbformat`, `nbformat_minor`, `metadata`, and `cells` keys
- Each cell has a `cell_type` (code, markdown, raw), `source` (list of strings or single string), `metadata`, and optional `outputs` (for code cells)
- Code cell outputs are typed: `stream`, `display_data`, `execute_result`, or `error`, each with distinct schemas
- The `metadata.kernelspec` object identifies the execution kernel (language, display name, kernel name)
