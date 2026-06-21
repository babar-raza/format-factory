# Specs Authority Layer — AI / Embeddings Usage Audit
**Run ID:** spec-auth-inv-20260621-002
**Date:** 2026-06-21

---

## Policy Statement (from AGENTS.md and GOVERNANCE.md)

> AI, LLMs, embeddings, vector DBs, rerankers, or semantic retrieval **may support** discovery,
> supervision, hardening, review, prioritization, and efficiency, but they **must not become
> the source of truth**. Final authority must remain deterministic, traceable, source-backed,
> versioned, and auditable.
>
> AI may help find candidate spec sections, summarize candidate gaps, detect contradictions,
> suggest questions, generate draft test ideas, and help reviewers inspect large text.
> AI must not create final authoritative facts unless those facts are independently grounded
> in source spec citations and deterministic validation.

This policy is formally documented and contractually captured in:
- `tools/ai/contracts/artifact-authority-states.yaml` (12-state machine)
- `AGENTS.md` §AF12-AF16
- `GOVERNANCE.md` §17 and §26.14
- `docs/llm-and-embedding-strategy.md`

---

## Section 1 — Current AI Usage

**Finding: No live AI/LLM calls are active in the current production system.**

Evidence:
- `.local/ai/` directory does NOT EXIST → no vector store has been instantiated
- No API keys or endpoint config in the repo
- `docs/llm-and-embedding-strategy.md` Status: "Backlog only. No LLM calls or embeddings created in this sprint."
- `tools/ai/run_ai_checks.py` exists but is NOT wired into `autonomous_cycle.py` or any supervisor step
- The AI authority lifecycle state machine (`tools/ai/validators/authority_lifecycle.py`) is implemented but NOT called from any product workflow

The "automated_extraction" method in 4,913 FACT-FODS-EX-* facts uses `deterministic_spec_text_search` (regex/lexical scan against normalized text), NOT an LLM. This is confirmed by the extraction metadata showing `xml_element_scan` pattern, no model_id, and no API call.

---

## Section 2 — Current Embeddings/Vector Usage

**Finding: No embeddings are created or used. No vector DB is instantiated.**

Evidence:
- `tools/ai/retrieval/namespace_manager.py` has full vector store design (format-segregated namespaces, chunk hash tracking, model fingerprint validation) but the instantiation directory `.local/ai/vector-stores/` does not exist
- TC-0015 (vector search evaluation) is required before TC-0016 (implementation) per AGENTS.md §X5-X7 and GOVERNANCE.md §17.2
- TC-0015 and TC-0016 are NOT marked complete in any evidence files found
- Gate restriction: "Tier 3 vector search may not be used in any Gate evidence artifact until TC-0016 is completed and independently verified"

The lexical retriever (`tools/ai/retrieval/lexical_retriever.py`) IS implemented and uses TF-based scoring (deterministic, no ML). This is correctly classified as Tier 1/2 retrieval, not Tier 3 vector search.

---

## Section 3 — Dormant AI Components

| Component | Path | Design Quality | Instantiation Status | Why Dormant |
|-----------|------|---------------|---------------------|-------------|
| Vector store namespace manager | `tools/ai/retrieval/namespace_manager.py` | HIGH — format-segregated, chunk-hash invalidation, model fingerprint tracking | NOT INSTANTIATED | TC-0015 evaluation not complete; TC-0016 not authorized |
| Authority lifecycle state machine | `tools/ai/validators/authority_lifecycle.py` | HIGH — 12-state machine, transition evidence required | IMPLEMENTED, NOT WIRED | No product workflow calls it |
| AI pipeline runner | `tools/ai/pipeline/runner.py` | HIGH — fixture mode works | PARTIAL — fixture mode tested | Live mode not authorized |
| Citation verifier | `tools/ai/synthesis/citation_verifier.py` | GOOD | IMPLEMENTED | Not wired to spec workbench |
| Contradiction detector | `tools/ai/synthesis/contradiction_detector.py` | GOOD | IMPLEMENTED | Not called |
| Evaluator | `tools/ai/pipeline/evaluator.py` | GOOD | IMPLEMENTED | Not called |
| Control plane (model router, discovery) | `tools/ai/control_plane/` | HIGH | IMPLEMENTED | No live AI endpoint configured |

---

## Section 4 — Missing-But-Useful AI Support

These are areas where AI support would be safe, useful, and within the existing policy framework:

| Use Case | Expected Benefit | Allowed Per Policy | Controls Needed |
|----------|-----------------|-------------------|-----------------|
| Candidate fact extraction from normalized text | Accelerate workbench build for CSV, DIF, GNUMERIC | YES — AGENTS.md §AF12 | Must cite spec text line; must flow through 12-state lifecycle; human review before promotion to verified |
| Spec section summarization for large ODF specs | Help identify relevant sections for FODT/FODP/FODG | YES | Citation required; output limited to ai_draft state |
| Cross-format contradiction detection | Detect when FODS and FODG have conflicting fact claims | YES | Contradiction flags must be human-reviewed; deterministic follow-up required |
| Requirement draft generation from verified facts | Speed up implementation-requirements.yaml creation | YES | Drafts stay in ai_draft state until verified against spec |
| Gap detection in section coverage | Identify spec sections with no requirements mapped | YES | `detect_coverage_gaps.py` already exists; AI could triage sections |

---

## Section 5 — Unsafe AI Paths (Must Remain Forbidden)

| Unsafe Path | Risk | Current Status |
|-------------|------|---------------|
| AI output directly promoted to "verified" fact without spec citation | Hallucinated requirements contaminate product | Policy forbids; 12-state machine blocks (ai_draft cannot skip to authoritative_after_gate) |
| Embeddings in Gate evidence bundles | Non-deterministic retrieval in gate proofs | Policy forbids (AGENTS.md §X5, GOVERNANCE.md §17.4) |
| Cross-format embedding queries | Format contamination | Policy forbids; namespace_manager.py enforces format isolation |
| LLM as spec authority (overriding spec text) | False claims enter product | Policy forbids; AGENTS.md §601 "not spec authority" |
| AI-generated requirements without source_id | Bypasses anti-bypass verifier | spec_verifier.py rejects source_id=null (14/14 adversarial tests prove this) |

---

## Section 6 — Recommended AI Support Architecture

The current design is correct. The following additions would bring it to production readiness:

### 6a. Wire authority_lifecycle.py into spec workbench population

When a new fact is added to verified-facts-review.yaml:
1. If extracted by AI: state = `ai_draft`
2. After spec_verifier passes: state = `source_verified`
3. After human review: state = `accepted_for_planning`
4. After gate evidence: state = `authoritative_after_gate`

Currently, facts are added directly as "verified" without state tracking.

### 6b. Activate lexical_retriever.py in acquisition planning

Use `query_normalized_spec.py` + `lexical_retriever.py` during acquisition-pack generation to automatically find relevant spec sections for a format task. This is Tier 1/2 and needs no additional authorization.

### 6c. AI-assisted coverage gap triage (safe, immediate)

Run `detect_coverage_gaps.py` on FODT, ZST workbenches. Use AI summarization (ai_draft state) to suggest candidate sections for manual fact extraction.

---

## Section 7 — Controls Required Before AI Output Can Affect Requirements

Before any AI-generated output can enter the requirements or product workflow:

1. **Source citation required**: Every AI-generated fact must carry `source_id` (from registered source), `section_id`, and `text_fragment` matching spec text.
2. **spec_verifier.py must run**: `verify_requirements()` must accept the fact before it can advance past `source_verified`.
3. **Human review required**: AI output must advance through at least `accepted_for_planning` before entering implementation-requirements.yaml.
4. **No Gate evidence**: AI output must not appear in Gate evidence until `authoritative_after_gate` — which requires Gate evaluation (TC-0015).
5. **Logging required**: Model ID, provider, input hash, output hash, and lifecycle state must be recorded in the fact provenance.
6. **Format isolation**: AI retrieval (when implemented) must use namespace_manager.py to prevent cross-format contamination.

---

## Section 8 — Explicit Statement: AI Is Not Authority

> **AI IS NOT AUTHORITY in this system.**
>
> AI components in this repository are assistive tools for discovery, review, drafting, and
> efficiency. They operate under the 12-state lifecycle machine that prevents AI output from
> reaching the "authoritative" state without independent spec citation, deterministic verification,
> and human review at gated transitions.
>
> The specification source (cached PDF, RFC text, or formal standard) is the ONLY authority.
> SHA-256 verification of the source, section-level citation, and deterministic text verification
> (spec_verifier.py) are the enforcement mechanisms.
>
> Embeddings are designed to support RETRIEVAL over already-verified spec text, not to generate
> facts. The namespace manager enforces format isolation and model-fingerprint-based invalidation.
>
> This policy is contractually captured in `tools/ai/contracts/artifact-authority-states.yaml`
> and operationally enforced by `tools/ai/validators/authority_lifecycle.py`.

---

## Overall AI/Embeddings Rating

**UNUSED_BUT_NOT_REQUIRED (plus well-designed for future safe use)**

- No AI is active or necessary for the current workbench coverage
- The 78 hand-curated FODS facts and auto-extracted EX facts use deterministic methods
- The AI platform is designed correctly with appropriate safeguards
- Controls are in place (12-state machine, namespace isolation, citation requirement)
- Missing: authority_lifecycle.py not wired into production workbench population
- Next authorized AI action: activate lexical_retriever.py for new format acquisition; then TC-0015 evaluation if vector search is desired
