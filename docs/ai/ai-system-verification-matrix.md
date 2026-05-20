# AI System Verification Matrix

## Purpose
Canonical reference for the verification status of every AI component.
Updated each sprint. Created in R32, updated R33 with runner-executable columns.

## Component Verification Status

| Component | Fixture Verified | Isolated Verified | Pipeline Fixture | Pipeline Live | Failure Injection | Runner Fixture | Runner Live | Blocked Dependency | Blocked Policy | Not Authorized |
|-----------|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| AIConfig (load_ai_config) | R31 | R31 | R31, R32 | R31, R32 | R31 | R33 | R33 | - | - | - |
| Model Discovery (discover_models) | R31 | R31 | R31 | R31, R32 | R31 | R33 | R33 | - | - | - |
| Model Router (select, fail-closed) | R31 | R31 | R31 | - | R31, R32 | R33 | - | - | - | - |
| Capability Probe (probe_model) | R31 | R31 | R31 | R31, R32 | R31 | R33 | R33 | - | - | - |
| Gateway (gateway_chat) | R31 | R31 | - | R31, R32, R33 | R31, R32 | - | R33 | - | - | - |
| Synthesis Runner (run_synthesis) | R31 | R31 | R31, R32, R33 | R32, R33 | R31, R32 | R33 | R33 | - | - | - |
| Citation Verifier (verify_all_citations) | R31 | R31 | R31, R32, R33 | R32, R33 | R31, R32 | R33 | R33 | - | - | - |
| Contradiction Detector | R31 | R31 | R31, R32, R33 | R32 | R31, R32 | R33 | - | - | - | - |
| Evaluator (evaluate_synthesis) | R31 | R31 | R31, R32, R33 | R32, R33 | R31, R32 | R33 | R33 | - | - | - |
| Requirements Generator | R31 | R31 | R31, R32 | - | R32 | R33 | - | - | - | - |
| Authority Lifecycle (12-state) | R31 | R31 | R31, R32, R33 | - | R31, R32 | R33 | R33 | - | - | - |
| Normalization Adapter | R31 | R31 | R31, R32, R33 | - | - | R33 | - | - | - | - |
| Retrieval Namespace Manager | R31 | R31 | R31 | - | R31, R32 | - | - | - | - | - |
| Lexical Retriever (ranked, diverse) | R32, R33 | R32, R33 | R32, R33 | - | R32 | R33 | R33 | - | - | - |
| Vector Retrieval (LanceDB) | - | - | - | - | - | - | - | LanceDB not installed | - | - |
| Scoped Agentic Runner (Qwen2) | R31 | R31 | - | - | R31 | - | - | - | - | No live agentic tasks |
| Telemetry Spool Manager | R31 | R31 | - | R32 | R31 | - | - | - | - | - |
| Telemetry Artifacts (durable) | R33 | R33 | - | R33 | - | - | R33 | - | - | - |
| Agent Metrics Drain | R31 | R31 | - | - | R31 | - | - | - | No AGENT_METRICS_API_KEY | - |
| Secret Redaction | R31 | R31 | - | R32, R33 | R31, R32, R33 | - | R33 | - | - | - |
| Runtime Guard (AI-free src/) | R31 | R31 | - | - | R31 | - | - | - | - | - |
| CLI Runner (run_ai_checks.py) | R31, R32, R33 | R32, R33 | R32, R33 | R32, R33 | R32, R33 | R33 | R33 | - | - | - |
| Commit Metadata Model | R33 | R33 | - | - | - | - | - | - | - | - |
| Contradiction Policy | R33 | R33 | R33 | - | - | R33 | - | - | - | - |
| Evidence Validator Integration | R33 | R33 | - | - | - | R33 | - | - | - | - |

## R33 New Columns
- **Runner Fixture:** Component exercised via `run_ai_checks.py --fixture-pipeline` (deterministic)
- **Runner Live:** Component exercised via `run_ai_checks.py --live-pipeline` (real gateway)

## Evidence Paths
- R31 reports: reports/r31/
- R32 reports: reports/r32/
- R33 reports: reports/r33/
- R31 tests: tests/ai/test_r31_ai_system_verification.py
- R32 tests: tests/ai/test_r32_ai_deepening.py
- R33 tests: tests/ai/test_r33_runner_pipeline_truth.py

## Legend
- **Fixture Verified:** Component tested with synthetic data, no live calls
- **Isolated Verified:** Component tested independently with mocks
- **Pipeline Fixture:** Component exercised as part of full fixture pipeline
- **Pipeline Live:** Component exercised with real LLM endpoint
- **Failure Injection:** Failure modes tested for safe behavior
- **Runner Fixture:** Exercised via CLI runner in fixture mode
- **Runner Live:** Exercised via CLI runner in live mode
- **Blocked Dependency:** Requires software not installed
- **Blocked Policy:** Requires credential/authorization not available
- **Not Authorized:** Capability exists but not approved for use in this sprint
