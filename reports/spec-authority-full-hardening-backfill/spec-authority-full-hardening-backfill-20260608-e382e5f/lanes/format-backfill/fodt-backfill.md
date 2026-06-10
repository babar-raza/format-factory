# FODT Backfill — P0 → P2
Sprint: FORMAT-FACTORY-SPEC-AUTHORITY-FULL-HARDENING-BACKFILL-AND-PILOT-MEGA-TRAIN-001

## Action Taken
Created `.local/spec-cache/fodt/odf-1.3/spec-index.yaml` referencing ODF 1.3 spec.
Spec text is the same PDF already cached under `.local/spec-cache/fods/1.3/`.
SHA-256: sha256:92cfe64ee30a8cca1be19a76d38628fdc8ef9153eb59547f6c96fe7b9b81b066

## Rationale
ODF 1.3 governs both FODS (Flat ODS) and FODT (Flat ODT). The distinction is the
`office:mimetype` value:
- FODS: `application/vnd.oasis.opendocument.spreadsheet`
- FODT: `application/vnd.oasis.opendocument.text`

Since the spec PDF is the same, the spec is already cached. Creating a spec-index.yaml
under `fodt/` allows `authority_gate_validation.py` to detect `spec_cached=True`.

## Result
FODT: P0 → P2 (spec_cached=True, 0 verified facts → P2)

## Candidate Fact Created
FACT-FODT-001-CANDIDATE: "FODT root element is <office:document> with office:mimetype='application/vnd.oasis.opendocument.text'"
Status: needs_review (requires deterministic text search)

## Next Step to P3
Run deterministic text search on ODF 1.3 PDF for "application/vnd.oasis.opendocument.text"
and "office:document" to verify FACT-FODT-001-CANDIDATE.
