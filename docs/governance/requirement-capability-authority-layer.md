# Requirement & Capability Authority Layer

**Added:** 2026-06-04
**Authority:** plans/master-plan.md Section 44.3
**Source:** memory/67-local-memory-governance-sync-20260604.md Section 4
**Status:** PLAN_HEALED_READY_FOR_MWP_EXECUTION

## Purpose

Accountability bridge between specification/source requirements and product readiness.

**Core question:** "Can we honestly claim this capability is supported, and what proves it?"

## Relationship to Other Layers

| Layer | Says |
|---|---|
| Specification Authority Layer | What **should** be true (spec requirements) |
| Requirement & Capability Authority Layer | What we **claim** is true + whether it is **proven enough for POC** |

## Does NOT Replace Existing Systems

This layer **wraps** existing systems with proof logic. Preserve:
- `product-capability-matrix/poc-targets.yaml` (readable dashboard)
- `registry/format-registry.yaml` (format context)
- Source code, tests, examples, dogfood outputs
- Evidence declarations/manifests/packages
- Source-change ledgers, Supervisor review packages

## Three Requirement Source Types

| Type | Use case |
|---|---|
| `spec_backed` | Requirement derived from format specification |
| `empirical_sample_backed` | Requirement derived from observed format samples |
| `product_policy_exception` | Requirement from product decision (allows progress while Spec Authority matures) |

## 11 Key Subsystems

1. ProductRequirementRegistry
2. CapabilityClaimRegistry
3. UnsupportedFeatureLedger
4. CapabilityDeltaSystem
5. CapabilityCoverageValidator / CapabilityCoverageEvaluator
6. OverclaimDetector
7. StalenessDetector / InvalidationEngine
8. PocReadinessComputer
9. MainstreamGapQueueGenerator
10. SupervisorVerdictInputGenerator / SupervisorVerdictPacketGenerator
11. PocTargetsSyncProposalGenerator

## Canonical Capability Proof Graph

### 18 Node Types
ProductRequirement, CapabilityClaim, ImplementationArtifact, TestArtifact, ExampleArtifact, DogfoodArtifact, EvidencePackage, UnsupportedFeature, EmpiricalEvidence, SpecRequirementRef, ProductPolicyDecision, ContextPackRef, CoverageRecord, CapabilityDelta, PocTargetField, StreamHandoff, UsageRecord, StalenessEvent

### 19 Edge Types
derives_from, claims_support_for, implemented_by, tested_by, exemplified_by, dogfooded_by, evidenced_by, limited_by, blocked_by, supersedes, invalidates, proposed_by, accepted_by, syncs_to, consumed_by, stale_due_to, narrows, broadens, conflicts_with

### 8 Graph Invariants
1. Accepted claims need accepted ProductRequirement.
2. Accepted ProductRequirement needs spec requirement, empirical evidence, or product policy decision.
3. `accepted_for_poc` claims need implementation + tests + evidence (+ dogfood if required).
4. `accepted_with_limitations` needs UnsupportedFeature node.
5. Stale nodes cannot support new `accepted_for_poc`.
6. `ai_draft` nodes cannot satisfy proof.
7. EvidencePackage proves only included artifacts, not truth by itself.
8. PocTargetField updated only via proposed sync delta — NOT directly.

## Claim-Scope Decomposition (12 Dimensions)
product_id, format_id, operation, direction, fidelity, variant, object_model_scope, io_scope, error_scope, performance_scope, platform_scope, POC_scope

## Overclaim Remediation

| Overclaim | Remediation |
|---|---|
| "support format" with only parse proof | Narrow to parse-only |
| "save" claimed with export proof only | Downgrade to export |
| "roundtrip" with parse only | Reject roundtrip, create parse claim |
| All variants claimed, one tested | Create variant-specific claims |
| Full support with partial proof | Accepted partial + blocked remainder |

## Proof Sufficiency Levels (10)

NO_PROOF → REQUIREMENT_ONLY → IMPLEMENTATION_ONLY → TESTED → EXAMPLED → DOGFOODED → COVERAGE_VALIDATED → ACCEPTED_FOR_POC → ACCEPTED_WITH_LIMITATIONS → REJECTED_OR_BLOCKED

## Minimum Proof by Capability Type

| Type | Minimum Required |
|---|---|
| Load/parse | requirement + implementation + tests + sample/input evidence |
| Edit | inspect proof + mutation tests + save/export proof |
| Save/write | requirement + implementation + roundtrip/readback test + output artifact |
| Export | requirement/policy + implementation + output artifact + validator/readback |
| Dogfood | real output + validation + evidence package |
| Package/import | package/import test + version metadata + source smoke |
| Roundtrip | comparison policy + readback + fidelity/limitation declaration |

## Authority Chain

1. Mainstream **proposes** CapabilityDelta
2. Skills **produces** handoffs/transcripts
3. Acceleration **recommends** `ai_draft`
4. Supervisor/validator **accepts or rejects**
5. Direct truth update / direct `poc-targets.yaml` mutation: **NOT ALLOWED** without proposed sync delta

## Current Plan Status

**Plan:** `delegated-roaming-whistle.md`
**Review verdict:** REQUIREMENT_CAPABILITY_AUTHORITY_LAYER_PLAN_HEALED_READY_FOR_MWP_EXECUTION
**Healing sprint:** `FORMAT-FACTORY-REQUIREMENT-CAPABILITY-AUTHORITY-LAYER-PRODUCTION-BLOCKER-HEALING-001` — COMPLETE
**Healing outputs:** `reports/requirement-capability-authority-layer-production-healing/` (39 files)
**Next sprint:** `FORMAT-FACTORY-REQUIREMENT-CAPABILITY-AUTHORITY-LAYER-MWP-001` (use healed prompt)

See memory/67-local-memory-governance-sync-20260604.md Section 4 for full detail.
