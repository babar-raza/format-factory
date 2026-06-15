# /spec-literal-qname-to-code-mapping

**Skill ID:** spec-literal-qname-to-code-mapping
**Registry Version:** 2.0
**Track:** spec_parity
**Status:** active

## Purpose

Generate or validate a QName-to-code mapping for a format. Produces:
- `qname-to-code-map-<format>.json` — maps each spec QName to its implementation class/function
- `namespace-tree-<format>.json` — hierarchical namespace structure
- `containment-graph-<format>.json` — spec containment relationships

Required before any product model work for the format.

## Invocation

```
python tools/supervisor/qname_ontology_generator.py \
  --format <FORMAT_ID> \
  --output-dir <output_dir>
```

## Required Inputs

- `format_id` — e.g., FODS, FODT, ZST
- `source_paths` — Python source files to scan for implementations
- `output_dir` — where to write QName maps

## Mandatory Validations

1. `qname_map_json_valid` — output JSON must parse without error
2. `namespace_tree_json_valid` — namespace tree JSON must parse without error
3. `qname_generator_exit_zero` — generator must exit 0

## Enforcement Rules

- Product model taskcards CANNOT omit spec_qname after this skill runs
- Flat/ad-hoc classes for spec concepts are FORBIDDEN
- All mapped QNames must have a source reference or a documented exception

## Evidence Requirements

- Raw log of generator execution
- QName map JSON artifact path
- Namespace tree JSON artifact path
- Mapping coverage percentage

## Allowed Paths

- `tools/supervisor/qname_ontology_generator.py`
- `src/python/<format>/` (read-only scan)
- `<output_dir>/` (write QName maps)
- `.local/evidences/<run_id>/`

## Forbidden Paths

- No edits to `src/` source files
- No Gate 11 commercial paths unless explicitly scoped

## Stop Conditions

- Stop if `qname_ontology_generator.py` exits non-zero
- Stop if output JSON fails to parse
- Stop if `format_id` is not in the known format registry

## Gate 11

NOT affected. This skill operates on FOSS Python paths only unless explicitly scoped to commercial.
