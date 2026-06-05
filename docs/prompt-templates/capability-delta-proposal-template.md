# Capability Delta Proposal Template

**Purpose:** Mainstream fills this template when proposing that a capability claim be promoted based on completed implementation, test, and dogfood work.
**Consumer:** CapabilityDeltaSystem → schema validation → EvidenceGraphImporter → CapabilityCoverageEvaluator → Supervisor
**Authority:** Mainstream is a contributor of evidence only. This template is a proposal, not an acceptance.

---

## Delta Metadata

- delta_id: (assigned by system; leave blank)
- proposed_at: (ISO8601 datetime)
- proposed_by: mainstream
- sprint_id: (sprint ID that produced this work)
- status: proposed

## Claim Reference

- claim_id: (e.g., claim-fods-export-001)
- target_product: (e.g., fods, fodt, netpbm-net, zst, sylk, dif)
- format_id: (e.g., fods, ppm, sylk)
- operation: (one of: load, parse, inspect, edit, save, write, export, import, roundtrip, validate, package, dogfood)
- direction: (one of: read_only, write_only, read_write, export_only, import_only, transform)
- fidelity: (one of: structure_only, content_only, metadata_only, formatting_partial, formatting_preserved, lossless, lossy, declared_limited)
- variant: (e.g., P3, P6, all_variants, single_sheet)
- poc_scope: (required | stretch | not_applicable)

## Evidence References

- changed_source_files: (list of file paths; leave empty if no source changes)
- new_test_files: (list of test file paths added or updated)
- dogfood_artifact_path: (path to produced format output file; null if not applicable)
- dogfood_checksum: (SHA-256 of dogfood file; null if not applicable)
- dogfood_validator_used: (description of how the dogfood output was validated; null if not applicable)
- evidence_package_ref: (path to evidence-declaration.yaml; null if not yet built)

## Unsupported Features (declared limitations)

- unsupported_features: (list of {feature_name, severity: blocking|non_blocking}; empty list if none)

## Proposed Claim Status

- proposed_new_status: (e.g., coverage_validated, accepted_for_poc, accepted_with_limitations)
- promotion_rationale: (1-2 sentence explanation of why this claim is ready for the proposed status)

## Phrasing Contract

This delta says: "here is evidence to promote this claim."
This delta does NOT say: "this claim is now accepted" or "this capability is proven."
The CapabilityCoverageEvaluator and Supervisor make acceptance decisions; Mainstream provides evidence.
