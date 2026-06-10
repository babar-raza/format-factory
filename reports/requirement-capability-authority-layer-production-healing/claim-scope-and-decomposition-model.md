# Claim Scope and Decomposition Model

Sprint ID: FORMAT-FACTORY-REQUIREMENT-CAPABILITY-AUTHORITY-LAYER-PRODUCTION-BLOCKER-HEALING-001
Owner: Lane B

## Claim Dimensions (12)

Every CapabilityClaim is described by 12 dimensions:

1. **product_id** — Which product implements this capability (e.g., fods, fodt, netpbm-net, zst)
2. **format_id** — Which file format is targeted (e.g., fods, fodt, ppm, sylk, dif)
3. **operation** — What operation is performed (see operation values below)
4. **direction** — The data flow direction (see direction values below)
5. **fidelity** — How faithfully the data is preserved (see fidelity values below)
6. **variant** — Which format variant is supported (e.g., P3/P6 for PPM, ODF 1.3, SYLK 1.0)
7. **object_model_scope** — Which portion of the object model is covered (e.g., cells_only, paragraphs_only, full_model)
8. **io_scope** — File I/O scope: in_memory_only, stream_only, file_path, any
9. **error_scope** — Which error cases are handled: none, basic_validation, strict_schema, full_error_recovery
10. **performance_scope** — Performance constraints claimed: none, small_files_only, large_file_capable, streaming
11. **platform_scope** — Platform constraints: any, windows_only, linux_only, net_only, python_only
12. **POC_scope** — Whether this claim is required for POC: required | stretch | not_applicable

## Operation Values (12)

- load — Load a file into memory from a path or stream
- parse — Parse the loaded bytes into an object model
- inspect — Read fields from the parsed object model without modifying
- edit — Modify the object model in memory
- save — Write the object model back to the same format and same file
- write — Write the object model to a new file (same format)
- export — Write the object model to a different format
- import — Read from a different format into this format's object model
- roundtrip — Load → edit → save with verified fidelity
- validate — Check that a file conforms to format constraints
- package — Bundle artifacts into a distributable package
- dogfood — End-to-end production use of the format capability with output verification

## Direction Values (6)

- read_only — Input only; no write capability claimed
- write_only — Output only; no read capability claimed
- read_write — Both read and write to the same format
- export_only — Read this format, write to a different format
- import_only — Read a different format, write to this format
- transform — Read and modify within the same format (subset of read_write with edit)

## Fidelity Values (8)

- structure_only — Only structural elements are preserved (e.g., sheet names, paragraph count)
- content_only — Only text/data content is preserved; formatting is dropped
- metadata_only — Only metadata fields are preserved
- formatting_partial — Some formatting is preserved; known gaps exist
- formatting_preserved — All formatting elements are preserved
- lossless — Perfect round-trip fidelity; no information loss
- lossy — Known information loss; acceptable for stated use case
- declared_limited — Fidelity is limited by declared UnsupportedFeature records; visible downstream

## Decomposition Rules (8)

**Rule 1:** Claim operation=full_support with proof of parse-only implementation → Split:
  - PARSE claim: accepted (tested_by linked TestArtifact)
  - SAVE claim: blocked_missing_implementation (no write-path artifact linked)

**Rule 2:** Claim operation=save with proof of export-only (different-format output) → Downgrade to EXPORT:
  - Original SAVE claim: rejected
  - New EXPORT claim: created with operation=export, direction=export_only

**Rule 3:** Claim operation=roundtrip with proof of load+export only (no same-format save) → Reject roundtrip; create LOAD_EXPORT claim:
  - ROUNDTRIP claim: rejected_downgraded
  - New LOAD_EXPORT claim: operation=export, direction=export_only, fidelity=declared_limited

**Rule 4:** Claim variant=all_variants with TestArtifacts covering only one variant → Split into variant-specific claims:
  - claim_P3: accepted (tested variant=P3 only)
  - claim_P6: blocked_missing_test (no TestArtifact for P6 linked)

**Rule 5:** Claim operation=dogfood with helpers/CLI tools only (no format output produced) → Block readiness:
  - dogfood_present stays false
  - Claim status: blocked_missing_dogfood
  - Required action: add DogfoodArtifact with actual format file output and checksum

**Rule 6:** DogfoodArtifact exists on disk but not linked to the claim in the graph → Keep dogfood_present=false:
  - Claim: dogfood_present=false, coverage_validated=false
  - Corrective action: EvidenceGraphImporter must link artifact to claim before dogfood_present transitions

**Rule 7:** TestArtifacts exist (tests pass) but no graph edge links them to the capability claim → Coverage remains unvalidated:
  - Claim: tests_present=false in graph (tests exist in test dir but not linked)
  - Corrective action: add tested_by edge from claim to TestArtifact nodes

**Rule 8:** Blocking UnsupportedFeature contradicts the core required capability → Block claim entirely:
  - Claim: status=blocked
  - If UnsupportedFeature severity=non_blocking: accepted_with_limitations allowed
  - If UnsupportedFeature severity=blocking: claim cannot be accepted_for_poc until feature is implemented

## Product-Specific Decomposition Examples (7)

**FODS:** Claim "supports FODS fully" with only get_cell_value + get_row_values proof →
  Decomposed: inspect claim accepted (operation=inspect, tested_by 15 test functions), save claim blocked_missing_test (no write roundtrip TestArtifact linked).

**FODT:** Claim "supports FODT roundtrip" with only get_paragraph_text + append_paragraph proof →
  Decomposed: Rule 3 applies. ROUNDTRIP rejected. New claim: operation=edit_partial, fidelity=declared_limited (paragraph ordering preserved, formatting partial). No roundtrip claim accepted until write_fodt + reload produces identical paragraph structure.

**Netpbm:** Claim "supports all PPM variants" with TestArtifacts covering only P3 ASCII →
  Decomposed: Rule 4 applies. claim_P3: accepted. claim_P6: blocked_missing_test. claim_binary_P6 created, requires TestArtifact with P6 format proof.

**ZST:** Claim "supports ZST roundtrip" with compress+decompress proof but no same-process validation →
  Decomposed: Rule 3 applies. ROUNDTRIP: rejected. New LOAD_EXPORT claim: LOAD_EXPORT accepted (direction=export_only). Roundtrip blocked until decompressed output is validated as byte-identical to input.

**Python Netpbm:** Claim "supports PPM write" with write_ppm producing P3 ASCII only →
  Decomposed: Rule 4. claim_P3_write: accepted. claim_P6_write: blocked_missing_implementation. variant scope narrowed from all_variants to P3_only.

**SYLK:** Claim "supports SYLK CSV export" with sylk_to_csv proof but no multi-sheet SYLK test →
  Decomposed: Rule 1 variant. single_sheet_export: accepted. multi_sheet_export: blocked_missing_test. Claim variant=single_sheet accepted; variant=multi_sheet split out as separate blocked claim.

**DIF:** Claim "supports DIF as SYLK substitute" with parse proof only, no write →
  Decomposed: Rule 1. DIF_parse: accepted. DIF_write: blocked_missing_implementation. Substitution claim deferred until both parse and write claims are accepted_for_poc.
