# AI System Verification Matrix

## Purpose
Canonical reference for the verification status of every AI component.
Updated each sprint. Created in R32, based on R31 isolation verification.

## Component Verification Status

| Component | Fixture Verified | Isolated Verified | Pipeline Fixture | Pipeline Live | Failure Injection | Blocked Dependency | Blocked Policy | Not Authorized |
|-----------|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| AIConfig (load_ai_config) | R31 | R31 | R31, R32 | R31, R32 | R31 | - | - | - |
| Model Discovery (discover_models) | R31 | R31 | R31 | R31, R32 | R31 | - | - | - |
| Model Router (select, fail-closed) | R31 | R31 | R31 | - | R31, R32 | - | - | - |
| Capability Probe (probe_model) | R31 | R31 | R31 | R31, R32 | R31 | - | - | - |
| Gateway (gateway_chat) | R31 | R31 | - | R31, R32 | R31, R32 | - | - | - |
| Synthesis Runner (run_synthesis) | R31 | R31 | R31, R32 | R32 | R31, R32 | - | - | - |
| Citation Verifier (verify_all_citations) | R31 | R31 | R31, R32 | R32 | R31, R32 | - | - | - |
| Contradiction Detector | R31 | R31 | R31, R32 | R32 | R31, R32 | - | - | - |
| Evaluator (evaluate_synthesis) | R31 | R31 | R31, R32 | R32 | R31, R32 | - | - | - |
| Requirements Generator | R31 | R31 | R31, R32 | - | R32 | - | - | - |
| Authority Lifecycle (12-state) | R31 | R31 | R31, R32 | - | R31, R32 | - | - | - |
| Normalization Adapter | R31 | R31 | R31, R32 | - | - | - | - | - |
| Retrieval Namespace Manager | R31 | R31 | R31 | - | R31, R32 | - | - | - |
| Lexical Retriever (ranked) | R32 | R32 | R32 | - | R32 | - | - | - |
| Vector Retrieval (LanceDB) | - | - | - | - | - | LanceDB not installed | - | - |
| Scoped Agentic Runner (Qwen2) | R31 | R31 | - | - | R31 | - | - | No live agentic tasks |
| Telemetry Spool Manager | R31 | R31 | - | R32 | R31 | - | - | - |
| Agent Metrics Drain | R31 | R31 | - | - | R31 | - | No AGENT_METRICS_API_KEY | - |
| Secret Redaction | R31 | R31 | - | R32 | R31, R32 | - | - | - |
| Runtime Guard (AI-free src/) | R31 | R31 | - | - | R31 | - | - | - |
| CLI Runner (run_ai_checks.py) | R31, R32 | R32 | R32 | R32 | R32 | - | - | - |

## Evidence Paths
- R31 reports: reports/r31/
- R32 reports: reports/r32/
- R31 tests: tests/ai/test_r31_ai_system_verification.py
- R32 tests: tests/ai/test_r32_ai_deepening.py

## Legend
- **Fixture Verified:** Component tested with synthetic data, no live calls
- **Isolated Verified:** Component tested independently with mocks
- **Pipeline Fixture:** Component exercised as part of full fixture pipeline
- **Pipeline Live:** Component exercised with real LLM endpoint
- **Failure Injection:** Failure modes tested for safe behavior
- **Blocked Dependency:** Requires software not installed
- **Blocked Policy:** Requires credential/authorization not available
- **Not Authorized:** Capability exists but not approved for use in this sprint
