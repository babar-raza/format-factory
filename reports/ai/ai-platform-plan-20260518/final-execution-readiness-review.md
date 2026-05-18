# Final Execution Readiness Review

**Date:** 2026-05-18
**Sprint:** FORMAT-FACTORY-AI-PLATFORM-FINAL-DEEP-PLAN-HEALING-001
**Status:** Updated after deep production architecture review

---

## 1. Is the plan ready for implementation review?

**YES** — with conditions.

The plan has been subjected to deep production architecture review including:
- 13 root causes identified and resolution designs provided
- 17 rerun consistency breakers analyzed with detection/prevention/evidence/regression per breaker
- 15 items to preserve confirmed untouched
- 15 items to redesign with concrete component specifications
- 48 risks with full control schema (risk ID, description, severity, likelihood, detection, prevention, mitigation, validation test, evidence artifact, owner, stop condition)
- 17 production components fully specified with responsibility/inputs/outputs/storage/schemas/failure-modes/validation/evidence/owner
- Concrete Agent Metrics field mapping (17 fields with aggregation rules)
- Artifact authority state machine with 12 states and transition prerequisites
- Control plane contract model with Pydantic field definitions
- Recovery and failure handling model
- Content-level validation (not just file counts)

**What earned this verdict:** The deep-review companion reports provide the analytical layer missing from the initial plan. The plan is no longer inventory-only — it has root cause analysis, rerun safety model, and production control specifications.

## 2. What is authorized in the first implementation sprint?

**Phase 1 Control Plane Foundation only:**
- Install LiteLLM (>=1.40.0) and Pydantic v2 (>=2.5.0) in .venv or requirements-ai.txt
- Create `tools/ai/` directory structure
- Create `tools/ai/control_plane/` modules: gateway, model_discovery, model_router, config
- Create `tools/ai/telemetry/` modules: call_logger, spool_manager
- Create `tools/ai/validators/` modules: schema_validator, authority_lifecycle, runtime_guard
- Create `tools/ai/schemas/` Pydantic models for TaskContract, TelemetryRecord, ModelRegistry
- Create `tools/ai/contracts/roles.yaml`
- Create `tests/ai/` test suite (at minimum: test_model_discovery, test_model_router, test_telemetry, test_runtime_guard, test_authority_lifecycle)
- Create `.local/ai/` directory structure
- Make one model discovery call to GPT_OSS_ENDPOINT
- Log discovery results to .local/ai/model-registry/

## 3. What remains forbidden?

1. No product source changes (src/python/, src/net/) — PERMANENT
2. No vector database creation — until Phase 3
3. No embedding generation — until Phase 3
4. No LlamaIndex installation — until Phase 3
5. No LanceDB installation — until Phase 3
6. No Qwen2 agentic tasks — until Phase 4 with scope guard operational
7. No autonomous code generation — until Phase 4+ with citation verifier
8. No Agent Metrics posting — until Phase 5
9. No gate approval via AI — PERMANENT prohibition
10. No secrets in committed files — PERMANENT prohibition
11. No direct endpoint calls bypassing gateway — PERMANENT prohibition

## 4. What evidence is required from implementation?

Phase 1 implementation sprint must produce:
- Created files manifest (all tools/ai/ files)
- Model discovery output sample (model list from endpoint)
- Role routing test results (per-role model selection verification)
- Fail-closed verification (ROLE_UNAVAILABLE when no model qualifies)
- Telemetry sample records (JSONL from at least one real call)
- Runtime guard scan results (src/ clean of AI imports)
- Test results summary (all tests/ai/ pass)
- No-secrets verification scan
- Git diff summary
- Evidence bundle with BUNDLE_VALIDATION: PASS

## 5. What taskcards must be opened/closed?

| Taskcard | Required Action |
|----------|----------------|
| AI-PLATFORM-FOUNDATION-PLAN | Transition to `implementation_in_progress` |
| AI-MODEL-DISCOVERY-AND-ROUTING | Transition to `implementation_in_progress` |
| AI-FOUNDATION-IMPLEMENTATION-NEXT | Transition to `authorized` (requires Babar Raza) |
| AI-PLATFORM-FINAL-PLAN-HEALING | Remains `closed_ready_for_implementation_review` |
| All other AI-* taskcards | Remain `plan_hardened` until their phase |

## 6. What exact stop conditions apply?

1. GPT_OSS_ENDPOINT not reachable → stop (cannot complete discovery)
2. GPT_OSS_API_KEY not set → stop (cannot authenticate)
3. LiteLLM import fails → stop (dependency not installed)
4. Runtime guard detects AI import in src/ → stop and fix
5. Any secret detected in committed file → IMMEDIATE stop and remediate
6. Gateway bypass detected → stop and refactor
7. Test suite has failures → stop and fix before evidence bundle

## 7. What must be verified before endpoint calls?

1. GPT_OSS_API_KEY is set in environment (not hardcoded)
2. GPT_OSS_ENDPOINT is set and URL is well-formed
3. Gateway module exists and is the only caller
4. Telemetry logger is operational (JSONL write succeeds)
5. Endpoint URL does not contain auth parameters in committed code
6. First call is `/v1/models` discovery (not a production call)

## 8. What must be verified before embeddings/vector DB creation?

1. Phase 1 and Phase 2 control plane fully operational
2. LanceDB installed in .venv (Phase 3 dependency)
3. Spec normalization output exists for target format
4. Normalization adapter successfully loads chunks with provenance
5. Embedding model discovered and dimension-stable
6. Per-format namespace isolation tested
7. Stale detection algorithm implemented and tested
8. Retrieval audit logging operational
9. AI-EMBEDDING-VECTOR-STORE-FOUNDATION taskcard authorized

## 9. What must be verified before GPT-OSS synthesis affects requirements?

1. Citation verifier implemented and tested against golden data
2. Contradiction detector implemented (or explicitly waived if no verified-facts.yaml exists)
3. Evaluator harness operational with golden fixtures
4. Artifact authority lifecycle validator operational
5. AI output starts as ai_draft (enforced by gateway)
6. DEC-034 independent verification sprint completed for generated requirements
7. Human review gate before any requirement reaches accepted_for_source_requirements
8. AI-GPT-OSS-SYNTHESIS-CONTROLS taskcard authorized

## 10. What must be verified before Qwen2 agentic tasks are allowed?

1. Scope guard implemented with path_allowlist and op_allowlist enforcement
2. Task state machine operational
3. Immediate-stop-on-violation behavior tested
4. Output-discard-on-violation behavior tested
5. Timeout enforcement tested
6. Semantic accuracy evaluated against golden answers (>= 80%)
7. Qwen2 model discovered and structured_output capability confirmed
8. Task contract explicitly allows Qwen2 for the specific task
9. AI-AGENTIC-QWEN2-CONTROLS taskcard authorized
10. Adversarial scope violation testing completed

## Assessment

**AI_PLATFORM_PLAN_READY_FOR_IMPLEMENTATION_REVIEW** — Plan is complete with deep analytical backing. Root causes documented. Rerun consistency analyzed. Production controls specified. Recovery model defined. All 48 risks with full control schema. 17 components with full specifications. Awaiting Babar Raza authorization for implementation handoff.
