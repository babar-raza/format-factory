# Specs Authority Layer — AI / Embeddings Usage Audit
# Sprint: SPEC-AUTHORITY-LAYER-PRODUCTION-INVESTIGATION-001
# Generated: 2026-06-06

---

## Governing Policy Statement

**AI may help find candidate spec sections, summarize candidate gaps, detect
contradictions, suggest questions, generate draft test ideas, and help reviewers
inspect large text. AI must not create final authoritative facts unless those
facts are independently grounded in source spec citations and deterministic
validation.**

This audit verifies compliance with that policy.

---

## 1. Current AI Usage

### 1.1 LLM / Completion API Usage

| Component | Path | Purpose | Active | Affects Authority | Source-Cited | Deterministic | Tests | Fail-Closed |
|-----------|------|---------|--------|------------------|--------------|---------------|-------|-------------|
| tools/llm/ | tools/llm/ | LLM endpoint abstraction layer | PRESENT | No (downstream use determines) | N/A | N/A | Unknown | Unknown |
| tools/ai/ | tools/ai/ | AI pipeline (normalization, requirements, synthesis, retrieval, test_generation) | PRESENT but not connected to spec authority pipeline | Potentially | Partial | NO | Unknown | Unknown |
| Claude Code session | Runtime agent | Sprint execution, code writing, investigation | ACTIVE | YES (agent writes implementation code) | NO — agent writes from memory+context | NO | N/A | N/A |

### 1.2 Key Finding on Agent-as-Authority Risk

The most significant AI authority risk found in this investigation is not a
tool-level issue — it is at the **agent execution level**.

**Observed pattern:**
- Agent (Claude Code) writes parser/writer code based on task prompts
- Task prompts reference acquisition packs that have partial spec references
- Agent code does NOT cite verified spec facts
- Evidence is declared ACCEPTED without spec fact backing

This means **LLM-generated implementation code is effectively treated as
authoritative** because there is no enforcement gate requiring spec_fact_refs
in evidence declarations for PRODUCT_SOURCE work items.

**This is the critical AI authority contamination path.**

### 1.3 Requirements Pipeline

| File | Purpose | Status |
|------|---------|--------|
| docs/ai-generated-format-requirements-pipeline.md | Design for AI-assisted requirements generation | DESIGN ONLY — not operational |
| docs/ai-generated-format-requirements-pipeline.yaml | Schema for above | DESIGN ONLY |
| tools/ai/ | AI pipeline implementation | PRESENT but disconnected from authority layer |

The `tools/ai/` directory contains:
- `agentic/` — agentic control plane
- `contracts/` — AI output contracts
- `control_plane/` — pipeline orchestration
- `normalization/` — text normalization AI
- `pipeline/` — end-to-end pipeline
- `prompts/` — prompt templates
- `requirements/` — AI requirements generation
- `retrieval/` — AI-assisted retrieval
- `run_ai_checks.py` — AI check runner
- `schemas/` — AI output schemas
- `synthesis/` — AI synthesis
- `telemetry/` — AI telemetry
- `test_generation/` — AI test generation
- `validators/` — AI output validation

**Finding:** This is a large AI subsystem designed to support the spec authority
layer, but it appears disconnected from the active acquisition pipeline. The
authority_integration_fabric does NOT import from tools/ai. Tests for these
AI components were not found in the active test discovery path.

---

## 2. Current Embeddings / Vector Usage

| Component | Status | Evidence |
|-----------|--------|---------|
| `.local/embeddings/` directory | DOES NOT EXIST | Confirmed via ls command |
| Vector database | NOT PRESENT | No chromadb, qdrant, pinecone, weaviate, faiss in requirements |
| Embedding model | NOT INSTALLED | No sentence-transformers, openai-embeddings, or similar in active venv |
| Tier 3 vector search | DESIGN ONLY | docs/spec-retrieval-strategy.md marks it "awaiting TC-0015" |
| tools/ai/retrieval/ | UNKNOWN state | May contain vector retrieval design; not connected to pipeline |

**Finding:** No embeddings or vector search are active. Policy documents
correctly prohibit Tier 3 for gate evidence. This is compliant.

---

## 3. Dormant AI Components

| Component | Location | What It Does | Risk if Activated Without Controls |
|-----------|----------|-------------|----------------------------------|
| AI requirements pipeline | tools/ai/requirements/ | Generates requirements from spec text using LLM | HIGH — output would be AI-generated, not spec-verified; blocks must prevent acceptance |
| AI synthesis | tools/ai/synthesis/ | Synthesizes facts from spec chunks | HIGH — synthesis output is candidate, not verified |
| AI test generation | tools/ai/test_generation/ | Generates test cases from requirements | MEDIUM — tests from unverified requirements inherit the verification debt |
| AI normalization | tools/ai/normalization/ | AI-assisted text normalization | LOW — if output is deterministic and validated against raw text |
| Embedding retrieval | tools/ai/retrieval/ | Semantic similarity over spec chunks | HIGH without source-hash invalidation and citation requirements |
| Telemetry | tools/ai/telemetry/ | AI usage telemetry | LOW if logging only |

---

## 4. Missing-But-Useful AI Support (Safe Roles)

| AI Use Case | Safety Classification | Required Controls |
|-------------|----------------------|-------------------|
| Candidate section finder: "which sections of ZST RFC mention content integrity?" | SAFE — assistive discovery | Must cite section IDs; output is candidate only; human reviews |
| Gap detector: "what requirements in the spec are not covered by current verified facts?" | SAFE — assistive review | Must run over indexed spec; output drives investigation, not authority |
| Contradiction detector: "does this implementation requirement contradict this spec section?" | SAFE — assistive quality | Must cite both the impl req and the spec section; human confirms |
| Draft test generator: "write a test for FACT-FODS-001 about office:document root" | SAFE — assistive drafting | Generated test must be reviewed; test does not become authoritative until human confirms |
| Large spec summarizer: "summarize sections 3.1-3.5 of ODF 1.3 for human review" | SAFE — human efficiency | Summary is not authority; human reads primary source before creating facts |

---

## 5. Unsafe AI Paths (Must Be Prevented)

| Unsafe Path | Why Unsafe | Current Status | Control Needed |
|-------------|-----------|----------------|---------------|
| Agent writes parser code based on memory of spec (no cached spec required) | LLM memory is unreliable; cannot be audited; may hallucinate format details | CURRENTLY HAPPENING for most formats | Require spec_fact_refs in evidence declaration for PRODUCT_SOURCE work |
| AI generates requirements with status "verified" directly | Bypasses human review; contaminated authority | Not currently happening (validate_generated_requirements.py blocks it) | Keep blocker; add tests for regression |
| Embedding search result treated as spec authority without citation | Vector similarity ≠ spec compliance | Not currently happening | Add explicit prohibition in gate criteria |
| AI summary in context pack without source-hash binding | Context pack could drift from spec without detection | context_pack_builder.py requires SHA; controls exist | GOOD — maintain |
| AI-only justification for gate approval | Gate approver (Babar Raza) may rely on AI summary without reading spec | Not enforced programmatically | Add requirement that gate decisions cite primary spec sections |

---

## 6. Recommended AI Support Architecture

The following safe AI support architecture is recommended once verified-fact
extraction is operational:

```
Stage 1 — Discovery (SAFE)
  Agent/AI → finds candidate spec sections by keyword/semantic search
  → Output: section IDs (e.g., "RFC 8878 §3.1") — NOT authority

Stage 2 — Extraction (SAFE with controls)
  Deterministic tool → extracts text from spec at found section IDs
  → Output: exact spec text with source hash + page + section ID

Stage 3 — Candidate Fact Creation (SAFE)
  AI → proposes candidate fact from exact spec text
  → Output: CandidateRequirement with status="candidate"
  → NEVER status="verified" from AI alone

Stage 4 — Verification (HUMAN REQUIRED)
  Human reviewer → reads primary spec text at cited location
  → Confirms or rejects candidate fact
  → Sets status="verified" or status="rejected"

Stage 5 — Authority (DETERMINISTIC)
  Verified fact → implementation requirement → code → test
  → All traceable back to verified fact ID
  → AI may not override verified fact without new human review
```

---

## 7. Controls Required Before AI Output Can Affect Requirements

These controls must ALL be in place before any AI-generated content can
influence the authority layer:

| Control | Status | Implementation |
|---------|--------|---------------|
| AI proposals must use status="candidate" | IMPLEMENTED (validate_generated_requirements.py) | KEEP |
| AI-only proposals cannot be accepted | IMPLEMENTED (validate_generated_requirements.py) | KEEP |
| Source_refs required for non-product-decision requirements | IMPLEMENTED | KEEP |
| Context packs must have manifest SHA-256 | IMPLEMENTED | KEEP |
| AI output must cite spec section ID + page + source hash | DESIGNED but not enforced in pipeline | IMPLEMENT |
| Human verification step must set status="verified" | DESIGNED but not enforced in pipeline | IMPLEMENT |
| Usage ledger must capture all AI-touching actions | DESIGNED (spec_governance_runtime.py) | VERIFY PERSISTENCE |
| Model/provider/configuration captured at inference time | NOT IMPLEMENTED | IMPLEMENT before activating tools/ai/ |
| Prompts stored and versioned alongside AI output | NOT VERIFIED | IMPLEMENT |

---

## 8. Explicit Statement: AI Is Not Authority

**AI output — whether from Claude, GPT-4, embeddings, or any other model —
is not a source of authority for the Format Factory specification compliance layer.**

AI may:
- Help locate candidate spec sections
- Draft candidate requirements (status="candidate" only)
- Generate test ideas for human review
- Assist reviewers in understanding large spec documents

AI must not:
- Set requirement status to "verified" unilaterally
- Justify a gate decision without a primary spec citation
- Generate spec facts that enter the proof graph as authoritative nodes
- Write implementation code that is treated as spec-compliant without a verified-fact chain

The current system is partially compliant with this principle:
- `validate_generated_requirements.py` enforces AI-proposal blocking (GOOD)
- But agent-written implementation code is not gated against verified facts (GAP)
- The tools/ai/ subsystem is not connected to the authority layer (reduces risk, but also means AI support for large spec navigation is unavailable)
