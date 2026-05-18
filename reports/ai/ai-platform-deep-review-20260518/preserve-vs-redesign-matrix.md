# Preserve vs Redesign Matrix

**Sprint:** FORMAT-FACTORY-AI-PLATFORM-DEEP-PRODUCTION-ARCHITECTURE-REVIEW-001
**Date:** 2026-05-18

---

## PRESERVE — Working Systems That Must Not Be Weakened

| ID | Component | Why Preserve | Risk If Changed |
|----|-----------|-------------|-----------------|
| P-01 | Deterministic runtime code (src/python/, src/net/) | Proven, tested, gate-approved | Breaks product integrity |
| P-02 | 11-gate acquisition pipeline with human approval | Core governance model, proven across 8+ formats | Removes accountability |
| P-03 | Evidence bundle system (build + validate) | 99 contracts, deterministic validation, proven | Loses audit trail |
| P-04 | Taskcard-driven work authorization | Bounded scope, clear ownership, tested | Scope creep |
| P-05 | Exact-path git staging | Prevents accidental staging of secrets/unrelated files | Security risk |
| P-06 | No push/PR/publication without authority | Release governance, proven | Unauthorized releases |
| P-07 | Local spec cache with provenance | Immutable source, hash-verified, legal compliance | Loses provenance chain |
| P-08 | Independent verification (DEC-034) | Prevents self-approval, proven | Quality collapse |
| P-09 | Format registry as gate authority | Single source of truth for gate states | State drift |
| P-10 | Agent Metrics as canonical telemetry | Cross-project analytics, established schema | Fragmented metrics |
| P-11 | .venv local environment | No Docker dependency, simple, portable | Complexity |
| P-12 | Existing AI usage ledger format | 8 entries exist, format proven | Backward incompatibility |
| P-13 | Spec normalization pipeline | deterministic, local-only, produces 884+ sections for FODS | Breaks retrieval substrate |
| P-14 | Generated requirements pipeline | Operational, schema-validated, governance established (TC-0053) | Loses only proven AI pipeline |
| P-15 | base-run.yaml forbidden patterns | Prevents embedding/vector/secret leakage in bundles | Security regression |

---

## REDESIGN — Components That Need Structural Change

| ID | Component | Current State | Why Redesign | Target State |
|----|-----------|--------------|-------------|-------------|
| R-01 | AI platform boundary | Non-existent (concept only) | No enforcement of "all AI through tools/ai/" | `tools/ai/` as sole AI entry point with import guard |
| R-02 | Model discovery/routing | Prose policy + static endpoints.yaml | Can't discover, probe, or route at runtime | Executable discovery with capability contracts |
| R-03 | Qwen2 agentic controls | Policy doc only | No scope enforcement mechanism | Scope guard with path/op allowlists as code |
| R-04 | GPT-OSS synthesis controls | Policy doc only | No schema validation or citation verification code | Pydantic schemas + citation verifier as code |
| R-05 | Embedding/vector store | Policy doc only | No index lifecycle management | LanceDB wrapper with manifest/stale/rebuild |
| R-06 | Spec normalization -> AI adapter | Normalization exists, no AI adapter | AI can't consume normalized output programmatically | Adapter that loads chunks with provenance |
| R-07 | Test generation lifecycle | Policy doc only | No generation/review/acceptance pipeline | Generator -> reviewer -> acceptance gate as code |
| R-08 | Telemetry posting lifecycle | Three separate designs, no unified flow | Fragmented, no posting mechanism | Single lifecycle: record -> aggregate -> post -> mark |
| R-09 | Artifact authority state machine | 12 states in prose | No state tracking, no transition enforcement | Executable state machine with transition validator |
| R-10 | Validation/eval system | File existence checks only | Doesn't prove plan completeness or behavior | Content validation + golden eval fixtures |
| R-11 | Parallel sprint state controls | Path-based ownership only | State drift in shared files possible | Section-level ownership + consistency checks |
| R-12 | Prompt/task contracts | Prose descriptions only | Implementation requires design decisions not in plan | Published Pydantic field definitions |
| R-13 | Telemetry -> Agent Metrics mapping | High-level "mapping rules" | 30 local fields to 17 Sheet fields: no concrete mapping | Explicit field-by-field aggregation spec |
| R-14 | Error recovery model | Not addressed | Every component described success-path only | Per-component failure handling spec |
| R-15 | Dependency version governance | Named tools, no versions | Upgrade could break behavior silently | Pinned versions + upgrade verification protocol |
