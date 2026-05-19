# COMMERCIAL-FODS-FODT-G11-GAP-CLOSURE

**Type:** Commercial track
**Created:** R32 (2026-05-19)
**Formats:** FODS, FODT
**Priority:** High (these are the only .NET formats)

---

## Current State
- **FODS .NET:** C4-C6 vertical slice, 1286 LOC, 160 tests, 3 exporters, round-trip verified
- **FODT .NET:** C4-C6 vertical slice, 1222 LOC, 142 tests, 3 exporters, round-trip verified
- **Gate 11:** g11e_prototype_complete, G11-F in_progress, G11-G NOT_STARTED
- **commercial_product_ready:** false (both)

## Gap to G11-G Approval

### Model Richness (Tier 0-1 -> Tier 3+)
**FODS gaps:**
- Cell formatting (bold, color, alignment)
- Formula storage (not evaluation)
- Merged regions (table:number-columns-spanned)
- Column/row sizing
- Multiple value types beyond string

**FODT gaps:**
- Inline formatting (bold, italic, underline, hyperlinks)
- List hierarchy (nested numbered/bulleted lists)
- Table content extraction and editing
- Section/frame/annotation support

### Security Gaps
- Missing: MaxCharactersFromEntities guard (documented in _readme.md)
- Missing: Formula injection guard for CSV exporter

### Exporter Gaps
- FODS CSV: no multi-sheet support, no number-columns-repeated expansion
- FODT Markdown: special characters not escaped

### G11-G Packet
- Comprehensive feature matrix per docs/format-feature-matrix-template.md
- Security review updated for .NET implementation
- Performance test (parse/save time for representative documents)
- Babar Raza review and approval

## Stop Conditions
- Do not implement formula evaluation
- Do not implement full ODF style inheritance
- Focus on model richness that enables practical document editing

## Evidence Required
- Model tests for new Tier 3+ features
- Updated security review
- Feature matrix filled
- G11-G packet prepared for human review
