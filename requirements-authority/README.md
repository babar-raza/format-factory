# Requirement & Capability Authority Layer

Sprint ID: FORMAT-FACTORY-REQUIREMENT-CAPABILITY-AUTHORITY-LAYER-MWP-001

## Purpose

This directory contains schemas, fixtures, and supporting files for the Canonical Capability Proof Graph authority layer.

## Directory Structure

```
requirements-authority/
  schemas/          JSON Schema Draft 2020-12 definitions
  fixtures/         Golden replay fixture packs (6 packs)
    clean_fods_export/
    fodt_export_not_save_overclaim/
    netpbm_partial_variant_coverage/
    zst_roundtrip_clean/
    sylk_missing_dogfood/
    dif_empirical_only_caveated/
```

## Key Design Rules

- **Netpbm must be retained.** Netpbm (.NET) is a required POC target.
- **SVG must not replace Netpbm.** SVG is not an equivalent format family.
- **ai_draft nodes cannot satisfy any proof class.** All ai_draft nodes are excluded from CapabilityCoverageEvaluator traversal.
- **PocTargetField updated only via proposed sync delta** — never direct mutation.
- **EvidencePackage proves artifacts, not capability truth alone.**
- **Mainstream proposes CapabilityDelta; it does not directly mutate authority.**

## Runtime Tools

All runtime tools are under `tools/requirements_authority/`. See that directory's README for usage.

## Schema Files

| Schema | Purpose |
|--------|---------|
| proof_graph_node.schema.json | All 18 node types |
| proof_graph_edge.schema.json | All 19 edge types |
| product_requirement.schema.json | ProductRequirement nodes |
| capability_claim.schema.json | CapabilityClaim nodes |
| capability_delta.schema.json | CapabilityDelta proposals |
| coverage_record.schema.json | CoverageRecord outputs |
| unsupported_feature.schema.json | UnsupportedFeature records |
| supervisor_verdict_packet.schema.json | 16-field normalized verdict packet |
| mainstream_gap_queue.schema.json | Gap queue entries |
