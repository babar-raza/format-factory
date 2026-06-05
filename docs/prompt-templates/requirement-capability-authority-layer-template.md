# Requirement & Capability Authority Layer Execution Template

**Added:** 2026-06-04
**Sprint ID pattern:** FORMAT-FACTORY-REQUIREMENT-CAPABILITY-AUTHORITY-LAYER-<PHASE>-<N>
**Reference:** docs/governance/requirement-capability-authority-layer.md

## Prerequisites

This template should only be used when the plan has verdict `REQUIREMENT_CAPABILITY_AUTHORITY_LAYER_PLAN_HEALED_READY_FOR_MWP_EXECUTION`.

Current plan status: PLAN_NEEDS_REPAIR (plan: `delegated-roaming-whistle.md`)
Healing prompt ID: `FORMAT-FACTORY-REQUIREMENT-CAPABILITY-AUTHORITY-LAYER-PRODUCTION-BLOCKER-HEALING-001`

## Mission

Build the Requirement & Capability Authority Layer proof graph, registries, validators, gap queue, and Supervisor verdict input.

NOT: product source implementation / direct poc-targets.yaml mutation / gate approval / external tool install.

## Hard Prohibitions
- No src/net/* or src/python/* edits
- No direct product-capability-matrix/poc-targets.yaml mutation (proposed delta only)
- No registry/format-registry.yaml mutation
- No gate approval, push, commit, publish
- No external tool install

## Allowed Paths
- requirements-authority/** (new)
- tools/requirements_authority/** (new)
- tests/supervisor/test_requirement_capability_authority_layer.py
- reports/requirement-capability-authority-layer-production-healing/**
- .local/evidences/requirement-capability-authority-layer-<N>/**
- .local/supervisor/reviews/requirement-capability-authority-layer-<N>/**

## Required Deliverables

### Proof Graph
- Node types: 18 (see governance doc)
- Edge types: 19 (see governance doc)
- Invariant enforcement: 8 invariants
- Schema-backed, versioned

### Registries
- ProductRequirementRegistry (schema + YAML/JSON storage)
- CapabilityClaimRegistry (schema + YAML/JSON storage)
- UnsupportedFeatureLedger

### Validators
- CapabilityCoverageValidator
- OverclaimDetector
- StalenessDetector

### Gap Queue
- MainstreamGapQueueGenerator (using POC families from poc-targets.yaml)
- Output: queue with gap_id, target_product, claim_id, missing_proof_type, next_action, lane, validation_command

### Supervisor Verdict Input
- SupervisorVerdictPacketGenerator
- Output: packet with poc_readiness_verdict, overclaim_risks, stale_claims, false_pass/stop risks

### PocTargetsSyncProposalGenerator
- Output: proposed delta (NOT direct mutation)
- Must be labeled `proposed_delta: true`

## POC Families to Process (initial)
- FODS (all 5 capability families)
- FODT (all 5 capability families)
- Netpbm .NET (all 5 capability families)
- ZST (4 families)
- Python Netpbm PBM/PGM/PPM (5 families)
- SYLK (5 families)
- DIF (5 families)

## Evidence Closeout
1. `.local/venv/Scripts/python tools/supervisor/autonomous_cycle.py --declaration .local/evidences/requirement-capability-authority-layer-<N>/evidence-declaration.yaml`
2. `.local/venv/Scripts/python tools/supervisor/build_declaration_review_package.py --declaration .local/evidences/requirement-capability-authority-layer-<N>/evidence-declaration.yaml`

## Allowed Verdicts
- `REQUIREMENT_CAPABILITY_AUTHORITY_LAYER_PHASE1_COMPLETE`
- `REQUIREMENT_CAPABILITY_AUTHORITY_LAYER_PHASE1_PARTIAL`
- `REQUIREMENT_CAPABILITY_AUTHORITY_LAYER_PHASE1_BLOCKED`

## Final Response Contract
- Exact verdict
- Proof graph: node count, edge count, invariants enforced
- Registries: product requirement count, capability claim count
- Gap queue: gap count per family
- Supervisor verdict packet: poc_readiness_verdict
- PocTargetsSyncProposal: proposed delta path (NOT mutation)
- Test count: passed/failed/skipped
- Evidence declaration path
- Review package absolute path: C:\Users\prora\...\
- Review package SHA-256
- Explicit: no direct poc-targets.yaml mutation, no product source edits, no push, no commit
