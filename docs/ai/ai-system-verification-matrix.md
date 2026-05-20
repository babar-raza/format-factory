# AI System Verification Matrix

## Purpose
Canonical reference for the verification status of every AI component.
Updated each sprint. Created in R32, updated R33 with runner-executable columns, R35 with fail-closed and validator integration.

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
| CLI Runner (run_ai_checks.py) | R31, R32, R33, R35 | R32, R33, R35 | R32, R33 | R32, R33 | R32, R33, R35 | R33, R35 | R33, R35 | - | - | - |
| Commit Metadata Model | R33 | R33 | - | - | - | - | - | - | - | - |
| Contradiction Policy | R33, R35 | R33, R35 | R33 | R35 | - | R33, R35 | R35 | - | - | - |
| Evidence Validator Integration | R33, R35 | R33, R35 | - | - | R35 | R33, R35 | - | - | - | - |
| Telemetry Minimization | R35 | R35 | - | - | - | - | R35 | - | - | - |
| Runner JSON Schema | R35 | R35 | - | - | - | R35 | - | - | - | - |
| Fail-Closed Live Pipeline | R35 | R35 | - | R35 | R35 | - | R35 | - | - | - |
| Citation Visibility | R35 | R35 | R35 | - | - | R35 | - | - | - | - |

## R33 New Columns
- **Runner Fixture:** Component exercised via `run_ai_checks.py --fixture-pipeline` (deterministic)
- **Runner Live:** Component exercised via `run_ai_checks.py --live-pipeline` (real gateway)

## R35 New Components
- **Telemetry Minimization:** Content keys stripped before redaction to reduce artifact size
- **Runner JSON Schema:** `--schema` flag outputs expected output shape
- **Fail-Closed Live Pipeline:** Live gateway failure produces `blocked_live_synthesis` (no fixture fallback)
- **Citation Visibility:** Pipeline output includes citation_verified, citations_all_valid, citations_checked, citations_failed

## R35 Fixes
- Evidence validation reads `required_repo_files` (was `required_artifacts` — silent zero-count bug)
- Evidence validation uses canonical contract loader from validate_evidence_bundle.py
- Live pipeline contradiction policy changed from `optional` to `required`
- R33 AI contract emergency_blocker_bundle removed, min_metadata_count restored to 30

## Evidence Paths
- R31 reports: reports/r31/
- R32 reports: reports/r32/
- R33 reports: reports/r33/
- R35 reports: reports/ai/r35-clean-runner-closure-20260520/
- R31 tests: tests/ai/test_r31_ai_system_verification.py
- R32 tests: tests/ai/test_r32_ai_deepening.py
- R33 tests: tests/ai/test_r33_runner_pipeline_truth.py
- R35 tests: tests/ai/test_r35_clean_runner_closure.py

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
