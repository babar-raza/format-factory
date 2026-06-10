# Regression Test Plan — Future Additions

Sprint: FORMAT-FACTORY-DOTNET-DOGFOOD-ARCHITECTURE-GAP-INVESTIGATION-AND-PLANNING-001
Date: 2026-06-05

## Purpose

This document lists regression tests to add in a later sprint to harden the architecture gap
classification and prevent gap promotion bypass.

## Planned Future Tests

### FT-1: select_poc_gaps.py returns ARCHITECTURE_BLOCKED for all 4 gap IDs

Verify that when `tools/supervisor/select_poc_gaps.py` is invoked, the 4 blocked gap IDs
(`commercial-net-fods-dogfood-status-fods-to-csv-dotnet`,
`commercial-net-fods-dogfood-status-fods-to-html-dotnet`,
`commercial-net-fodt-dogfood-status-fodt-to-markdown-dotnet`,
`commercial-net-fodt-dogfood-status-fodt-to-txt-dotnet`)
are all returned with status `ARCHITECTURE_BLOCKED` and are not included in the
actionable selection output.

### FT-2: generate_next_worker_prompt.py skips blocked gaps in dogfood task generation

Verify that `tools/supervisor/generate_next_worker_prompt.py` does not emit any dogfood task
for the 4 blocked gap IDs. The generated prompt must not contain `/add-dogfood-export` invocations
referencing these gap IDs until their blocker (`missing_target_writer_library`) is resolved.

### FT-3: Running select_poc_gaps.py fresh does not promote blocked gaps above safe alternatives

Verify that a fresh run of `select_poc_gaps.py` against the current poc-targets.yaml does not
rank any of the 4 blocked gaps above unblocked alternatives (e.g.,
`foss-reduced-sylk-python-status-installed-workflow` at score 110) in the output selection list.
This prevents score inflation from causing a blocked gap to be selected for execution.

### FT-4: No evidence declaration can mark these 4 gaps as dogfood_status IMPLEMENTED without FF writer proof

Verify that the evidence validator (`tools/supervisor/validate_evidence_for_supervisor.py` or
equivalent) rejects any evidence declaration that sets `dogfood_status: IMPLEMENTED` for any of
the 4 blocked gap IDs unless the corresponding FF target writer library package is present in
`src/net/` with a verifiable namespace (e.g., `FormatFactory.Csv`, `FormatFactory.Html`,
`FormatFactory.Markdown`, `FormatFactory.Txt`).

## Notes

- FT-1 and FT-2 require `select_poc_gaps.py` and `generate_next_worker_prompt.py` to surface
  ARCHITECTURE_BLOCKED state explicitly; this may require a schema extension to those tools.
- FT-3 is a determinism test — run twice and compare outputs.
- FT-4 requires the evidence validator to cross-reference `target-writer-library-matrix.json`
  at declaration validation time.
- All four future tests should be added to `tests/supervisor/test_validate_dotnet_dogfood_architecture.py`
  as additional test functions in the same file.
