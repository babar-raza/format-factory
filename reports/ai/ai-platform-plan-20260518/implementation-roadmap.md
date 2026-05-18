# Implementation Roadmap

**Date:** 2026-05-18
**Status:** PLAN — Implementation not yet authorized

## Phase Overview

### Phase 1 — Control Plane Foundation
**Taskcard:** AI-PLATFORM-FOUNDATION-PLAN
**Dependencies:** Human plan review and authorization; GPT_OSS_API_KEY/GPT_OSS_ENDPOINT available
**Deliverables:**
- `tools/ai/control_plane/` modules (model_discovery.py, model_router.py, capability_probe.py, task_contract.py, prompt_registry.py, schema_registry.py)
- `tools/ai/telemetry/` modules (call_logger.py, spool_manager.py)
- `tools/ai/validators/` modules (schema_validator.py, authority_lifecycle.py, runtime_guard.py)
- `tools/ai/schemas/` Pydantic models
- `tests/ai/` test suite
- `.local/ai/` directory structure
**Gate:** Model discovered, routed, telemetry logged, runtime guard passing

### Phase 2 — Synthesis Pipeline
**Taskcards:** AI-GPT-OSS-SYNTHESIS-CONTROLS, AI-TEST-GENERATION-INTEGRATION
**Dependencies:** Phase 1 operational; normalized spec artifacts available
**Deliverables:**
- Synthesis runner with citation verification
- Contradiction detector
- Golden eval framework
- AI test generation pipeline
- Model benchmark suite
**Gate:** One synthesis task passing full validation; test generation producing accepted tests

### Phase 3 — Embedding/Retrieval Foundation
**Taskcards:** AI-EMBEDDING-VECTOR-STORE-FOUNDATION, AI-SPEC-NORMALIZATION-INTEGRATION
**Dependencies:** Phase 1 operational; embedding model discovered; normalized chunks available
**Deliverables:**
- LlamaIndex ingestion pipeline
- LanceDB vector store with format namespaces
- Chunk manifests and stale detection
- Retrieval audit logging
**Gate:** One format fully indexed with reproducible retrieval

### Phase 4 — Agentic Integration and Advanced
**Taskcards:** AI-AGENTIC-QWEN2-CONTROLS
**Dependencies:** Phase 1 operational; Qwen2 discovered
**Deliverables:**
- Qwen2 controlled agent runner
- Task state machine with scope guards
- Cross-format embedding (with isolation)
**Gate:** One low-risk task completing full lifecycle

### Phase 5 — Telemetry and Analytics
**Taskcards:** AI-TELEMETRY-AGENT-METRICS-INTEGRATION
**Dependencies:** Phase 1 spool operational
**Deliverables:**
- Agent Metrics poster
- Spool drain pipeline
- Usage analytics fields
**Gate:** Telemetry flowing to Agent Metrics

### Phase 6 — Hardening
**Taskcards:** AI-RISK-MITIGATION-MATRIX
**Dependencies:** All prior phases
**Deliverables:**
- Full evaluator suite
- Replay manifests
- Risk register validation tests
- Cross-format isolation tests
**Gate:** All 48 risk register items have validation tests

## Sequencing Constraints

- Phase 2 cannot start until Phase 1 control plane is operational
- Phase 3 requires Phase 1 + normalized spec chunks
- Phase 4 can start after Phase 1 (independent of Phase 2-3)
- Phase 5 can start after Phase 1 local spool
- Phase 6 requires all prior phases for full coverage

## Authorization Required

Each phase requires explicit human authorization before implementation begins.
