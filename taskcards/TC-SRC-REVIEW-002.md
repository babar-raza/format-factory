# TC-SRC-REVIEW-002: Canonical Construct Registry Schema

**Lane**: SRC-REVIEW
**Status**: backlog
**Owner**: autonomous agent
**Prerequisites**: none
**item_type**: GOVERNANCE_ASSET

## Objective

Create `shared/qname-registry/schema.yaml` and the full `shared/` directory structure needed for
the canonical QName registry, spec manifests, and generation rules.

## Execution Steps

1. Create `shared/` at repo root (git-tracked, NOT in .gitignore)
2. Create `shared/qname-registry/schema.yaml` with required-field schema for registry entries
3. Create `shared/spec-manifests/` (empty directory)
4. Create `shared/generation-rules/python.yaml` and `dotnet.yaml` (empty stubs)
5. Create `tests/spec_registry/` directory + `__init__.py`
6. Create `tests/spec_registry/test_schema_validation.py`

## Schema Content

```yaml
type: array
items:
  type: object
  required: [qname, namespace_uri, local_name, canonical_class, spec_fact_ref, status, source_layer]
  properties:
    qname:          {type: string, description: "e.g. table:table-cell"}
    namespace_uri:  {type: string}
    local_name:     {type: string}
    canonical_class:{type: string, description: "e.g. Table.TableCell"}
    spec_fact_ref:  {type: string, description: "e.g. FACT-FODT-003"}
    status:         {type: string, enum: [seeded, architecture_only, implementing, implemented, stable, deprecated]}
    source_layer:   {type: string, enum: [Spec, Public, Compat, Reading, Writing, Validation, Conversion, Internal]}
    facade_names:   {type: array, items: {type: string}}
    python_file:    {type: [string, "null"]}
    dotnet_file:    {type: [string, "null"]}
```

## Validation

`python -c "import yaml; yaml.safe_load(open('shared/qname-registry/schema.yaml'))"` — no error

## Evidence Required

- schema.yaml content
- test_schema_validation.py PASS output

## Rollback

Delete `shared/` directory

## Completion Criteria

schema.yaml exists and is valid YAML; test passes; `shared/` is git-tracked
