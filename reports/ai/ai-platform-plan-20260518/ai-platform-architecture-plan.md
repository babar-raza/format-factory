# AI Platform Architecture Plan

**Sprint:** FORMAT-FACTORY-AI-PLATFORM-FINAL-PLAN-HEALING-AND-IMPLEMENTATION-READINESS-001
**Date:** 2026-05-18
**Status:** PLAN — Implementation not yet authorized

## 1. Executive Summary

Format Factory will build a generic, segregated, reusable, production-grade AI/LLM/Embedding platform layer. All AI usage flows through one governed substrate. The platform is designed once and hardened deeply — not assembled from ad hoc endpoint calls.

## 2. Architecture Overview

### 2.1 Three AI Usage Types

**Type A — Agentic Reasoning / Task Execution**
- High-risk: Claude/Codex (outside llm.professionalize.com)
- Low-risk: Qwen2 via llm.professionalize.com with strict controls
- All agentic work governed by role contracts, task contracts, path scoping, state machines, validators, IV, evidence, rollback rules

**Type B — LLM Transformation / Synthesis**
- Preferred: GPT-OSS via llm.professionalize.com
- Use cases: spec extraction, requirement drafting, test generation, security analysis, evidence review
- Controls: citation verification, contradiction detection, evaluator regression, authority lifecycle

**Type C — Embeddings / Retrieval**
- Source: embedding model via llm.professionalize.com (auto-detected)
- Vector stores: format-segregated, permanent, project-local (.local/ai/vector-stores/)
- Never authority; hash-invalidated; replayable

### 2.2 Mandatory Control Plane

Infrastructure governing all AI usage:
- Model discovery and capability probing
- Role-based model routing (not hardcoded)
- Task contracts (Pydantic v2)
- Prompt registry (versioned, immutable, hash-tracked)
- Schema registry
- Artifact authority lifecycle enforcement
- Validators and evaluators
- Telemetry (Agent Metrics canonical, JSONL spool)
- Evidence bundle integration
- Runtime AI-free guard

### 2.3 Directory Layout

```
tools/ai/                        # AI platform (repo tools only)
  control_plane/                 # Discovery, routing, contracts
  agentic/                       # Agent runner, state machine, scope guard
  synthesis/                     # Synthesis runner, citation, contradiction
  retrieval/                     # Embeddings, vector store, chunk manifest
  telemetry/                     # Logging, Agent Metrics, spool
  validators/                    # Schema, authority, runtime guard
  contracts/                     # Task contract definitions
  prompts/                       # Versioned prompt templates
  schemas/                       # Pydantic models
  evals/                         # Golden evaluation datasets

.local/ai/                       # Runtime state (gitignored)
  vector-stores/{format}/        # LanceDB per format
  llm-logs/                      # Per-call JSONL
  spool/                         # Agent Metrics offline spool
  cache/                         # Prompt/response cache
  model-registry/                # Discovered model capabilities
```

### 2.4 Segregation Boundary

Runtime product code (`src/python/**`, `src/net/**`) MUST NOT import AI infrastructure. Enforced by static analysis (`tools/ai/validators/runtime_guard.py`).

## 3. Environment Configuration

- `GPT_OSS_API_KEY` — authentication
- `GPT_OSS_ENDPOINT` — base URL
- No hardcoded model names, endpoints, or credentials in any committed file

## 4. Implementation Phases

| Phase | Scope | Key Gate |
|-------|-------|----------|
| 1 | Control plane, routing, telemetry, runtime guard | One endpoint verified, telemetry logging |
| 2 | GPT-OSS synthesis, evals, test generation | One synthesis task passing full validation |
| 3 | Embeddings, LanceDB, format indexes | One format indexed with reproducible retrieval |
| 4 | Qwen2 agentic, source generation | One low-risk task completing full lifecycle |
| 5 | Agent Metrics full integration, replay | Telemetry flowing to Agent Metrics |
| 6 | Hardening, regression, cross-format isolation | All risk register items have validation tests |

## 5. Authority Documents

Primary: `docs/ai/ai-platform-operating-model.md`
Governance: `GOVERNANCE.md` 26.14, `AGENTS.md` AF16
Master plan: `plans/master-plan.md` Section 39
Risk register: `docs/ai/ai-risk-register.md` (48 risks)
Technology decisions: `docs/ai/ai-technology-decision-record.md`

## 6. Implementation Not Yet Authorized

This plan must be reviewed by human authority before Phase 1 begins.
