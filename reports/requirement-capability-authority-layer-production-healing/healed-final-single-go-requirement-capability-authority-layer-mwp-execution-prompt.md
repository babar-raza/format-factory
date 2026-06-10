# Healed Final Single-Go Execution Prompt
# Requirement & Capability Authority Layer — MWP Implementation Sprint

MODE: SINGLE-GO EXECUTION — REQUIREMENT & CAPABILITY AUTHORITY LAYER MWP IMPLEMENTATION
Sprint ID: FORMAT-FACTORY-REQUIREMENT-CAPABILITY-AUTHORITY-LAYER-MWP-001
Date context: 2026-06-04
Authority: This prompt is self-contained. All models, invariants, and rules are embedded below.
Do not reference external documents to determine what to build. This prompt is the specification.

---

## HARD PROHIBITIONS (read before any action)

- NO edits to src/net/**, src/python/**, tests/net/**, tests/python/** (product code is out of scope)
- NO mutation of product-capability-matrix/poc-targets.yaml directly (use PocTargetsSyncProposalGenerator)
- NO mutation of registry/format-registry.yaml
- NO Gate 8, Gate 11, or commercial_product_ready=true claims
- NO commit, NO push (requires explicit user authorization)
- NO package publication
- NO external LLM API calls, NO credential usage
- NO ai_draft content used as proof source
- ALL Python commands must use: PYTHON=".local/venv/Scripts/python"; [ -f "$PYTHON" ] || PYTHON="python"
- ALL absolute paths resolved via: REPO_ROOT=$(git rev-parse --show-toplevel)
- NEVER hardcode C:\Users\prora\... or any Windows username path

---

## MWP GOALS (12)

1. Build a Canonical Capability Proof Graph as JSONL nodes + JSONL edges; deterministically recomputable from registries and imports.
2. Build ProductRequirementRegistry with enforced lifecycle state machine (candidate → accepted/stale/rejected).
3. Build CapabilityClaimRegistry with claim-scope decomposition and proof sufficiency enforced per capability type.
4. Build UnsupportedFeatureLedger for declared non-blocking and blocking limitations.
5. Build CapabilityDeltaSystem: Mainstream proposes CapabilityDelta; never mutates authority directly.
6. Build CapabilityCoverageEvaluator: binary PASS per claim based on graph invariants and proof sufficiency model.
7. Build OverclaimDetector with decomposition (split_claim, narrow_claim, downgrade_status) — not rejection only.
8. Build StalenessInvalidationEngine: propagates staleness from source requirement through the full proof chain.
9. Build PocReadinessComputer: per-target readiness verdict from graph state.
10. Build MainstreamGapQueueGenerator: 11-step deterministic ranked queue from proof state.
11. Build SupervisorVerdictPacketGenerator: normalized 16-field machine-readable JSON packet.
12. Build GoldenReplaySuite: 25 test categories, 6 fixture packs, determinism test (same inputs → same hash).

---

## PRODUCT TARGETS (8)

| Target | Type | Proof Level Required | Dogfood Required |
|--------|------|---------------------|-----------------|
| FODS (.NET) | Commercial required | ACCEPTED_FOR_POC | Yes |
| FODT (.NET) | Commercial required | ACCEPTED_FOR_POC | Yes |
| Netpbm .NET | Commercial required | ACCEPTED_FOR_POC | Yes |
| ZST (Python) | FOSS required | ACCEPTED_FOR_POC | Yes |
| Python Netpbm | FOSS required | ACCEPTED_FOR_POC | Yes |
| SYLK (Python) | FOSS required | ACCEPTED_FOR_POC | Yes |
| DIF (Python) | FOSS substitution | ACCEPTED_FOR_POC | Yes |
| Gnumeric (Python) | FOSS stretch | COVERAGE_VALIDATED | No |

Critical rules:
- Netpbm must be retained. Netpbm (.NET) is a required POC target.
- SVG must not replace Netpbm. SVG is a different format family; adding SVG does not satisfy Netpbm requirements.
- DIF may substitute SYLK only if DIF coverage validates equal or faster.
- Gnumeric counts only if required capabilities are coverage-validated.

---

## PYTHON AND PATH STANDARDS

```bash
# Python with fallback:
PYTHON=".local/venv/Scripts/python"
[ -f "$PYTHON" ] || PYTHON="python"
$PYTHON --version

# Repo root resolution (never hardcode):
REPO_ROOT=$(git rev-parse --show-toplevel)

# Example path construction:
ZIP_PATH="$REPO_ROOT/.local/supervisor/reviews/requirement-capability-authority-layer-production-healing/declaration-review-package.zip"
```

---

## REQUIRED IMPLEMENTATION PATHS (5)

1. `tools/requirements_authority/` — All 13 tool scripts (see tool list below)
2. `tools/requirements_authority/graph/` — JSONL graph files: capability-graph-nodes.jsonl, capability-graph-edges.jsonl
3. `tools/requirements_authority/registries/` — ProductRequirementRegistry.json, CapabilityClaimRegistry.json, UnsupportedFeatureLedger.json
4. `tools/requirements_authority/fixtures/` — 6 golden replay fixture packs (nodes.jsonl + edges.jsonl per pack)
5. `tests/requirements_authority/` — 25 test category test files

---

## REQUIRED TOOLS (13) under tools/requirements_authority/

1. `tools/requirements_authority/build_proof_graph.py` — Builds capability-graph-nodes.jsonl and capability-graph-edges.jsonl from registries and imports
2. `tools/requirements_authority/import_evidence_artifacts.py` — EvidenceGraphImporter: resolves artifact references to graph nodes
3. `tools/requirements_authority/run_coverage_evaluator.py` — CapabilityCoverageEvaluator: binary PASS/FAIL per claim; produces CoverageRecord
4. `tools/requirements_authority/run_overclaim_detector.py` — OverclaimDetector: checks 10 patterns; produces decomposition recommendation
5. `tools/requirements_authority/run_staleness_engine.py` — StalenessInvalidationEngine: checks triggers; creates StalenessEvent nodes; propagates
6. `tools/requirements_authority/compute_poc_readiness.py` — PocReadinessComputer: per-target verdict from graph state
7. `tools/requirements_authority/generate_gap_queue.py` — MainstreamGapQueueGenerator: 11-step algorithm; produces mainstream-gap-queue.json
8. `tools/requirements_authority/generate_supervisor_verdict_packet.py` — SupervisorVerdictPacketGenerator: produces supervisor-verdict-packet.json (16 fields)
9. `tools/requirements_authority/generate_poc_targets_sync_proposal.py` — PocTargetsSyncProposalGenerator: proposes poc-targets.yaml delta; never direct mutation
10. `tools/requirements_authority/validate_delta_schema.py` — Schema validator for CapabilityDelta proposals
11. `tools/requirements_authority/migrate_existing_assets.py` — Imports existing tests, examples, dogfood, reports as candidate graph records
12. `tools/requirements_authority/compute_graph_hash.py` — Computes source_graph_hash (SHA-256 of sorted nodes+edges)
13. `tools/requirements_authority/run_golden_replay.py` — Runs all 6 fixture packs; verifies hash determinism across 3 reruns

---

## REQUIRED OUTPUT ARTIFACTS (13)

1. `tools/requirements_authority/capability-graph-nodes.jsonl` — All graph nodes
2. `tools/requirements_authority/capability-graph-edges.jsonl` — All graph edges
3. `tools/requirements_authority/registries/ProductRequirementRegistry.json` — All ProductRequirements with lifecycle status
4. `tools/requirements_authority/registries/CapabilityClaimRegistry.json` — All CapabilityClaims with scope dimensions
5. `tools/requirements_authority/registries/UnsupportedFeatureLedger.json` — All UnsupportedFeature records
6. `tools/requirements_authority/reports/coverage-report.json` — CoverageRecord per claim; output of CapabilityCoverageEvaluator
7. `tools/requirements_authority/reports/mainstream-gap-queue.json` — Ranked gap entries for Mainstream
8. `tools/requirements_authority/reports/supervisor-verdict-packet.json` — 16-field normalized packet
9. `tools/requirements_authority/reports/poc-readiness-report.json` — Per-target readiness from PocReadinessComputer
10. `tools/requirements_authority/reports/stale-graph-report.json` — Stale nodes from StalenessInvalidationEngine
11. `tools/requirements_authority/reports/recomputation-queue.json` — Claims requiring re-evaluation
12. `tools/requirements_authority/reports/overclaim-report.json` — Overclaim flags with decomposition recommendations
13. `tools/requirements_authority/reports/golden-replay-results.json` — Results of all 6 fixture packs; hash determinism verified

---

## CANONICAL CAPABILITY PROOF GRAPH — EMBEDDED MODEL

### Node Types (18)
ProductRequirement, CapabilityClaim, ImplementationArtifact, TestArtifact, ExampleArtifact,
DogfoodArtifact, EvidencePackage, UnsupportedFeature, EmpiricalEvidence, SpecRequirementRef,
ProductPolicyDecision, ContextPackRef, CoverageRecord, CapabilityDelta, PocTargetField,
StreamHandoff, UsageRecord, StalenessEvent

### Edge Types (19)
derives_from, claims_support_for, implemented_by, tested_by, exemplified_by, dogfooded_by,
evidenced_by, limited_by, blocked_by, supersedes, invalidates, proposed_by, accepted_by,
syncs_to, consumed_by, stale_due_to, narrows, broadens, conflicts_with

### Graph Invariants (8)
(1) Every accepted CapabilityClaim must link via claims_support_for to at least one accepted ProductRequirement.
(2) Every accepted ProductRequirement must link via derives_from to SpecRequirementRef, EmpiricalEvidence, or ProductPolicyDecision.
(3) accepted_for_poc requires: implemented_by + tested_by + evidenced_by(materialized=true) + dogfooded_by if dogfood_required=true.
(4) accepted_with_limitations requires: at least one limited_by → UnsupportedFeature(severity=non_blocking).
(5) Stale nodes cannot support accepted_for_poc transitions; stale requirement demotes all downstream claims.
(6) ai_draft nodes cannot satisfy any proof class; excluded from CapabilityCoverageEvaluator traversal.
(7) EvidencePackage proves only its included artifacts when checksums match and claim_links are present.
(8) PocTargetField updated only through accepted CapabilityDelta via PocTargetsSyncProposalGenerator; never direct mutation.

### Storage
JSONL (one JSON object per line): capability-graph-nodes.jsonl + capability-graph-edges.jsonl
Graph is deterministically recomputable; source_graph_hash = SHA-256(sorted nodes+edges content)

---

## CLAIM DECOMPOSITION RULES (8)
<!-- embedded design models: claim decomposition, stale invalidation, overclaim remediation -->

**Rule 1:** Full support claimed + parse-only proof → split_claim: PARSE accepted + SAVE blocked_missing_implementation
**Rule 2:** Save claimed + export-only proof (different format output) → downgrade_status: create EXPORT claim; reject SAVE
**Rule 3:** Roundtrip claimed + parse-only proof → reject_claim(roundtrip) + narrow_claim → LOAD_EXPORT claim
**Rule 4:** All variants claimed + one variant tested → split_claim by variant; untested variants blocked_missing_test
**Rule 5:** Commercial-ready claimed + helpers only (no format output) → require_dogfood; block readiness
**Rule 6:** Dogfood claimed but artifact not graph-linked → dogfood_present stays false; block coverage_validated
**Rule 7:** Tests exist in repo but no tested_by graph edge → tests_present stays false; graph edge required
**Rule 8:** Blocking UnsupportedFeature contradicts required capability → claim must be blocked; non-blocking → accepted_with_limitations

---

## PROOF SUFFICIENCY BY CAPABILITY TYPE (8)

| Capability Type | Minimum Proof Classes | Sufficient Level |
|----------------|----------------------|-----------------|
| load / parse | RequirementProof + ImplementationProof + TestProof | TESTED |
| inspect | RequirementProof + ImplementationProof + TestProof | TESTED |
| edit | RequirementProof + ImplementationProof + TestProof + ExampleProof | EXAMPLED |
| save / write | RequirementProof + ImplementationProof + TestProof + DogfoodProof | DOGFOODED |
| export | RequirementProof + ImplementationProof + TestProof + DogfoodProof | DOGFOODED |
| dogfood | RequirementProof + DogfoodProof + EvidencePackageProof | COVERAGE_VALIDATED |
| package / import | RequirementProof + ImplementationProof + TestProof + ExampleProof(installed) | EXAMPLED |
| roundtrip | RequirementProof + ImplementationProof + TestProof + DogfoodProof + FreshnessProof | DOGFOODED + Fresh |

Proof sufficiency levels (ordered, 10):
NO_PROOF → REQUIREMENT_ONLY → IMPLEMENTATION_ONLY → TESTED → EXAMPLED → DOGFOODED →
COVERAGE_VALIDATED → ACCEPTED_FOR_POC → ACCEPTED_WITH_LIMITATIONS → REJECTED_OR_BLOCKED

---

## GOLDEN REPLAY FIXTURE PACKS (6)

### Pack A: Clean FODS Export Claim
Input: ProductRequirement(accepted) + CapabilityClaim(fods-export) + ImplementationArtifact + TestArtifact(fresh) + DogfoodArtifact(checksum valid) + all required edges
Expected: CoverageRecord=clean; verdict=ACCEPT_PRODUCT_PROGRESS

### Pack B: FODT Export-Only-Not-Save Overclaim
Input: CapabilityClaim(operation=save) + DogfoodArtifact in CSV format (not FODT)
Expected: CoverageRecord=blocked_overclaim; verdict=REJECT_OVERCLAIM; remediation=downgrade_status(export)

### Pack C: Netpbm Partial Variant Coverage
Input: CapabilityClaim(variant=all_variants) + TestArtifact for P3 only; no P6 test
Expected: CoverageRecord=blocked_overclaim; verdict=REJECT_OVERCLAIM; remediation=split_claim(P3/P6)

### Pack D: ZST Roundtrip Clean
Input: ProductRequirement(empirical_only) + CapabilityClaim(roundtrip) + all proof classes including DogfoodArtifact(byte-identical)
Expected: CoverageRecord=partial_with_known_limitations(empirical caveat); verdict=ACCEPT_WITH_LIMITATIONS

### Pack E: SYLK Missing Dogfood
Input: ProductRequirement(accepted) + CapabilityClaim(sylk-csv-export, dogfood_required=true) + ImplementationArtifact + TestArtifact; no DogfoodArtifact
Expected: CoverageRecord=blocked_missing_dogfood; verdict=BLOCK_MISSING_DOGFOOD

### Pack F: DIF Empirical-Only Caveated
Input: ProductRequirement(empirical_only, accepted_with_caveat) + CapabilityClaim(dif-parse) + ImplementationArtifact + TestArtifact + DogfoodArtifact(validator_used=manual)
Expected: CoverageRecord=partial_with_known_limitations; verdict=ACCEPT_WITH_LIMITATIONS

Determinism requirement: all 6 packs must produce identical source_graph_hash and identical verdict across 3 independent reruns. COVERAGE_CLEAN must appear in output when all invariants pass.

---

## REQUIRED TEST CATEGORIES (≥10 named)

1. test_clean_proof_graph
2. test_missing_requirement_blocks_claim
3. test_missing_implementation_blocks_claim
4. test_missing_test_blocks_claim
5. test_missing_dogfood_blocks_when_required
6. test_stale_implementation_demotes_claim
7. test_ai_draft_rejected_as_proof
8. test_overclaim_full_support_decomposed
9. test_accepted_with_limitations_requires_unsupported_feature
10. test_poc_targets_not_mutated_directly
11. test_delta_rejected_with_correct_reason
12. test_supervisor_verdict_packet_has_all_16_fields
13. test_gap_queue_deterministic_across_reruns
14. test_staleness_propagates_through_chain
15. test_empirical_only_accepted_with_caveat

---

## MIGRATION PROTOCOL

Before building new graph nodes, run migrate_existing_assets.py to:
1. Import tests/net/**, tests/python/** as TestArtifact candidates (status: candidate)
2. Import examples/** as ExampleArtifact candidates
3. Import poc-targets.yaml as candidate PocTargetField nodes (not authority)
4. Import source-change ledgers as StalenessEvent candidates
5. Mark all imported nodes with import_status=imported_candidate
6. ai_draft nodes from Acceleration reports: mark ai_draft=true

---

## DELTA PROMOTION FLOW (summary)

Mainstream proposes CapabilityDelta → schema_validated → evidence_imported (EvidenceGraphImporter) → coverage_computed (CapabilityCoverageEvaluator) → accepted or rejected → if accepted: PocTargetsSyncProposalGenerator emits proposal → Supervisor accepts → PocTargetField updated via syncs_to edge.

Never direct mutation of poc-targets.yaml. PocTargetsSyncProposalGenerator proposes; Supervisor authorizes.

---

## STALENESS INVALIDATION SUMMARY

12 triggers (embedded): spec_changed, empirical_changed, requirement_changed, impl_changed_after_coverage, test_changed_after_coverage, test_log_older_than_source, dogfood_older_than_impl, evidence_missing_proof, context_pack_stale, unsupported_feature_changed, claim_scope_changed, policy_changed.

Propagation: requirement stale → claims stale → coverage records invalidated → poc target proposals blocked.

---

## OVERCLAIM REMEDIATION SUMMARY

10 patterns. Never wholesale-reject without attempting decomposition first.
Enum: narrow_claim, split_claim, add_unsupported_feature, require_dogfood, require_tests, require_implementation, downgrade_status, mark_empirical_only, request_policy_decision, reject_claim.

---

## FINAL RESPONSE CONTRACT

After completing all 12 goals, respond with a structured JSON-compatible summary containing all of:

```
{
  "sprint_id": "FORMAT-FACTORY-REQUIREMENT-CAPABILITY-AUTHORITY-LAYER-MWP-001",
  "verdict": "<one of: COVERAGE_CLEAN | COVERAGE_PARTIAL_WITH_CAVEATS | COVERAGE_BLOCKED>",
  "tools_built": ["list of 13 tool paths"],
  "output_artifacts": ["list of 13 output artifact paths"],
  "graph_hash": "<source_graph_hash sha256>",
  "coverage_records": {"total": N, "clean": N, "blocked": N, "partial": N},
  "poc_readiness_per_target": {"fods": "...", "fodt": "...", ...},
  "golden_replay_result": {"total_packs": 6, "all_deterministic": true|false, "COVERAGE_CLEAN": true|false},
  "false_pass_risks_found": N,
  "false_stop_risks_found": N,
  "evidence_declaration_path": ".local/evidences/...",
  "review_package_path": "<absolute path from REPO_ROOT>",
  "review_package_sha256": "<sha256 hex>"
}
```

### Allowed Verdict Values (3)

1. **COVERAGE_CLEAN** — All required claims for all required POC targets are coverage_validated with no blocking issues; no stale events; proof graph is internally consistent.

2. **COVERAGE_PARTIAL_WITH_CAVEATS** — One or more claims are accepted_with_limitations; UnsupportedFeature records are declared and visible; no blocking overclaims; some empirical_only requirements.

3. **COVERAGE_BLOCKED** — One or more required POC targets have claims that are blocked (missing proof, stale, overclaim, hidden limitation). Mainstream gap queue identifies next actions.

---

## SCOPE GUARD

No files outside the following paths may be created or modified by this sprint:
- tools/requirements_authority/**
- tests/requirements_authority/**
- tools/requirements_authority/registries/**
- tools/requirements_authority/reports/**
- tools/requirements_authority/fixtures/**
- .local/evidences/requirement-capability-authority-layer-mwp-001/**
- .local/supervisor/reviews/requirement-capability-authority-layer-mwp-001/**

Forbidden: src/net/**, src/python/**, tests/net/**, tests/python/**,
product-capability-matrix/poc-targets.yaml (write), registry/format-registry.yaml (write).

At sprint close: run git status --short and verify no M or A entries outside allowed paths.

---

## AUTHORITY BOUNDARY REMINDERS

- Mainstream produces evidence; does not accept claims.
- Acceleration produces ai_draft; ai_draft rejected as proof.
- Skills produces governed handoffs; does not accept claims.
- Supervisor accepts CapabilityDelta with coverage_computed=PASS; must not infer PASS from prose.
- Specification Authority sources requirements; does not accept POC claims.
- Evidence proves artifacts; does not prove capability truth in isolation.
- accepted_with_limitations must be visible to all downstream consumers.
