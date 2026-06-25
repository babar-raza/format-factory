# AI Embeddings Audit
**Mission:** spec-auth-inv-20260625-001
**Date:** 2026-06-25

## Embedding Infrastructure Status

### Current State
- **Embedding storage:** None (no vector store configured)
- **Semantic search:** Not implemented
- **Spec chunk indexing:** Not implemented
- **LLM grader:** Configured via env vars `GPT_OSS_ENDPOINT` + `GPT_OSS_API_KEY` (optional)

### What Would Embeddings Enable
1. **Semantic gap discovery:** "Which spec sections are not covered by any capability?"
2. **Cross-format fact linking:** "Are these two facts semantically equivalent across formats?"
3. **Evidence verification:** "Does this code pattern implement the spec section it claims?"

### Gap: No Chunk-Level Provenance
Evidence schema has no `chunk_id`, `section_ref`, or `page_ref` fields.
Without these, AI graders cannot verify that implementation evidence maps to specific spec sections.

### Recommendation
1. Add optional `chunk_id`, `section_ref`, `page_ref` to evidence_artifacts schema (RC-004)
2. Implement spec chunk extractor alongside SAL parsers
3. Consider embedding-based gap discovery as Phase 2 capability

### Current LLM Grader Status
- Available: `grade_intermediate_verify.py` (Level 2 fallback)
- Semantic quality score (SQS): requires external endpoint — defaults to 0.0 if unavailable
- Evidence quality score (EQS): deterministic fallback when LLM unavailable
- `evidence_quality_zero` warning: non-blocking (goes to continuation_warnings, not hard_stops)
