---
memory_id: "57"
sprint: FORMAT-FACTORY-R49-EDITABLE-OBJECT-MODEL-POC-BASELINE-AND-STRATEGY-SYNC-001
date: 2026-05-22
category: product-strategy
visibility: internal
---

# 57 — R49: Object-Model Edit/Save, Export Strategy, AI Acceleration

## Babar's Clarified Product Direction (R49)

This is the authoritative strategy memory for the Format Factory product direction as
clarified by Babar Raza. Future agents MUST read this before executing sprints.

### POC Definition (what "POC proven" means)

A format is NOT POC-proven by artifact existence alone. A format is POC-proven when:
1. **Load** — file can be parsed and neutral model extracted
2. **Object Model** — meaningful objects are accessible (sheets/cells for spreadsheets,
   blocks/paragraphs/headings for documents)
3. **Edit** — a meaningful object can be modified through the API
4. **Save same format** — edited document can be saved back to the same format
5. **Reload** — saved file can be re-parsed successfully
6. **Verify edit** — the edited object reflects the change in the reloaded document
7. **Verify preservation** — unedited objects are unchanged in the reloaded document

This must be proven from the INSTALLED WHEEL, not from source.

### Object Model Requirements

**Spreadsheet formats (FODS, ODS, etc.):**
- Sheet by name/index
- Cell by row+column index
- Cell value (typed: float, boolean, string)
- Cell formula (read at minimum; write where feasible)
- Cell style/alignment (taskcard if unsupported)
- Preservation of untouched cells/rows/sheets

**Document formats (FODT, ODT, etc.):**
- Paragraph blocks (text:p)
- Heading blocks (text:h with level)
- Inline runs/spans (taskcard if unsupported)
- Table blocks (taskcard if unsupported)
- List blocks (taskcard if unsupported)
- Preservation of unedited blocks

### Same-Format Save Strategy

- Save MUST produce a valid file of the same format
- DOM-backed save (like .NET FodsDocument) preserves unrecognized nodes by design
- Streaming write (like Python writer.py) must reconstruct full structure from neutral model
- Unedited cells/blocks must round-trip with same value_type and value
- Lossy fields (formulas not re-serialized in Python writer) MUST be documented as gaps

### Export Strategy (dogfooding)

- Export formats (PDF, HTML, CSV, TXT, Markdown, JSON) are acquired as first-class formats
- Export format writers use Format Factory's own libraries internally where possible
- CSV/TXT/Markdown/JSON: short-win targets (simple text/structured serialization)
- HTML: medium target (requires element mapping)
- PDF: long train target (complex; external library or from-scratch write)
- Existing FODS→CSV, FODT→TXT exporters count as proto-dogfooding
- Full dogfooding: FODT saved as FODT, then exported to HTML via Format Factory HTML writer

### AI Acceleration (non-authoritative)

- AI may: draft object-model gap matrices, propose tests, suggest schema designs,
  produce phase-audit checklists, retrieve specification excerpts
- AI may NOT: approve gates, claim authority, skip evidence, expose secrets
- Every AI call MUST be logged in `reports/<RUN>/ai-usage-ledger.jsonl`
- Agent Metrics posting MUST be attempted; if environment-blocked, state explicitly
- AI drafts have status `ai_draft` until deterministically verified
- Accepted drafts become taskcards only after human/deterministic IV

### Phase Audit Progression

Phase audits run sprint-by-sprint:
- Phase 1 (R46): Specification Ingestion — COMPLETE_ALL_FORMATS_PASS
- Phase 2 (R48): Sample Acquisition/Provenance — COMPLETE_ALL_FORMATS_PASS (20 formats)
- Phase 3 (R48 pilot, R49 expand): Parser Requirements Prototype — FODS/FODT PASS; ZST/ODS/ODT R49
- Phase 4 (future): Oracle Comparison and Fuzz — not started
- Phase 5-7 (future): deeper quality, style, gate reviews

## Key R49 Changes

### FODT Writer Fix (critical)
- Before: `document.get("paragraphs", [])` — returned `[]` when parser output used `blocks`
- After: `document.get("blocks") or document.get("paragraphs", [])` — accepts both
- Heading blocks (`type="heading"`) now serialize to `text:h` with `text:outline-level`
- Backward compatible: `paragraphs` key still works

### Validator Enhancement (R49 Lane 1B)
- `check_proof_file_finality()` added to `validate_evidence_bundle.py`
- Detects stale placeholders: `(updated after`, `to be recorded`, `IN PROGRESS`, etc.
- Called when `--check-no-pending` flag is active
- Prevents R48-style caveat (stale placeholder captured in bundle)

### Python POC Tests Added
- `test_r49_object_model_poc.py` (FODS): 13 tests — edit/save/reload/preservation
- `test_r49_object_model_poc.py` (FODT): 12 tests — writer fix + edit/save/reload/preservation
- 25 total new tests; 383 FODS+FODT tests pass (was 358 in R48)

## Governance (unchanged)

- commercial_product_ready: false for all formats
- Gate 11 G11-G awaits Babar approval
- Gate 8 packets awaiting human review
- DEC-033: .NET commercial only

## Sprint History Links

- R48: `reports/r48/final-verdict.md` — BUNDLE_VALIDATION: PASS; FODT writer mismatch gap
- R49: `reports/r49/final-verdict.md` — FODT writer fixed; POC tests proven; Phase Audit 3 expanded
