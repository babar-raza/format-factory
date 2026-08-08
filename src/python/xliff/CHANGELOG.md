# Changelog

## 0.2.0.dev0

- Add the `format_factory.xliff` production namespace and common lifecycle API.
- Add bounded XLIFF 2.0/2.1 parsing, typed core models, extension preservation,
  validation diagnostics, deterministic writing, and reproducible packaging.
- Add 6 independently pluggable segment QA checks, reported separately from
  `validate()`'s own conformance diagnostics (`run_qa_checks`, `QA_CHECKS`).
- Add a whole-document `xml:space`/`xml:lang` resolver
  (`effective_attributes_by_unit`) and its underlying reusable resolution
  rules.
- Add fail-closed translation state-transition checking between two document
  snapshots (`check_state_transitions`, `DEFAULT_STATE`, `TransitionPolicy`).
- Add a template merge/drift-check contract for round-tripping translations
  into a caller's own non-XLIFF format (`MergeAdapter`, `Skeleton`,
  `compute_source_digest`, `merge_with_drift_check`, `TemplateMergeAdapter`).
- Add standard-module coverage reporting and bundled OASIS XSD/Schematron/NVDL
  schema validation (`module_coverage_manifest`, `is_production_complete`,
  `schema_validate`, `full_schema_validate`).
- Add LOSSLESS/CANONICAL preservation modes with pre-commit loss disclosure
  (`dumps`, `PreservationMode`, `check_preservation`).
- Add configurable resource limits (`XLIFF_DEFAULT_LIMITS`) enforced
  incrementally during parsing.
