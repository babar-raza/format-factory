# /spec-shaped-product-architecture-blueprint

**Skill ID:** spec-shaped-product-architecture-blueprint
**Registry Version:** 2.0
**Track:** spec_parity
**Status:** active

## Purpose

Generate a spec-shaped architecture blueprint for a format. The blueprint defines:
- Class hierarchy derived from the spec (not invented arbitrarily)
- Containment edges from spec structure
- Namespace mapping per the canonical spec
- Implementation targets per class

No flat/ad-hoc class invention allowed. All classes must have a `spec_qname`.

## Required Inputs

- `format_id` — e.g., FODS, FODT, ZST
- `spec_body` — spec family (e.g., OASIS, IETF, Custom)
- `qname_map_path` — path to the QName map from spec-literal-qname-to-code-mapping
- `output_path` — where to write the blueprint YAML

## Blueprint Schema

```yaml
format_id: FODS
spec_body: OASIS
spec_version: ODF 1.3
blueprint_generated_at: <iso8601>
classes:
  - class_name: FodsDocument
    spec_qname: office:document
    canonical_namespace: urn:oasis:names:tc:opendocument:xmlns:office:1.0
    containment_parent: null
    children: [FodsSpreadsheet]
    implementation_target: src/python/fods/fods_model.py
```

## Mandatory Validations

1. `blueprint_yaml_valid` — YAML must parse without error
2. `no_flat_class_violations` — no class without spec_qname
3. `spec_qname_present_in_all_classes` — every class entry has canonical_namespace

## Allowed Paths

- `tools/supervisor/qname_ontology_generator.py`
- `src/python/<format>/` (read-only scan)
- `<output_path>` (write blueprint YAML)
- `.local/evidences/<run_id>/`

## Forbidden Paths

- No edits to `src/` source files during blueprint generation
- No Gate 11 commercial paths unless explicitly scoped
- No changes to `registry/format-registry.yaml`

## Stop Conditions

- Stop if `qname_map_path` does not exist (must run spec-literal-qname-to-code-mapping first)
- Stop if blueprint YAML fails to parse
- Stop if any class is missing `spec_qname` (flat class violation)

## Evidence Requirements

- Blueprint YAML artifact path
- Class count
- QName coverage percentage
- Violation count (must be 0)
