# Agentic Qwen2 Control Policy

**Version:** 1.0
**Date:** 2026-05-18
**Status:** PLAN — Implementation not yet authorized
**Authority:** docs/ai/ai-platform-operating-model.md

---

## 1. Purpose

Define the controls required when using Qwen2 (via llm.professionalize.com) for agentic work within Format Factory. Qwen2 may be used for lower-risk agentic tasks but requires firm governance — not just tests and evidence, but structural controls that prevent scope drift, unvalidated mutations, and authority escalation.

## 2. Scope Classification

### 2.1 Allowed Scope (Low-Risk Agentic)

Qwen2 may perform:
- Format candidate classification and scoring
- Artifact sorting and categorization
- Simple fact extraction from structured inputs
- Report template population
- Evidence checklist verification
- File listing and inventory tasks
- Metadata extraction from known schemas

### 2.2 Forbidden Scope

Qwen2 MUST NOT perform:
- Direct repository mutations (commits, branch operations)
- Gate evidence generation that becomes authoritative
- Security analysis or vulnerability assessment
- Generated requirements that feed into implementation
- Code generation for product source (`src/`)
- Test generation for product test suites
- Any task classified as `agentic_high_risk`
- Authority file modifications (master plan, GOVERNANCE.md, AGENTS.md)
- Evidence bundle building or validation
- Release or publication decisions

## 3. Required Controls

Every Qwen2 agentic invocation must have:

### 3.1 Pre-Execution Controls

| Control | Description |
|---------|-------------|
| Role contract | YAML defining the agent role, allowed operations, forbidden operations |
| Task contract | Pydantic schema defining inputs, expected outputs, success criteria |
| Path allowlist | Explicit list of file paths the agent may read |
| Write allowlist | Explicit list of file paths the agent may write (empty for read-only tasks) |
| Operation allowlist | Allowed operations (read, classify, extract, report) |
| Model capability check | Verify Qwen2 meets minimum for the task via capability probe |
| Governance check | Confirm task is classified as low-risk in task contract |

### 3.2 Execution Controls

| Control | Description |
|---------|-------------|
| State-machine guard | Task follows defined states: `initialized → running → validating → accepted/rejected` |
| Output schema | All outputs validated against Pydantic schema before acceptance |
| Scope monitor | Runtime check that agent has not accessed files outside allowlist |
| Token budget | Maximum input + output tokens per invocation |
| Timeout | Maximum wall-clock time per task |
| Error handler | On error: stop, log, do not retry without human review |

### 3.3 Post-Execution Controls

| Control | Description |
|---------|-------------|
| Validator checks | Deterministic validation of all outputs |
| Independent verification | If output affects any authority file: DEC-034 IV required |
| Evidence capture | Task contract, inputs, outputs, telemetry included in evidence |
| Rollback rules | If validation fails: discard output, log failure, report to human |
| Authority state | Output tagged as `ai_draft` — cannot become authoritative without further gates |

## 4. Output Authority

Qwen2 output is **advisory** until:
1. Deterministic schema validation passes
2. Task-specific validator checks pass
3. Output is accepted through task state machine
4. If authority-affecting: DEC-034 independent verification completes
5. Human review approves promotion from `ai_draft`

Qwen2 output MUST NOT:
- Directly modify authority files
- Be treated as evidence without validation
- Bypass the artifact authority lifecycle
- Influence gate decisions without human review

## 5. Telemetry Requirements

Every Qwen2 call must log:
- All fields from `docs/ai/ai-telemetry-and-agent-metrics-policy.md`
- Additional field: `qwen2_risk_classification: low_risk`
- Additional field: `qwen2_scope_check: pass/fail`
- Additional field: `qwen2_output_authority_state: ai_draft`

## 6. Failure Modes

| Failure | Response |
|---------|----------|
| Qwen2 unavailable at endpoint | Fail closed. Do not substitute another model for agentic work. |
| Qwen2 output fails schema validation | Reject output. Log. Do not retry automatically. |
| Qwen2 attempts to access file outside allowlist | Stop task immediately. Log scope violation. |
| Qwen2 produces output exceeding token budget | Truncate and reject. Log. |
| Qwen2 output contradicts verified facts | Reject output. Flag for human review. |

## 7. Cross-References

| Document | Relationship |
|----------|-------------|
| `docs/ai/ai-platform-operating-model.md` | Parent platform model, Type A controls |
| `docs/ai/model-routing-and-discovery-policy.md` | Qwen2 routing constraints |
| `docs/ai/ai-artifact-authority-lifecycle.md` | Output authority states |
| `docs/ai/ai-risk-register.md` | RISK-AI-021 (Qwen2 exceeding task scope) |
