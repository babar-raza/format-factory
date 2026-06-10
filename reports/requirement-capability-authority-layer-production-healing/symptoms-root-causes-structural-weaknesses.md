# Symptoms, Root Causes, and Structural Weaknesses

Sprint ID: FORMAT-FACTORY-REQUIREMENT-CAPABILITY-AUTHORITY-LAYER-PRODUCTION-BLOCKER-HEALING-001
Owner: Lane A

## Symptoms

- Capability status is spread across multiple files: poc-targets.yaml, supervisor reports, evidence declarations, test results, dogfood outputs — no single query returns unified state
- PASS verdict can be issued without a uniform proof chain: file existence alone can trigger acceptance
- Dogfood is inconsistently required: some capabilities are marked PASS without dogfood output
- Unsupported features are invisible: no ledger of declared limitations, so limitations are hidden downstream
- Evidence packages prove file existence, not capability truth: checksums and manifests do not link to claims
- Gap selection is ad hoc: Mainstream reads heterogeneous reports and selects gaps by judgment, not algorithm
- Acceleration ranks gaps without authority state: ai_draft recommendations are not grounded in proof graph
- Skills handoffs are missing claim IDs: handoff templates do not reference specific claim identifiers
- Supervisor infers from heterogeneous reports: prose patterns rather than machine-readable verdict fields
- Stale dependencies do not consistently invalidate: a changed requirement does not propagate demotion to downstream claims
- Sprint reruns can choose different gaps for the same proof state: no deterministic gap queue
- Evidence repair is mistaken for product progress: polishing metadata is counted as sprint output

## Root Causes

- No canonical proof graph: no directed graph linking ProductRequirements through CapabilityClaims to evidence
- No single claim registry with enforced lifecycle: claims are scattered across YAML files with no state machine
- No deterministic evaluator: no binary test that reads graph state and returns PASS/FAIL per invariant
- No claim-scope decomposition: overbroad claims are rejected or accepted wholesale; valid partial evidence is wasted
- No proof sufficiency model per family: no definition of what minimum evidence is required per capability type
- No migration model: existing assets (tests, dogfood, reports) are not imported as candidate graph records
- No graph link from requirement to source/test/dogfood/evidence: the chain is broken at every segment
- No freshness propagation: a staleness event at the requirement level does not propagate through the graph
- No normalized Supervisor packet: Supervisor input is prose with no machine-readable fields
- No computed gap queue: gap selection has no algorithm, no ranking, and no deterministic output
- No golden replay suite: there is no test that proves the evaluator gives the same result on the same input
- No overclaim decomposition: overclaim detector rejects without splitting valid from invalid evidence

## Structural Weaknesses

- Source outruns requirement proof: implementation is added before a spec or empirical requirement backs the claim
- Tests pass but do not prove capability: tests exist but are not linked to specific capability claims in the graph
- Dogfood is missing while capability looks green: dogfood_required is not enforced at coverage validation time
- Claims are too broad: "supports format X" encompasses load, parse, edit, save, export, roundtrip without decomposition
- Limitations are hidden: unsupported features are not declared in a visible ledger and are omitted from downstream consumers
- Stale requirements support claims: requirements accepted months ago support claims without freshness verification
- Empirical evidence is confused with official specification: empirical samples are treated as spec-backed without caveat
- ai_draft can influence readiness: Acceleration outputs are not explicitly excluded as proof sources
- Reruns choose different gaps: without a computed queue, different agents on different days make different selections
- Evidence becomes the work instead of proof: evidence declaration and package building are counted as sprint deliverables rather than proof mechanisms
- poc-targets.yaml is mutated directly: status fields are written without going through a proposed delta and validator pass
- Accepted_with_limitations is not propagated: downstream consumers do not see declared limitation records
