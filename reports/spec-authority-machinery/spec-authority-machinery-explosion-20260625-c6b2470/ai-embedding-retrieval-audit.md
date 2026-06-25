# AI / Embedding / Retrieval Audit
## Run ID: spec-authority-machinery-explosion-20260625-c6b2470

---

## 1. What Exists

### AI Tools (labeled ai_draft — NOT in production path)

| Tool | Location | Label | Role | Status |
|------|----------|-------|------|--------|
| `ai_evidence_critic.py` | `tools/spec-cache/` | ai_draft | Review evidence quality against spec facts | Exists, NOT called from production |
| `ai_implementation_designer.py` | `tools/spec-cache/` | ai_draft | Suggest implementation patterns from spec facts | Exists, NOT called from production |
| `ai_spec_section_extractor.py` | `tools/spec-cache/` (assumed) | ai_draft | Extract spec sections for LLM summarization | Advisory only |

### Policy Documents (sound — not runtime-enforced)

| Document | Key Rules | Enforcement Status |
|----------|-----------|-------------------|
| `docs/governance/ai-authority-boundary.md` | AI may assist; AI cannot be spec authority | Policy only — no runtime validator |
| `docs/llm-and-embedding-strategy.md` | LLM outputs labeled ai_draft; human verification required | Policy only — no runtime validator |
| `docs/spec-retrieval-and-rag-policy.md` | Tier-based retrieval: exact spec text > AI summary > paraphrase | Policy only — not runtime-enforced |
| `docs/spec-retrieval-strategy.md` | Retrieval design: spec text → chunk → embedding → similarity search | Design only — no active embedding pipeline |

---

## 2. What Is Absent From Production

### Embeddings: NOT DEPLOYED

No embedding pipeline is active in any production or advisory path:
- No vector database (Chroma, Pinecone, Weaviate, FAISS) configured
- No embedding generation step in spec normalization pipeline
- chunks.jsonl exists for FODS but NOT embedded in any vector store
- Workers have no mechanism to query "what does the spec say about {element}?" at runtime

### RAG Pipeline: DESIGN ONLY

The `docs/spec-retrieval-and-rag-policy.md` describes a tier-based retrieval design:
- Tier 1: Exact spec text match (character-level)
- Tier 2: Semantic similarity search over spec chunks
- Tier 3: AI-generated summary from verified facts

None of these tiers are active in the production path. Workers execute without access to any retrieval mechanism.

### LLM Authority Guard: POLICY ONLY

`docs/governance/ai-authority-boundary.md` forbids AI from being spec authority. The policy is:
- AI can SUGGEST candidate facts → requires human verification before P4+
- AI can DRAFT test patterns → requires human review before acceptance
- AI CANNOT label its output as verified without human sign-off

But there is no runtime validator (V-number) that:
- Prevents ai_draft artifacts from being cited in evidence as authoritative
- Detects when AI-generated text was promoted to verified status without human sign-off
- Blocks sprint acceptance when spec_fact_refs point to ai_draft sources

---

## 3. Risk Assessment

### Current Risk: LOW-MODERATE

AI tools are NOT in the production path. No AI-generated content is being promoted to verified spec fact status. The risk is future-state (what happens if ai_draft tools are promoted without guards).

### Future Risk: MODERATE if unaddressed

If the system adds LLM-assisted spec summarization without runtime guards:
- AI-generated "facts" could contaminate the verified facts workbench
- Proof graphs could include AI-sourced evidence without attribution
- Product code could cite "facts" that have no verified spec backing

---

## 4. Safe AI Assist Opportunities

These are safe uses of AI in spec authority work — all require human verification before P4:

| Opportunity | Description | Guard Required |
|-------------|-------------|----------------|
| Spec section candidate retrieval | Given a format element name, retrieve most relevant spec sections via similarity search on chunks.jsonl | Label output ai_draft; require human acceptance before P4 |
| Contradiction detection | Compare code behavior assertions against spec fact assertions; flag potential contradictions for human review | Label flagged items ai_contradiction_candidate; require human adjudication |
| Candidate test generation | Generate test skeleton from verified facts (FACT-{FMT}-NNN) with human-visible spec reference | Label output ai_draft_test; require human to verify behavioral assertions before committing |
| Requirement pack summarization | Summarize a group of verified facts into a structured requirement pack | Label output ai_draft_requirement; require human to verify against spec text |
| T3 authorization pre-check | Given a spec URL, determine if it meets T3 authorization conditions (legal category, redistribution policy) | Advisory only; human operator must sign off on T3 authorization |

---

## 5. Recommendations

### Immediate (no risk added)
1. No changes to AI tooling required now — policy is correct and AI is not in production
2. Document the safe-use opportunities above as a future roadmap item

### Phase E (after Phase A-D repairs, see healing-roadmap.md)
1. Deploy embedding pipeline for FODS chunks.jsonl (already chunked) → Chroma/FAISS local instance
2. Wire ai_spec_section_extractor.py to a spec chunk retrieval endpoint
3. Add V49 governance validator: "PRODUCT_SOURCE items MUST NOT cite ai_draft artifacts as authoritative evidence"
4. Run contradiction detection between fods-p6-proof-graph.yaml assertions and Compat/ code behavior
5. Use LLM-assisted candidate test generation for FACT-FODS-002..010 (NOT FACT-FODS-001, already proven)

### Never (hard rule per policy)
- AI output MUST NOT be labeled as verified spec fact without human sign-off
- AI MUST NOT set `spec_fact_ref` values in qname-registry entries without human verification
- AI MUST NOT write to `.local/spec-cache/{format}/workbench/verified-facts.yaml` directly

---

## 6. Verdict

**AI/EMBEDDING STATUS: MOSTLY_ADVISORY**

Policy is sound. AI tools exist but are labeled ai_draft. No embeddings deployed. No RAG pipeline active. Current risk is LOW. Future risk requires V49 governance validator before Phase E AI assist work begins.
