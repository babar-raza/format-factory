# Lane E: Spec Normalization Adapter

## Implementation
Created `tools/ai/normalization/adapter.py` with:
1. `NormalizedChunk` dataclass — format_id, source_path, source_hash, section, page, extraction_method, normalization_version, chunk_hash, content
2. `discover_normalized_artifacts()` — searches generated-requirements/ and acquisition-packs/normalized/
3. `load_chunks_from_jsonl()` — loads chunks from JSONL files
4. `load_normalized_chunks()` — main entry point, raises NormalizationNotAvailable if absent
5. `validate_chunk_freshness()` — compares source_hash against current hash

## Tests (8)
- test_valid_provenance, test_missing_format_id, test_missing_source_hash, test_missing_extraction_method
- test_load_from_jsonl, test_empty_jsonl
- test_no_artifacts_raises (fail-closed), test_discover_empty_dir
- test_fresh_chunk, test_stale_chunk

## Fail-Closed Behavior
- NormalizationNotAvailable raised when no artifacts exist — not an exception dump
- Clear status message identifying what's missing

## Lane E Status: CLOSED_VERIFIED
