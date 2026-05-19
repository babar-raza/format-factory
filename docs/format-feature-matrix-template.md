# Format Feature Matrix Template

**Document type:** Template
**Created:** R32 (2026-05-19)
**Purpose:** Every format must eventually have a completed feature matrix. This template defines the sections and fields.

---

## How to use

1. Copy this template to `acquisition-packs/{format}/feature-matrix.yaml` (or .md).
2. Fill in each section honestly based on actual source and tests.
3. Mark features as: supported, partial, unsupported, deferred, not_applicable.
4. Reference the test that proves each supported feature.

---

## Template

```yaml
format_id: {format_id}
display_name: "{display_name}"
matrix_version: "1.0"
last_updated: "YYYY-MM-DD"
updated_by: "{sprint_id}"

identification_and_probe:
  magic_byte_detection:
    status: supported | unsupported | not_applicable
    test_reference: "tests/python/{format}/test_*.py::test_name"
  mime_type_validation:
    status: supported | unsupported | not_applicable
    test_reference: ""
  file_extension_detection:
    status: supported | unsupported | not_applicable
    test_reference: ""
  header_metadata_extraction:
    status: supported | unsupported | not_applicable
    test_reference: ""
  version_detection:
    status: supported | unsupported | not_applicable
    test_reference: ""

load_and_read:
  basic_structure_parse:
    status: supported | partial | unsupported
    test_reference: ""
    notes: ""
  full_content_extraction:
    status: supported | partial | unsupported
    test_reference: ""
    notes: ""
  typed_value_parsing:
    status: supported | partial | unsupported | not_applicable
    test_reference: ""
    notes: "e.g., cell types for spreadsheets, pixel types for images"
  nested_structure_handling:
    status: supported | partial | unsupported | not_applicable
    test_reference: ""
    notes: "e.g., nested lists, grouped shapes, layer hierarchy"
  metadata_extraction:
    status: supported | partial | unsupported
    test_reference: ""
    notes: "e.g., title, author, creation date"

object_model:
  formal_neutral_model:
    status: supported | partial | unsupported
    model_file: ""
    entity_count: 0
    notes: ""
  dataclass_or_schema:
    status: supported | unsupported
    notes: ""
  feature_count_modeled: 0
  feature_count_unmodeled: 0

editing:
  field_level_edit:
    status: supported | unsupported | not_applicable
    test_reference: ""
    notes: "e.g., set cell value, set paragraph text"
  structural_edit:
    status: supported | unsupported | not_applicable
    test_reference: ""
    notes: "e.g., add/remove rows, add/remove paragraphs"
  dom_preservation:
    status: supported | unsupported | not_applicable
    test_reference: ""
    notes: "unknown nodes preserved during edit"

save_and_write:
  same_format_save:
    status: supported | unsupported
    test_reference: ""
  format_fidelity:
    status: supported | partial | unsupported
    notes: "how much of the original format is preserved on save"

export_and_conversion:
  export_formats:
    - format: "csv"
      status: supported | unsupported
      test_reference: ""
    - format: "json"
      status: supported | unsupported
      test_reference: ""
    - format: "html"
      status: supported | unsupported
      test_reference: ""
    # Add more as needed

round_trip:
  parse_write_parse_compare:
    status: supported | unsupported
    test_reference: ""
    notes: ""
  edit_round_trip:
    status: supported | unsupported
    test_reference: ""
    notes: "load -> edit -> save -> reload -> verify edit persisted"

security_and_malformed_input:
  file_size_guard:
    status: supported | unsupported
    max_size: ""
  xxe_protection:
    status: supported | unsupported | not_applicable
    notes: ""
  zip_bomb_protection:
    status: supported | unsupported | not_applicable
    notes: ""
  decompression_bomb_protection:
    status: supported | unsupported | not_applicable
    notes: ""
  dimension_limit:
    status: supported | unsupported | not_applicable
    max_value: ""
  malformed_input_count: 0
  malformed_all_graceful: true | false

corpus_and_spec:
  sample_count: 0
  sample_licenses: "project-owned-synthetic | third-party-licensed | mixed"
  spec_cached: true | false
  spec_normalized: true | false
  spec_sections_mapped_to_model: 0

unsupported_features:
  - feature: "{feature_name}"
    reason: "deferred | complexity | spec_gap | not_in_scope"
    planned: true | false

packaging:
  python_foss:
    pyproject_exists: true | false
    local_build_tested: true | false
    package_name: ""
    version: ""
  net_commercial:
    csproj_exists: true | false
    local_build_tested: true | false
    nuget_package: ""

commercial_readiness:
  applicable: true | false
  capability_level: ""
  commercial_product_ready: false
  g11_status: ""
```

---

## Notes

- This template is aspirational. Not all formats need every field immediately.
- The minimum useful matrix is: identification, load/read, object_model, security, and unsupported_features.
- The matrix is evidence — it must reflect actual source/tests, not plans.
