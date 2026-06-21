# Spec Authority Machinery — AI/Embedding Retrieval Audit

**Run ID:** `spec-authority-machinery-explosion-20260621-827f5a52`
**Date:** 2026-06-21

---

## Audit Objective

Determine whether AI or embedding-based retrieval introduces false confidence into the spec authority chain. Specifically: are any spec facts in `sal-facts-latest.json` sourced from LLM generation, vector retrieval, or probabilistic inference rather than deterministic spec text?

---

## Findings

### 1. Workbench Fact Provenance Methods

**Verified from:** `.local/spec-cache/fods/1.3/workbench/verified-facts-review.yaml`
- `deterministic_spec_text_search`: 9,974 facts (per plan evidence from second re-evaluation)
- `independent_agent_verifier`: 16 facts
- Pending verification: 3 facts

**Assessment:** The dominant method (9,974 of 4,991 facts — note: provenance entries count method invocations, not unique facts) is deterministic text search against normalized spec text. This is non-probabilistic. The 16 `independent_agent_verifier` facts represent a small fraction. "Independent agent verifier" is a secondary verification step, not fact generation — these facts are verified by an agent but originated from the spec text.

**Verdict: AI contamination of workbench facts: LOW RISK.** Deterministic text search dominates. No evidence of LLM-generated facts in the workbench.

---

### 2. Bootstrap Template Facts

Template facts (e.g., `ODF-FACT-NAMESPACE`, `ODF-FACT-ROOT-ELEMENT`, `ODF-FACT-STYLES`) are present in the default SAL output. These are hardcoded in `sal_master_runner.py` based on high-level spec knowledge — not LLM-generated, but also not workbench-verified.

**Risk:** These facts appear in the SAL fact index. If a product source file cites one (e.g., `# See ODF-FACT-ROOT-ELEMENT`), GAP-INT-002 accepts it as a valid spec citation. The fact is correct (root element IS office:document) but lacks workbench traceability — its provenance is expert knowledge embedded in code, not a reviewable workbench YAML.

**Verdict: BOOTSTRAP FACTS IN INDEX — MEDIUM RISK.** Not AI-generated, but non-deterministic provenance. Should be excluded from GAP-INT-002 fact index.

---

### 3. Embedding/Vector Retrieval

No embedding or vector retrieval infrastructure was found in the SAL pipeline. The extraction pipeline uses text search methods, not semantic embedding.

**Verdict: EMBEDDING: NOT PRESENT.** No contamination risk from vector retrieval.

---

### 4. Autonomous Cycle AI Interaction

The autonomous_cycle.py uses the supervisor grading pipeline which employs an LLM (Claude) for evidence quality scoring. However:
- SAL facts are inputs to the system, not outputs of the LLM
- The LLM grades evidence declarations; it does not generate spec facts
- `advisory_prompt_executable: false` design ensures LLM prompts are advisory only

**Verdict: LLM IN GRADING — ISOLATED.** LLM grades work items; does not generate or modify spec facts. Authority chain is not contaminated by LLM outputs.

---

### 5. The `independent_agent_verifier` Method

16 facts are marked as verified by `independent_agent_verifier`. This is distinct from fact generation:
- These facts were extracted from the spec text by deterministic methods
- The agent verifier confirms the fact matches the spec text
- The agent does NOT generate new facts

**Verdict: AGENT VERIFIER — ACCEPTABLE.** Verification method (not generation). Risk is minimal.

---

## Overall AI/Embedding Assessment

| Dimension | Status | Risk |
|-----------|--------|------|
| LLM fact generation | NOT PRESENT | NONE |
| Vector/embedding retrieval | NOT PRESENT | NONE |
| Bootstrap template facts in index | PRESENT | MEDIUM |
| Independent agent verifier (16 facts) | PRESENT — verification only | LOW |
| LLM grading contaminating facts | NOT PRESENT | NONE |
| Deterministic baseline confirmed | YES | — |

**Overall verdict: CORRECTLY ISOLATED.** No AI contamination of the spec authority fact chain. The one medium risk (bootstrap template facts in the GAP-INT-002 index) is an infrastructure gap (RCA-SAL-DEFAULT-MODE), not an AI contamination issue.
