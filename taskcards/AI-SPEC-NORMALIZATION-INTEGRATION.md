# Taskcard: AI-SPEC-NORMALIZATION-INTEGRATION

## Objective
Integrate spec normalization with the AI platform so that all AI and embedding consumers receive normalized artifacts with full provenance, not raw untracked spec files.

## Status
`implemented_fixture_mode` — adapter.py with NormalizedChunk, provenance tracking, chunk loader, and fail-closed NormalizationNotAvailable implemented in R27 (cb7e05c). 8 tests pass.

## Prerequisites
- Spec normalization layer operational (`docs/python-foss/specification-normalization.md`)
- At least one format has normalized spec artifacts (FODS has partial normalization)

## Allowed Scope
- Define normalization output schema for AI consumption
- Create chunk generation pipeline from normalized artifacts
- Define provenance record schema (source hash, extraction method, normalization version)
- Integrate chunk output with embedding pipeline input
- Create tests in `tests/ai/test_normalization_integration.py`

## Forbidden Scope
- No changes to existing normalization tools (unless extending for AI output)
- No raw PDF/spec processing bypassing normalization
- No product source changes

## Gates
1. Normalization output schema defined and validated
2. Chunk generation produces manifested chunks with hashes
3. Provenance records link chunks to source specs
4. Embedding pipeline accepts only normalized chunks
5. Raw spec bypass detected and rejected

## Evidence Requirements
- Chunk manifest sample for one format
- Provenance record samples
- Bypass detection test results

## Validation Requirements
- Tests pass
- No raw spec inputs accepted by AI pipeline

## Closeout Criteria
- Normalization → chunking → embedding pipeline operational for one format
- Provenance chain complete from source spec to chunk

## Next Transition
On closeout: AI-EMBEDDING-VECTOR-STORE-FOUNDATION can index normalized chunks.
