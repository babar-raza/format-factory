# Proof Sufficiency Model

Sprint ID: FORMAT-FACTORY-REQUIREMENT-CAPABILITY-AUTHORITY-LAYER-PRODUCTION-BLOCKER-HEALING-001
Owner: Lane B

## Proof Classes (9)

### 1. RequirementProof
- **Required fields:** requirement_id, source_type (spec|empirical|policy), source_ref, status
- **Accepted sources:** SpecRequirementRef, EmpiricalEvidence, ProductPolicyDecision
- **Rejection cases:** source missing; source is ai_draft; requirement_id already superseded
- **Freshness rule:** RequirementProof is stale if source document version has changed since last acceptance
- **Relation to claim status:** Without accepted RequirementProof, CapabilityClaim cannot leave candidate state

### 2. ImplementationProof
- **Required fields:** artifact_path, git_commit_hash, last_modified, function_or_class_ref
- **Accepted sources:** ImplementationArtifact node with non-empty artifact_path
- **Rejection cases:** artifact_path does not exist in repo; artifact is a stub; ai_draft=true
- **Freshness rule:** Stale if source file mtime is newer than recorded last_modified in graph
- **Relation to claim status:** Without ImplementationProof, claim cannot reach implementation_present

### 3. TestProof
- **Required fields:** test_file_path, test_id, last_passed_at, claim_id (must match)
- **Accepted sources:** TestArtifact linked via tested_by edge to the specific CapabilityClaim
- **Rejection cases:** test exists in repo but no graph edge links it to the claim; test last_passed_at is null; ai_draft=true
- **Freshness rule:** Stale if implementation artifact mtime is newer than test last_passed_at
- **Relation to claim status:** Without TestProof, claim cannot reach tests_present

### 4. ExampleProof
- **Required fields:** example_path, format_id, example_type, claim_id
- **Accepted sources:** ExampleArtifact linked via exemplified_by edge
- **Rejection cases:** example_path missing; not linked to claim in graph
- **Freshness rule:** Advisory freshness only; example older than implementation triggers caveat, not demotion
- **Relation to claim status:** ExampleProof required for examples_present; not required for accepted_for_poc unless capability family mandates it

### 5. DogfoodProof
- **Required fields:** dogfood_path, format_id, checksum, produced_at, validator_used, claim_id
- **Accepted sources:** DogfoodArtifact linked via dogfooded_by edge; checksum must be verifiable
- **Rejection cases:** dogfood_path missing; checksum invalid; no validator_used recorded; artifact not linked to claim; ai_draft=true
- **Freshness rule:** Stale if produced_at is older than latest implementation modification
- **Relation to claim status:** Required for dogfood_present; required for coverage_validated when dogfood_required=true for capability family

### 6. EvidencePackageProof
- **Required fields:** zip_path, sha256, manifest_entries (list of artifact paths), materialized=true, claim_links (which claims each artifact proves)
- **Accepted sources:** EvidencePackage with materialized=true and all manifest entries verified against checksums
- **Rejection cases:** materialized=false (declared but not built); checksum mismatch; no claim_links in manifest; ai_draft artifacts inside package
- **Freshness rule:** Stale if any included ImplementationArtifact or TestArtifact was modified after the package was built
- **Relation to claim status:** EvidencePackageProof does not alone satisfy proof sufficiency; it must include graph-linked artifact nodes

### 7. LimitationProof
- **Required fields:** feature_name, severity, claim_id, discovered_at, declared_by
- **Accepted sources:** UnsupportedFeature node linked via limited_by edge
- **Rejection cases:** limitation claimed but no UnsupportedFeature record exists; severity field missing
- **Freshness rule:** No expiry; limitations remain until resolved and edge is removed
- **Relation to claim status:** Required for accepted_with_limitations; if severity=blocking, claim must be blocked, not accepted

### 8. FreshnessProof
- **Required fields:** last_evaluated_at, source_graph_hash, staleness_events (list)
- **Accepted sources:** StalenessInvalidationEngine output for the claim and its dependency chain
- **Rejection cases:** evaluation older than configured freshness_window; staleness_events list is non-empty and unresolved
- **Freshness rule:** Self-referential — FreshnessProof itself must be generated within the freshness_window
- **Relation to claim status:** Without valid FreshnessProof, accepted_for_poc may not be reaffirmed across sprint boundaries

### 9. PolicyProof
- **Required fields:** decision_id, decision_text, decided_by, decided_at, policy_scope
- **Accepted sources:** ProductPolicyDecision node; requires human authorization (decided_by must be a named human)
- **Rejection cases:** decision_id missing; decided_by is ai_draft or automated agent; scope does not cover the claim
- **Freshness rule:** Policy decisions do not expire automatically; must be explicitly superseded
- **Relation to claim status:** Required when claim needs policy_exception (non-standard requirement coverage)

## Proof Sufficiency Levels (10, ordered)

1. **NO_PROOF** — No evidence of any kind exists for the claim
2. **REQUIREMENT_ONLY** — RequirementProof exists; no implementation linked
3. **IMPLEMENTATION_ONLY** — ImplementationProof exists; no tests linked; no requirement
4. **TESTED** — RequirementProof + ImplementationProof + TestProof all present and linked
5. **EXAMPLED** — TESTED + ExampleProof linked
6. **DOGFOODED** — EXAMPLED (or TESTED) + DogfoodProof linked and validated
7. **COVERAGE_VALIDATED** — All required proof classes for the capability type present; no staleness events; evaluator returns PASS
8. **ACCEPTED_FOR_POC** — COVERAGE_VALIDATED + Supervisor has accepted the delta; PocTargetField synced
9. **ACCEPTED_WITH_LIMITATIONS** — ACCEPTED_FOR_POC with known non-blocking UnsupportedFeature records; LimitationProof required
10. **REJECTED_OR_BLOCKED** — Evaluator returned FAIL or blocking UnsupportedFeature prevents acceptance

## Minimum Proof by Capability Type (8)

### load / parse
Minimum: RequirementProof + ImplementationProof + TestProof
Sufficient level: TESTED
Additional: ExampleProof recommended; DogfoodProof not required unless dogfood_required=true

### inspect
Minimum: RequirementProof + ImplementationProof + TestProof
Sufficient level: TESTED
Additional: ExampleProof required for production-facing inspect capabilities

### edit
Minimum: RequirementProof + ImplementationProof + TestProof + ExampleProof
Sufficient level: EXAMPLED
Additional: DogfoodProof required if edit is the primary user-facing capability

### save / write
Minimum: RequirementProof + ImplementationProof + TestProof + DogfoodProof
Sufficient level: DOGFOODED
Additional: Roundtrip TestProof (load → save → load and verify) required; ExampleProof required

### export
Minimum: RequirementProof + ImplementationProof + TestProof + DogfoodProof
Sufficient level: DOGFOODED
Additional: DogfoodArtifact must be in the target format; validator_used must be specified

### dogfood
Minimum: RequirementProof + DogfoodProof + EvidencePackageProof
Sufficient level: COVERAGE_VALIDATED
Additional: dogfood_path must exist and checksum must be verifiable; validator_used must be named

### package / import
Minimum: RequirementProof + ImplementationProof + TestProof
Sufficient level: TESTED
Additional: ExampleProof showing installed-package usage required; DogfoodProof required for commercial packaging claims

### roundtrip
Minimum: RequirementProof + ImplementationProof + TestProof + DogfoodProof + FreshnessProof
Sufficient level: DOGFOODED with FreshnessProof
Additional: Roundtrip TestProof must verify load → edit → save → load produces identical object model; DogfoodArtifact must be the re-loaded output, not the intermediate write
