# DEEPEN-ODT-PRODUCTION-TRACK

**Type:** Format deepening
**Created:** R32 (2026-05-19)
**Format:** ODT (OpenDocument Text, ZIP)
**Priority:** Medium

---

## Current Evidence-Backed Maturity
- **Class:** read_only_prototype
- **Source:** src/python/odt/odt_parser.py (250 LOC)
- **Tests:** 66 methods
- **Gate:** G8
- **Model:** dataclass (OdtDocument) — paragraphs, headings, list items but shallow nesting

## Next Target Maturity
**read_only_library_foundation** (formalize model, deepen content extraction)

## Feature Gaps
1. Content extraction is shallow (no list nesting depth, no table content)
2. No write capability
3. No export
4. Neutral model not formalized
5. No packaging

## Source Gaps
- Missing: deeper content model (nested lists, tables), neutral_model.py, writer, exporter

## Tests Required
- Nested list tests, table content tests
- Target: 80+ tests after deepening

## Stop Conditions
- Do not implement inline formatting in first deepening sprint
- Focus on content structure before styling

## Evidence Required
- Enriched model covers lists, tables, headings with depth
- At least 20 new tests for deepened features
