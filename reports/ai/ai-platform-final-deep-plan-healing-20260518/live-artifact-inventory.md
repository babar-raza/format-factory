# Live Artifact Inventory

**Sprint:** FORMAT-FACTORY-AI-PLATFORM-FINAL-DEEP-PLAN-HEALING-001
**Date:** 2026-05-18
**Gate:** 2
**Lane:** L2

---

## Methodology

Every artifact listed in the prior plan was verified against live repo state using `ls`, `glob`, and `read`. Classifications: present_current, present_stale, missing, contradictory, superseded, out_of_scope.

## docs/ai/ — Policy Documents (11 files)

| File | Status | Notes |
|------|--------|-------|
| `docs/ai/ai-platform-operating-model.md` | present_current | Master design, PLAN status |
| `docs/ai/model-routing-and-discovery-policy.md` | present_current | Role routing, discovery |
| `docs/ai/agentic-qwen2-control-policy.md` | present_current | Qwen2 controls |
| `docs/ai/gpt-oss-synthesis-control-policy.md` | present_current | GPT-OSS controls |
| `docs/ai/embedding-and-vector-store-policy.md` | present_current | Vector store policy |
| `docs/ai/ai-telemetry-and-agent-metrics-policy.md` | present_current | Telemetry policy |
| `docs/ai/ai-risk-register.md` | present_current | 48 risks (RISK-AI-001 through 048) |
| `docs/ai/ai-artifact-authority-lifecycle.md` | present_current | 12-state machine |
| `docs/ai/ai-assisted-acquisition-pipeline.md` | present_current | Gate integration |
| `docs/ai/ai-technology-decision-record.md` | present_current | Tech decisions |
| `docs/ai/deferred-ai-features-review.md` | present_current | Deferred classification |

## taskcards/AI-*.md — AI Taskcards (17 files)

| File | Status | Notes |
|------|--------|-------|
| `AI-PLATFORM-FOUNDATION-PLAN.md` | present_current | plan_hardened |
| `AI-MODEL-DISCOVERY-AND-ROUTING.md` | present_current | plan_hardened |
| `AI-AGENTIC-QWEN2-CONTROLS.md` | present_current | plan_hardened |
| `AI-GPT-OSS-SYNTHESIS-CONTROLS.md` | present_current | plan_hardened |
| `AI-EMBEDDING-VECTOR-STORE-FOUNDATION.md` | present_current | plan_hardened |
| `AI-TELEMETRY-AGENT-METRICS-INTEGRATION.md` | present_current | plan_hardened |
| `AI-SPEC-NORMALIZATION-INTEGRATION.md` | present_current | plan_hardened |
| `AI-TEST-GENERATION-INTEGRATION.md` | present_current | plan_hardened |
| `AI-RISK-MITIGATION-MATRIX.md` | present_current | plan_hardened |
| `AI-FOUNDATION-IMPLEMENTATION-NEXT.md` | present_current | planned |
| `AI-USAGE-OPERATING-MODEL.md` | present_current | plan_hardened |
| `AI-SPEC-RETRIEVAL-RAG-POLICY.md` | present_current | plan_hardened |
| `AI-COMMERCIAL-DEVELOPMENT-PATTERNS.md` | present_current | plan_hardened |
| `AI-USAGE-LEDGER-AND-METRICS.md` | present_current | plan_hardened |
| `AI-VALIDATION-GATES.md` | present_current | plan_hardened |
| `AI-GENERATED-FORMAT-REQUIREMENTS-PIPELINE.md` | present_current | plan_hardened |
| `AI-PLATFORM-FINAL-PLAN-HEALING.md` | contradictory | Status says closed but healing sprint is being re-run |

## Legacy Taskcards

| File | Status | Notes |
|------|--------|-------|
| `LLM-001-llm-professionalize-model-discovery.md` | superseded | Body says superseded by AI-MODEL-DISCOVERY-AND-ROUTING; frontmatter status still says `proposed_pending_human_approval` |
| `EMB-001-controlled-embedding-retrieval-design.md` | superseded | Body says superseded by AI-EMBEDDING-VECTOR-STORE-FOUNDATION; frontmatter status still says `proposed_pending_human_approval` |

## reports/ai/ — Plan Reports

| File | Status | Notes |
|------|--------|-------|
| `reports/ai/ai-platform-plan-20260518/ai-platform-architecture-plan.md` | present_current | Main plan |
| `reports/ai/ai-platform-plan-20260518/current-ai-usage-audit.md` | present_current | Usage audit |
| `reports/ai/ai-platform-plan-20260518/ai-platform-gap-root-cause-analysis.md` | present_current | Gap analysis |
| `reports/ai/ai-platform-plan-20260518/technology-decision-report.md` | present_current | Tech decisions |
| `reports/ai/ai-platform-plan-20260518/risk-register-and-control-matrix.md` | present_current | Risk summary |
| `reports/ai/ai-platform-plan-20260518/implementation-roadmap.md` | present_current | 7-phase roadmap |
| `reports/ai/ai-platform-plan-20260518/validation-and-regression-strategy.md` | present_stale | Needs deeper validation model |
| `reports/ai/ai-platform-plan-20260518/parallel-sprint-safety-plan.md` | present_current | Path ownership |
| `reports/ai/ai-platform-plan-20260518/deferred-feature-decision-log.md` | present_current | 30+ items classified |
| `reports/ai/ai-platform-plan-20260518/final-execution-readiness-review.md` | present_stale | Verdict not earned by deep review |

## reports/ai/ — Deep Review (prior session, untracked)

| File | Status | Notes |
|------|--------|-------|
| `reports/ai/ai-platform-deep-review-20260518/symptoms-root-causes-structural-weaknesses.md` | present_current | Good depth, absorb |
| `reports/ai/ai-platform-deep-review-20260518/rerun-consistency-failure-analysis.md` | present_current | 17 breakers, absorb |
| `reports/ai/ai-platform-deep-review-20260518/preserve-vs-redesign-matrix.md` | present_current | 15+15 items, absorb |
| `reports/ai/ai-platform-deep-review-20260518/production-solution-architecture.md` | present_current | 15 components, absorb |

## Memory and Config

| File | Status | Notes |
|------|--------|-------|
| `memory/42-ai-llm-embedding-platform-plan-hardening-20260518.md` | present_current | Needs update for this sprint |
| `memory/00-index.md` | present_current | References memory/42 |
| `tools/llm/endpoints.yaml` | present_current | Config only, no secrets |

## Evidence Contracts

| File | Status | Notes |
|------|--------|-------|
| `tools/evidence/contracts/ai-platform-architecture-plan-20260518.yaml` | present_current | Needs update for healing sprint |
| `tools/evidence/contracts/ai-llm-embedding-plan-hardening-sync.yaml` | present_current | Prior sprint |

## Implementation Code Check

| Check | Result |
|-------|--------|
| `tools/ai/*.py` | NONE — no implementation code exists |
| `tools/ai/` directory | DOES NOT EXIST |
| AI imports in `src/python/` | NONE |
| AI imports in `src/net/` | NONE |

## Inventory Verdict

**47 artifacts located.** 2 present_stale (validation strategy, execution readiness), 2 contradictory/superseded (taskcard status, LLM-001/EMB-001 frontmatter), 0 missing, 4 deep-review files available for absorption. No implementation code found anywhere.

## State Transition

| Timestamp | From | To | Lane | Evidence | Notes |
|-----------|------|----|------|----------|-------|
| 2026-05-18T00:03:00Z | current_plan_audited | live_artifacts_verified | L2 | this file | 47 artifacts verified |
