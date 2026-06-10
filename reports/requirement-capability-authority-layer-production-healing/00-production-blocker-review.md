# Production-Blocker Review — Why the Prior Plan Is Not Execution-Ready

Sprint ID: FORMAT-FACTORY-REQUIREMENT-CAPABILITY-AUTHORITY-LAYER-PRODUCTION-BLOCKER-HEALING-001
Owner: Lane A

## 1. Why is the current plan not production-ready?

The prior PLAN-001 sprint is artifact-first and taskcard-heavy. It describes which files to
create (schemas, YAML registries, governance docs, taskcards) but never defines how capability
truth is established, maintained, and queried. There is no canonical proof graph, no deterministic
evaluator, no proof sufficiency model per capability type, and no lifecycle state machine with
named transition actors. The plan generates artifacts — it does not build a system that can answer
"Is this capability provably ready for POC?" with a deterministic binary result.

## 2. What would fail across repeated reruns?

Gap selection is not deterministic. Without a computed gap queue derived from proof graph state,
two reruns of Mainstream could select different gaps from the same repo. Evidence packages could
be re-declared without re-materializing files. Overclaims would not be decomposed — they would
either block valid evidence wholesale or pass silently. Staleness would not propagate: a changed
spec requirement would not automatically demote downstream capability claims. Different agents
reading different heterogeneous report files would reach different readiness conclusions.

## 3. Why is a schema/taskcard plan insufficient?

Schemas define structure, not truth. A YAML file that validates against a schema can still contain
false claims. A taskcard marks DONE when output files exist — but file existence does not prove
capability readiness. The authority layer requires a runtime evaluator that reads graph state and
computes PASS/FAIL based on invariants, not based on file presence or schema compliance alone.

## 4. Why does the project need a capability proof graph?

Without a graph, the project has no single source of truth for which requirements exist, which
claims support them, what evidence backs each claim, and whether each link in the chain is fresh
and unbroken. Capability state is currently distributed across poc-targets.yaml, supervisor
reports, evidence declarations, test results, and dogfood outputs. There is no way to ask
"why is claim X not POC-ready?" and get a deterministic answer derived from linked nodes.

## 5. How can false PASS still occur under the current plan?

- Evidence package exists but claim is not graph-linked: file presence incorrectly read as proof
- Test passes but is not linked to the claim it supports: coverage appears valid when it is not
- poc-targets.yaml shows PASS status but the requirement it derives from is stale
- Dogfood output exists but was not validated against the expected format output
- ai_draft evidence has not been explicitly excluded as a proof source
- Supervisor reads heterogeneous prose reports and infers PASS without a machine-readable verdict packet

## 6. How can Mainstream still pick the wrong gaps?

Without a computed gap queue, Mainstream uses heuristic judgment — reading poc-targets.yaml,
supervisor reports, and session-resume.md — and selects gaps ad hoc. Two sprints may pick the
same gap (redundant), skip a blocking gap (wrong order), or pick a stretch target instead of a
required one. There is no algorithm that ranks gaps by proof state, POC impact, and smallest
missing proof component.

## 7. How can Supervisor still infer readiness from heterogeneous reports?

Supervisor currently reads prose reports (latest-review.md, evidence-review.md, session-resume.md)
and infers product readiness from text patterns. These reports have different formats, are written
by different agents, and contain claims that may be inconsistent. Without a normalized
supervisor-verdict-packet.json with machine-readable fields (claims_checked, overclaim_risks,
stale_claims, poc_readiness_verdict), the Supervisor cannot determine readiness deterministically.

## 8. How can evidence packages still prove artifacts but not capability truth?

An evidence package materializes files and computes checksums. This proves the files exist and
match their declared content. It does not prove that the files implement the claimed capability,
that tests are linked to the claim they support, that dogfood output is valid for the format, or
that the requirement backing the claim is still current. Evidence proves artifact integrity, not
capability truth.

## 9. What must be preserved from existing systems?

- poc-targets.yaml as a dashboard (not mutated directly — updated only through proposed deltas)
- registry/format-registry.yaml as format context (read-only authority)
- Existing tests, examples, dogfood outputs, and source files (as candidate evidence, not authority)
- Supervisor review packages (as structured input to the verdict packet generator)
- Mainstream dashboard and sprint model (gap queue consumer)
- Skills handoff and transcript model (claim-ID-backed governance layer)
- Acceleration ai_draft packet format (advisory only, never proof)
- Specification Authority outputs (accepted spec requirements and empirical evidence as candidates)
- build_declaration_review_package.py and supervisor toolchain (as infrastructure, not authority)

## 10. What must be redesigned before implementation?

- Canonical proof graph: JSONL nodes + edges with deterministic recomputation
- ProductRequirementRegistry with enforced lifecycle (candidate → accepted/stale/rejected)
- CapabilityClaimRegistry with claim-scope decomposition and proof sufficiency per type
- UnsupportedFeatureLedger (non-blocking limitations visible downstream)
- CapabilityDeltaSystem (Mainstream proposes deltas; never mutates authority directly)
- CapabilityCoverageEvaluator (binary PASS per claim based on graph invariants)
- OverclaimDetector with decomposition (split or narrow, not reject wholesale)
- StalenessInvalidationEngine (propagates from source requirement through graph)
- PocReadinessComputer (per-target verdict from graph state)
- MainstreamGapQueueGenerator (deterministic ranked queue from proof state)
- SupervisorVerdictPacketGenerator (normalized machine-readable packet for Supervisor)
- GoldenReplaySuite (25 test categories, 6 fixture packs, determinism test)
- Migration model (existing assets imported as candidates, not authority)
- Four-stream and two additional consumer contracts (explicit boundaries)

---

RCA_PLAN_IS_PRODUCTION_BLOCKED_UNTIL_PROOF_GRAPH_AND_RUNTIME_MODELS_ARE_ADDED
