# Local Memory / Governance Sync — 2026-06-04

**Sprint:** FORMAT-FACTORY-LOCAL-MEMORY-GOVERNANCE-SYNC-20260604-001
**Type:** Durable knowledge synchronization from ChatGPT project memory
**Date:** 2026-06-04

This entry captures the full memory payload from ChatGPT project memory synchronization. Future agents must read this before acting to avoid contradicting decisions made by the user.

---

## Section 1: Independent Layer Strategy

**Core principle:**
> "Anything that repeatedly influences product decisions must become an independent, verifiable authority/support layer."

A layer is justified only if it produces artifacts another stream can consume and independently verify.

**Avoid:**
- Reports-only layers
- Prompt-only layers
- Evidence-polishing loops
- AI summary stores without authority rules
- Dashboards without enforcement

**Evidence proves work. Evidence is not the product.**

The user wants repeated decision-influencing systems separated into independent, versioned, schema-backed, evidence-producing layers whose results can be independently verified, vetted, and passed to the next stream.

---

## Section 2: Specification Authority Layer Direction

The initial Specification Authority Layer plan is not production-grade until healed.

**The hard problem:** Make huge file-format specs reliably usable by agents and LLMs without:
- Whole-spec prompt stuffing
- Ad-hoc browsing
- Memory-only claims
- Random snippets

**Preserve (do not remove):**
- Independent Specification Authority Layer
- Raw specs as authority
- AI as `ai_draft` until verified
- Context packs as mandatory consumption unit
- Usage ledger
- Four-stream integration
- Pilots: ZST, Netpbm, DIF, Gnumeric, FODS/FODT
- Git vs local storage split
- Provenance/checksum/license tracking

**Redesign/build (architecture-first):**
- Full data lifecycle
- Schema lifecycle/versioning
- Deterministic context packs
- Staleness/refresh propagation
- Coverage validation
- Mainstream enforcement
- Regression tests

**11 required subsystems:**
1. SpecSourceRegistry
2. SpecVault
3. SpecParser
4. SpecNormalizer
5. SpecIndexer
6. SpecDigestor
7. RequirementExtractor
8. SpecVerifier
9. RequirementGraph
10. ContextPackBuilder
11. SpecGovernanceRuntime

**13 lifecycle states:**
- source_candidate → registered_source → raw_snapshot → parsed_artifact → normalized_artifact → indexed_artifact → digest_artifact → candidate_requirement → verified_requirement → context_pack → usage_record → coverage_record → refresh_event

**Deterministic context pack contract:**
Same source snapshots + same request + same index version + deterministic ranking/tie-breaks + timestamp isolation → same manifest/hash.

**Context pack multi-resolution:**
- Raw snapshots: NEVER stuffed into prompt
- Parsed section tree
- Chunks/tables
- Section summaries
- Subsystem summaries
- Always-included format capsule
- Task context pack
- Implementation/test handoff

**Complete-picture policy:**
Every context pack includes:
- Format capsule
- Spec/subtree outline
- Task-specific requirements
- Direct source chunks for critical rules
- Unsupported/ambiguous areas + edge cases + open uncertainties
- Retrieval log + manifest hash
- If token budget exceeded: drop optional adjacent chunks first. NEVER drop requirement IDs, source refs, or format capsule.

**Usage ledger:**
- Append-only under `.local/spec-usage-ledger/usage-YYYYMMDD.jsonl`
- Every context-pack build and every AI consumption logs a row
- Fields: stream, task, context_pack_id/hash, source snapshots, requirement IDs, model/mode, prompt/output paths, validation status, authority state, stale_at_use
- Corrections use `correction_of`

**Four-stream enforcement:**
- Mainstream: handoffs require `context_pack_id` + `requirement_ids` + `source_snapshot_ids`
- Acceleration: outputs remain `ai_draft`, log `context_pack_id` and `usage_id`
- Skills: templates/transcripts require `context_pack_id` + `requirement_ids` + `usage_id`
- Supervisor: validates claim support, stale packs, `ai_draft` misuse, false PASS prevention

**Anti-bypass rules:**
- Ad-hoc URL citation rejected until source registered
- Memory-only spec claim rejected
- Raw AI summary without `source_refs` must run verifier
- Unverified requirements remain candidate
- Context pack without `manifest.sha256` rejected

**Pilot scope:**
- Minimum: ZST, Netpbm, DIF
- Extended/Phase 2: Gnumeric, FODS/FODT/ODF
- Rationale: Strong 3-format pilot > 5 shallow ingestions
- DIF/Gnumeric/ODF source licensing must be verified during execution; if unclear → raw snapshot quarantined + fetch-blocker documented

---

## Section 3: Specification Authority Production-Blocker Plan Review

**Plan name:** `ticklish-dancing-lobster(1).md`
**Review verdict:** `PLAN_NEEDS_REPAIR`

**Strengths:**
- Addressed 10 blockers
- Added 11 subsystems including SpecSourceRegistry and SpecNormalizer
- Defined 13 lifecycle states
- Defined deterministic context-pack contract
- Defined regression categories
- Narrowed pilot scope to ZST + Netpbm + DIF

**Required repairs before execution (14 points):**
1. Add declaration-driven supervisor closeout: `python tools/supervisor/autonomous_cycle.py --declaration <path>`
2. Allow: `.local/supervisor/reviews/specification-authority-layer-production-healing/**`
3. Remove brittle hardcoded counts as authority (19 taskcards, 25 files, 20 Markdown files)
4. Use declared-vs-materialized validation from file-ownership-map / taskcard-state / evidence-manifest
5. Initialize taskcards as `READY`, not `IN_PROGRESS`
6. Lifecycle: `READY → IN_PROGRESS → CLOSED_VERIFIED`
7. Populate `evidence_paths` before close
8. Do not pre-fill `worker_self_verdict: PASS`
9. Choose final verdict after validation and autonomous-cycle result
10. Python portability: preferred `.local/venv/Scripts/python`, fallback `python`, same PYTHON for all
11. Remove machine-specific path `C:\Users\prora\.claude\plans\ticklish-dancing-lobster.md`
12. Use current attached plan or repo-local `input-plan.md`
13. Normalize final verdicts — remove generic COMPLETE/PARTIAL/BLOCKED
14. Add durable `reports/specification-authority-layer-production-healing/review-package-proof.md`
+ Strengthen validation (declared output existence, Markdown H1, JSON/YAML parse, no unresolved taskcards, keywords, no forbidden changes, autonomous-cycle run captured, package exists, SHA-256 computed)

**Ready-to-send repair prompt ID:** `FORMAT-FACTORY-SPECIFICATION-AUTHORITY-LAYER-PRODUCTION-HEALING-PLAN-REPAIR-001`
**Purpose:** Repair the plan only, do NOT execute the healing sprint.
**Target verdicts:**
- `SPEC_AUTH_HEALING_PLAN_REPAIRED_READY_FOR_SINGLE_GO_EXECUTION`
- `SPEC_AUTH_HEALING_PLAN_REPAIRED_WITH_LIMITATIONS`
- `SPEC_AUTH_HEALING_PLAN_STILL_NEEDS_REPAIR`

---

## Section 4: Requirement & Capability Authority Layer Direction

**Purpose:** Accountability bridge between specification/source requirements and product readiness.

**Core question:** "Can we honestly claim this capability is supported, and what proves it?"

**Must NOT replace existing systems.** Preserve:
- `product-capability-matrix/poc-targets.yaml` (readable dashboard)
- `registry/format-registry.yaml` (format context)
- Source code, tests, examples, dogfood outputs
- Evidence declarations/manifests/packages
- Source-change ledgers
- Supervisor review packages
- Mainstream dashboard
- Skills handoff/transcript model
- Acceleration `ai_draft` packet model

**Wraps existing systems with proof logic.**

**Relationship to Spec Authority:**
- Specification Authority Layer says what **should** be true.
- Requirement & Capability Authority Layer says what we **claim** is true and whether it is **proven enough for POC**.

**Three requirement source types:**
- `spec_backed`
- `empirical_sample_backed`
- `product_policy_exception`

**11 key subsystems:**
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

**Current plan `delegated-roaming-whistle.md` verdict:** Too shallow, not production-ready.
Had right vocabulary but was artifact-first/taskcard-heavy, not a durable decision engine.

**Required redesign:** Move from "schemas + taskcards + docs" to "proof graph + deterministic evaluation runtime + claim decomposition + staleness propagation + gap queue + Supervisor verdict packet"

### Canonical Capability Proof Graph

**Node types (18):**
ProductRequirement, CapabilityClaim, ImplementationArtifact, TestArtifact, ExampleArtifact, DogfoodArtifact, EvidencePackage, UnsupportedFeature, EmpiricalEvidence, SpecRequirementRef, ProductPolicyDecision, ContextPackRef, CoverageRecord, CapabilityDelta, PocTargetField, StreamHandoff, UsageRecord, StalenessEvent

**Edge types (19):**
derives_from, claims_support_for, implemented_by, tested_by, exemplified_by, dogfooded_by, evidenced_by, limited_by, blocked_by, supersedes, invalidates, proposed_by, accepted_by, syncs_to, consumed_by, stale_due_to, narrows, broadens, conflicts_with

**Graph invariants (8):**
1. Accepted claims need accepted ProductRequirement.
2. Accepted ProductRequirement needs spec req / empirical evidence / product policy decision.
3. `accepted_for_poc` claims need implementation/tests/evidence and dogfood if required.
4. `accepted_with_limitations` needs UnsupportedFeature.
5. Stale nodes cannot support new `accepted_for_poc`.
6. `ai_draft` nodes cannot satisfy proof.
7. EvidencePackage proves only included artifacts, not truth by itself.
8. PocTargetField updated only via proposed sync delta.

### Claim-scope decomposition dimensions (12):
product_id, format_id, operation, direction, fidelity, variant, object_model_scope, io_scope, error_scope, performance_scope, platform_scope, POC_scope

### Overclaim remediation (must narrow/split):
- "support format" → parse-only if only parse proof
- "save" claimed with export proof → downgrade to export
- "roundtrip" claimed with parse only → reject roundtrip, create parse claim
- All variants claimed but one tested → variant-specific claims
- Full support with partial proof → accepted partial + blocked remainder

### Proof sufficiency classes (9):
RequirementProof, ImplementationProof, TestProof, ExampleProof, DogfoodProof, EvidencePackageProof, LimitationProof, FreshnessProof, PolicyProof

### Proof sufficiency levels (10):
NO_PROOF → REQUIREMENT_ONLY → IMPLEMENTATION_ONLY → TESTED → EXAMPLED → DOGFOODED → COVERAGE_VALIDATED → ACCEPTED_FOR_POC → ACCEPTED_WITH_LIMITATIONS → REJECTED_OR_BLOCKED

### POC Capability Families

**FODS:** load/inspect, edit object model, same-format save/write, CSV export/dogfood, example/package proof
**FODT:** load/inspect, edit object model, same-format save/write, Markdown/TXT export/dogfood, example/package proof
**Netpbm .NET:** load/read metadata, edit/image transform, same-format save, export/conversion, example/package proof
**ZST:** compress, decompress, probe/validate, roundtrip, CLI/import/package proof
**Python Netpbm:** PBM/PGM/PPM parse/write, binary/text variants, examples/import proof
**SYLK:** parse, write, CSV export, roundtrip, example/import proof
**DIF:** parse, write_dif, CSV export, roundtrip, example/import proof
**Gnumeric (stretch):** read workbook/sheets/cells, metadata extraction, CSV/JSON export, write if feasible, example/import proof

### Format Rules:
- Netpbm must be retained. SVG must NOT replace Netpbm.
- DIF may substitute or supplement SYLK if proof validates faster.
- Gnumeric counts only if required capabilities validate.

### Authority chain:
- Mainstream proposes CapabilityDelta
- Skills produces handoffs/transcripts
- Acceleration recommends `ai_draft`
- Supervisor/validator accepts or rejects
- Direct truth update / direct `poc-targets.yaml` mutation NOT allowed

### Healing prompt ID:
`FORMAT-FACTORY-REQUIREMENT-CAPABILITY-AUTHORITY-LAYER-PRODUCTION-BLOCKER-HEALING-001`
**Target:** `REQUIREMENT_CAPABILITY_AUTHORITY_LAYER_PLAN_HEALED_READY_FOR_MWP_EXECUTION`

Healed MWP output dirs:
- `requirements-authority/**`
- `tools/requirements_authority/**`
- `tests/supervisor/test_requirement_capability_authority_layer.py`

---

## Section 5: Supervisor Product Traffic Controller State

**Bundle:** `declaration-review-package(67).zip`
**SHA-256:** `f927ebbd1d6e1d067bcd9da04d7cd12705533c84030f18afda71d59cbf1a97b1`
**Entries:** 129 / Size: 204,135 bytes
**Verdict:** `SUPERVISOR_SPRINT_ACCEPTED_AS_REAL_PROGRESS_WITH_NON_BLOCKING_EVIDENCE_CAVEATS`

**Real work completed:**
- `tools/supervisor/product_velocity_scorer.py` (created)
- `tools/supervisor/ai_supervisor_advisor.py` (created)
- `tools/supervisor/external_tool_governance.py` (created)
- `tools/supervisor/autonomous_cycle.py` (modified)
- Continuation states added: NO_PRODUCT_OUTPUT_FLOOR, NO_MISSING_REQUIRED_ARTIFACTS, NO_UNCLASSIFIED_DIRTY_STATE
- 23 targeted tests added

**External runtime governance detected:**
- Ruflo/claude-flow: detected, not configured
- Task Master: detected, not configured
- Superpowers: not installed
- GhidraMCP: disabled by default

**Non-blocking caveats:**
- Supervisor review still ACCEPTED_WITH_REWORK / evidence_quality_score=0.0
- Anti-skip: missing sample outputs / wrong-stream global next-sprint
- Taskcard-state not fully closed while declaration lists completed work
- Continuation-signal conflict

**Next Supervisor prompt:** `FORMAT-FACTORY-SUPERVISOR-PRODUCT-TRAFFIC-CONTROLLER-INTEGRATION-001`

---

## Section 6: Supervisor + Skills Latest Execution Evidence

### Supervisor Bundle
- `declaration-review-package(69).zip`
- SHA-256: `6b0b6b9511372639cfbafb455061a879fdc8d3455239bd803b7ed3d85176b5d7`
- 99 entries / run: `supervisor-product-traffic-controller`

### Skills Bundle
- `declaration-review-package(70).zip`
- SHA-256: `35cda024812fbe254da8763e7f515d78717cc38f610fa89be1379dfd2a0a7264`
- 162 entries / run: `skills-product-first`

Both accepted for forward progress with non-blocking evidence caveats.

**Supervisor implementation completed:**
- `tools/supervisor/generate_stream_routing_packet.py`
- `tools/supervisor/check_cross_stream_consumption.py`
- Stream-local routing packets (all 4 streams)
- Product-specific Mainstream handoff
- External-tool status integration
- Tests: `test_supervisor_product_traffic_controller_integration.py`, `test_cross_stream_consumption.py`, `test_continuation_state_integration.py`, `test_external_tool_governance_integration.py`
- 53 passed / 0 failed / 0 skipped
- Caveat: raw pytest log not found in ZIP (test count in evidence and test files packaged)

**Supervisor product classification:** PARTIAL_FEW_FAMILIES
**Supervisor decision:** CONTINUE_WITH_LIMITATIONS
**Recommended families:** FODS, FODT, Netpbm

**Supervisor generated product queue:**
- FODS CSV dogfood/export
- FODS HTML dogfood/export
- FODT Markdown dogfood/export
- FODT TXT dogfood/export
- SYLK installed workflow
- Netpbm FOSS proof
- SYLK writer/export proof
- ZST dependency resolution

**Supervisor caveats:**
- ACCEPTED_WITH_REWORK despite rework_count=0 and artifacts_missing=0
- git_status_final mentions dirty `.claude/commands`, `.supervisor`, `plans/master-plan.md` not in declared changed files
- Supervisor still reported Skills missing but Skills bundle now supplies packet
- Generated next-sprint text referenced older `supervisor_loop` / autonomous-cycle style
- Future prompts must use `autonomous_cycle.py --declaration`

**Skills implementation completed:**
- Governed source-change contract
- Mainstream consumption packet for FODS CSV dogfood/export
- Handoff-to-mainstream
- Near-live transcript / live-cycle proof
- 6 reusable Mainstream templates: add-dotnet-api, add-python-api, add-export, add-dogfood-pipeline, add-roundtrip-test, update-capability-matrix
- 10 receiver fixtures (1 compliant, 8 expected-failing, 1 YES_WITH_LIMITATIONS)
- Superpowers evaluation without install
- External skill normalization map/wrapper
- No-plugin-install proof

**Skills pytest:** 72 passed / 0 failed / 0 skipped (raw log confirmed)
**Skills key output:** `reports/skills-product-first/mainstream-consumption-packet.json`
**Packet target:** GAP-FODS-DOGFOOD-CSV-DOTNET-001
**Capability:** dogfood_status.fods_to_csv_dotnet
**Recommended skill:** add-dotnet-api
**Expected test:** `tests/net/fods/FodsR114ExportToCsvTests.cs`
**Expected source:** `src/net/fods/FodsDocument.cs` or `src/net/fods/FodsWorkbook.cs`

**Skills caveats:**
- Path-heavy items accepted with limitations
- MCP/check-mcp-status promotion deferred (4/10 MCP criteria passed, 6/10 failed)
- Superpowers: evaluated only, not installed (correct behavior)
- Packet expects capability-matrix update but Mainstream should treat as proposed delta unless authorized
- Only FODS CSV packet is full; no live packets yet for FODS HTML, FODT Markdown/TXT, Netpbm, SYLK, ZST

---

## Section 7: Supervisor and Skills Hardening Prompts

**User decision:** Mainstream should wait. Before Mainstream consumes Supervisor/Skills outputs, each lane should get hardening/independent verification. Mainstream waits until all three lanes (including Acceleration) have independent proof.

**Recommended execution order:**
1. Skills hardening (so Supervisor can classify latest Skills output instead of SKILLS_MISSING_PACKET)
2. Supervisor hardening
3. Acceleration hardening / IV
4. Mainstream implementation

### Supervisor Hardening Sprint
**ID:** `FORMAT-FACTORY-SUPERVISOR-TRAFFIC-CONTROLLER-HARDENING-IV-001`
**Mission:** Harden and independently verify latest Supervisor Product Traffic Controller before Mainstream consumes it.
**NOT:** product implementation / evidence cleanup

**Lanes:**
- Lane 0: Coordinator/safety
- Lane A: Evidence-to-implementation reconciliation
- Lane B: Replay and determinism hardening
- Lane C: Cross-stream consumption hardening
- Lane D: Product routing hardening
- Lane E: Continuation and false-pass/false-stop hardening
- Lane F: External-tool governance read-only hardening
- Lane G: Tests
- Lane H: Hardened routing outputs
- Lane I: Evidence and closeout using `autonomous_cycle.py --declaration`

**Replay scenarios (10):**
baseline, current Skills packet present, missing Skills, missing Acceleration, both missing, stale/malformed Skills, stale/malformed Acceleration, empty selected-product-gaps fallback, weak breadth, synthetic clean-pass

**Final verdicts:**
- `SUPERVISOR_TRAFFIC_CONTROLLER_HARDENED_INDEPENDENTLY_VERIFIED`
- `SUPERVISOR_TRAFFIC_CONTROLLER_HARDENED_WITH_LIMITATIONS`
- `SUPERVISOR_TRAFFIC_CONTROLLER_HARDENING_FAILED_NEEDS_REWORK`

### Skills Hardening Sprint
**ID:** `FORMAT-FACTORY-SKILLS-GOVERNED-EXECUTION-HARDENING-IV-001`
**Mission:** Harden and independently verify latest Skills/Governed Execution before Mainstream consumes it.
**NOT:** Mainstream implementation / plugin install / MCP promotion / evidence cleanup / template expansion beyond product consumption proof

**Lanes:**
- Lane 0: Coordinator/safety
- Lane A: Evidence-to-implementation reconciliation
- Lane B: FODS CSV packet/handoff hardening
- Lane C: Template/transcript validator hardening
- Lane D: Product breadth handoff hardening
- Lane E: Superpowers/external skill boundary hardening
- Lane F: Cross-stream consumption readiness packet
- Lane G: Skills hardening tests
- Lane H: Evidence closeout using `autonomous_cycle.py --declaration`

**Skills hardening details:**
- Validate full FODS CSV packet
- Create/validate safe packet shells for: FODT Markdown, FODT TXT, Netpbm proof/dogfood/package
- Shells labeled `NEEDS_MAINSTREAM_DISCOVERY` when full discovery needed
- Shells must be consumable by Mainstream as fallback handoffs
- Superpowers boundary: no `.claude-plugin` mutation, no `/plugin install`, no MCP registration, no `.vscode/mcp.json` mutation, no SessionStart injection
- Expected Skills readiness status (if FODS full packet validates + FODT/Netpbm shells exist): `SKILLS_CONSUMABLE_WITH_LIMITATIONS`

**Final verdicts:**
- `SKILLS_GOVERNED_EXECUTION_HARDENED_INDEPENDENTLY_VERIFIED`
- `SKILLS_GOVERNED_EXECUTION_HARDENED_WITH_LIMITATIONS`
- `SKILLS_GOVERNED_EXECUTION_HARDENING_FAILED_NEEDS_REWORK`

---

## Section 8: Mainstream Deferred

**Status:** DEFERRED until Supervisor + Skills + Acceleration each have independent hardening proof.

A prior Mainstream implementation prompt exists but must NOT run yet per user's later decision.

**When Mainstream eventually runs, use:**
- Supervisor routing
- Skills handoff
- Acceleration packets

**Target at least 3 families:** FODS, FODT, Netpbm

**Priority:**
1. FODS CSV dogfood/export
2. FODT Markdown/TXT dogfood/export
3. Netpbm proof

**Mainstream must produce:**
- Source changes, tests, dogfood outputs, transcripts
- Capability delta proposals (NOT direct authority mutation)
- Evidence declaration/review package

**Mainstream must NOT:** commit, push, publish, approve gates, spend sprint on evidence cleanup.

**Mainstream must retain Netpbm. SVG must NOT replace Netpbm.**

**Capability matrix update:** Treat Skills packet as proposed delta unless explicitly authorized.

---

## Section 9: Evidence Handling Principle

**User emphasis (repeated):** Do not waste time correcting evidence packaging/metadata unless it blocks execution or important proof.

**Focus on:** implementation, product progress, moving project in the right direction.

**Future reviews should:** report evidence caveats honestly + continue safe forward work + NOT make non-blocking evidence caveats the sprint goal.

**Evidence repair is justified ONLY when required to:**
- Prove important work
- Prevent false claims
- Fix missing materialized proof
- Unblock independent verification

**Every future sprint prompt must still require:**
- Evidence bundle or review package
- Absolute review package path in final response
- SHA-256 in final response

**But evidence cleanup must NOT become the main sprint.**

---

## Section 10: External Tool Posture

Ruflo/claude-flow, Task Master, Superpowers, GhidraMCP are accelerators/support tools, NOT authority.

**Ruflo/claude-flow:**
- Detection may be read-only
- Absent/not configured → fallback to local coordinator (does NOT block product work)

**Task Master:**
- Detected/not configured is NOT product-blocking
- Not authority

**Superpowers:**
- May be evaluated/normalized
- Must NOT be installed without explicit approval
- No `.claude-plugin` mutation / no `/plugin install` / no MCP registration / no `.vscode/mcp.json` mutation / no SessionStart injection

**GhidraMCP:**
- Disabled by default
- Not needed for text/XML/compression POC targets
- Do NOT activate unless explicitly approved and useful

**External tool output cannot:**
- Close taskcards
- Become capability authority
- Approve gates

---

## Section 11: Future Prompt and Review Standards

**Prompts must be:**
- Ready-to-send, detailed, self-contained
- Taskcard-driven with allowed/forbidden paths
- Lane ownership + file ownership + overlap checks
- taskcard-state + validation commands + rollback/failure handling
- Evidence declaration/review package
- Final response contract

**Agents should NOT treat human as blocker except for true external authority/credentials.**

**Always:**
- Inspect uploaded evidence before verdicts or next prompts
- Produce next prompt when user shares sprint results/evidence
- Sprints broad enough to advance implementation/product progress
- Do not get stuck only healing evidence

**Plan reviews must produce:**
- `PLAN_NEEDS_REPAIR` → provide repair prompt
- `READY_FOR_SINGLE_GO_EXECUTION` → provide single-go execution handoff

**Use declaration-driven closeout:**
1. `python tools/supervisor/autonomous_cycle.py --declaration <evidence-declaration.yaml>`
2. `python tools/supervisor/build_declaration_review_package.py --declaration <evidence-declaration.yaml>`
3. Fallback ZIP only if needed

**Final responses must include:**
- Absolute review package path
- SHA-256

---

## Authority Notes

- No Gate 8 or Gate 11 approval granted.
- No commercial_product_ready=true.
- No push or commit authorized.
- All plans in PLAN_NEEDS_REPAIR state until explicitly repaired.
- Mainstream is DEFERRED.

---

*End of memory/67 — 2026-06-04*
