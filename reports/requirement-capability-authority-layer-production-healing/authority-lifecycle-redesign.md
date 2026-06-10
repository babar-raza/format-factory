# Authority Lifecycle Redesign

Sprint ID: FORMAT-FACTORY-REQUIREMENT-CAPABILITY-AUTHORITY-LAYER-PRODUCTION-BLOCKER-HEALING-001
Owner: Lane C

## ProductRequirement Lifecycle (10 states)

States: candidate → source_linked → verification_pending → accepted | accepted_with_caveat | empirical_only | policy_exception → stale | rejected | superseded

| State | Description | Actor who may trigger | Blocking condition |
|-------|-------------|----------------------|--------------------|
| candidate | Requirement proposed but not yet sourced | Mainstream, Specification Authority, EvidenceGraphImporter | None — initial state |
| source_linked | SpecRequirementRef or EmpiricalEvidence linked via derives_from edge | Specification Authority, EvidenceGraphImporter | source node must exist in graph |
| verification_pending | Source linked; awaiting human or policy review | Specification Authority | Cannot auto-advance if source is ai_draft |
| accepted | Requirement verified against spec or empirical source | Specification Authority (human) | source_linked must be true; source must not be ai_draft |
| accepted_with_caveat | Accepted but with a known gap or ambiguity in source | Specification Authority | Caveat must be documented in metadata |
| empirical_only | No formal spec; backed by empirical sample only | Specification Authority | Caveat: empirical_only requirements support empirical_only claims only |
| policy_exception | Accepted via ProductPolicyDecision (no spec or empirical source) | ProductPolicyDecision (requires human decision_id) | decision_id must be present and non-null |
| stale | Source has changed; requirement must be re-verified | StalenessInvalidationEngine (automated trigger) | All downstream claims must be demoted to stale |
| rejected | Requirement found invalid or out of scope | Specification Authority | All linked claims must be demoted to blocked |
| superseded | Replaced by a newer ProductRequirement version | Specification Authority | Superseding requirement must be in accepted state |

## CapabilityClaim Lifecycle (13 states)

States: candidate → requirement_linked → implementation_present → tests_present → examples_present → dogfood_present → coverage_validated → accepted_for_poc | accepted_with_limitations → stale | rejected | blocked | superseded

| State | Description | Actor who may trigger | Blocking condition |
|-------|-------------|----------------------|--------------------|
| candidate | Claim proposed but no requirement or implementation linked | Mainstream, EvidenceGraphImporter | None — initial state |
| requirement_linked | claims_support_for edge to accepted ProductRequirement present | Mainstream (via delta), EvidenceGraphImporter | ProductRequirement must be in accepted/accepted_with_caveat/empirical_only/policy_exception |
| implementation_present | ImplementationArtifact linked via implemented_by edge | EvidenceGraphImporter, Mainstream (delta) | Artifact must exist in repo; must not be stub |
| tests_present | TestArtifact linked via tested_by edge | EvidenceGraphImporter | TestArtifact must have last_passed_at not null |
| examples_present | ExampleArtifact linked via exemplified_by edge | EvidenceGraphImporter | ExampleArtifact must exist in repo |
| dogfood_present | DogfoodArtifact linked via dogfooded_by edge | EvidenceGraphImporter | DogfoodArtifact must have valid checksum and validator_used |
| coverage_validated | CapabilityCoverageEvaluator has run and returned PASS for all required proof classes | CapabilityCoverageEvaluator (automated) | All required proof classes for capability type must pass; no stale events |
| accepted_for_poc | Supervisor has accepted delta and PocTargetField synced | Supervisor (via accepted CapabilityDelta) | coverage_validated must be true; no stale events; delta in state accepted |
| accepted_with_limitations | Accepted for POC with declared non-blocking UnsupportedFeature records | Supervisor (via accepted CapabilityDelta) | At least one UnsupportedFeature with severity=non_blocking linked |
| stale | Dependency (requirement, implementation, test, dogfood) has changed since coverage_validated | StalenessInvalidationEngine | All accepted_for_poc claims backed by stale node are demoted |
| rejected | Claim found to be overclaimed or invalid | CapabilityCoverageEvaluator, OverclaimDetector | Rejected claims must be decomposed or removed |
| blocked | Blocking UnsupportedFeature or missing required proof prevents acceptance | OverclaimDetector, CapabilityCoverageEvaluator | Blocked claims cannot become accepted_for_poc until blocker is resolved |
| superseded | Replaced by a narrower or broader claim | Mainstream (via delta) | Superseding claim must be in requirement_linked or higher state |

## CapabilityDelta Lifecycle (8 states)

States: proposed → schema_validated → evidence_imported → coverage_computed → accepted | rejected | needs_rework → stale

| State | Description | Actor who may trigger | Blocking condition |
|-------|-------------|----------------------|--------------------|
| proposed | Mainstream submits a delta proposal referencing work done | Mainstream only | Delta must reference specific claim_id and operation |
| schema_validated | Delta validated against capability-delta-proposal-template schema | Schema validator (automated) | Schema must pass; no unfilled template tokens |
| evidence_imported | EvidenceGraphImporter has linked all artifact references in delta to graph nodes | EvidenceGraphImporter (automated) | All referenced artifacts must resolve to files in repo |
| coverage_computed | CapabilityCoverageEvaluator has run on the linked claim | CapabilityCoverageEvaluator (automated) | CoverageRecord created; PASS or FAIL recorded |
| accepted | Supervisor has reviewed coverage_computed result and accepted the delta | Supervisor (with validation output) | coverage_computed must be PASS; no blocking issues |
| rejected | Evaluator or Supervisor found delta invalid | Supervisor, CapabilityCoverageEvaluator | Rejection reason must be recorded; claim reverts to prior state |
| needs_rework | Delta is partially valid but requires corrections | Supervisor | Rework guidance must be provided; Mainstream must resubmit |
| stale | Delta was accepted but a StalenessEvent has since invalidated one of its artifact nodes | StalenessInvalidationEngine | Stale delta cannot reaffirm claim; new delta required |

## CoverageRecord Lifecycle (12 states)

States: not_checked → clean | partial_with_known_limitations | blocked_missing_requirement | blocked_missing_implementation | blocked_missing_test | blocked_missing_example | blocked_missing_dogfood | blocked_stale_requirement | blocked_overclaim | blocked_missing_evidence | requires_policy_decision

| State | Description |
|-------|-------------|
| not_checked | CapabilityCoverageEvaluator has not yet run for this claim |
| clean | All required proof classes present; no staleness; PASS |
| partial_with_known_limitations | PASS with non-blocking UnsupportedFeature records; accepted_with_limitations result |
| blocked_missing_requirement | No accepted ProductRequirement linked to this claim |
| blocked_missing_implementation | No ImplementationArtifact linked; or artifact is a stub |
| blocked_missing_test | No TestArtifact linked to this claim in the graph |
| blocked_missing_example | ExampleArtifact required for capability type but none linked |
| blocked_missing_dogfood | DogfoodArtifact required (dogfood_required=true) but none linked or validated |
| blocked_stale_requirement | ProductRequirement backing this claim is in state stale |
| blocked_overclaim | OverclaimDetector flagged this claim; decomposition required |
| blocked_missing_evidence | EvidencePackage required but not materialized or not linked |
| requires_policy_decision | Claim needs ProductPolicyDecision but none recorded |

## Transition Rules (all objects)

- **Validator may move claim to coverage_validated** only when CapabilityCoverageEvaluator returns PASS for all required proof classes.
- **Mainstream may propose delta only** — Mainstream cannot directly accept claims, mutate poc-targets, or record accepted_for_poc.
- **Acceleration may produce ai_draft suggestion only** — Acceleration cannot trigger any lifecycle transition. ai_draft nodes are never traversed in proof evaluation.
- **Skills may produce handoff/delta template only** — Skills cannot accept claims or move any state machine forward.
- **Supervisor may accept/downgrade with validation output** — Supervisor must have coverage_computed PASS from evaluator before accepting; prose is insufficient.
- **Stale dependency demotes accepted_for_poc → stale or needs_revalidation** — Automated; StalenessInvalidationEngine triggers this.
- **accepted_with_limitations requires UnsupportedFeature records** — Cannot be accepted_with_limitations without at least one non-blocking UnsupportedFeature node linked.
- **policy_exception requires decision ID** — ProductPolicyDecision must have a non-null decision_id assigned by a named human.
