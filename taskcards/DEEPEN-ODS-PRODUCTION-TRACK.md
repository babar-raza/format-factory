# DEEPEN-ODS-PRODUCTION-TRACK

**Type:** Format deepening
**Created:** R32 (2026-05-19)
**Format:** ODS (OpenDocument Spreadsheet, ZIP)
**Priority:** High — strongest spreadsheet candidate after FODS

---

## Current Evidence-Backed Maturity
- **Class:** read_only_library_foundation
- **Source:** src/python/ods/ods_parser.py (303 LOC)
- **Tests:** 61 methods (parse, typed cells, ZIP guards, neutral model, oracle, fuzz)
- **Gate:** G8 (security review)
- **Model:** dataclass (OdsDocument/OdsSheet/OdsRow/OdsCell) with typed values

## Next Target Maturity
**read_write_library_foundation** (then export_capable_library)

## Feature Gaps
1. No write capability (ODS ZIP construction)
2. No export (CSV, JSON, HTML from ODS)
3. Neutral model uses dataclass but not formalized with schema file
4. No round-trip tests
5. No packaging (pyproject.toml, __version__)

## Source Gaps
- Missing: ods_writer.py, neutral_model.py (formalized), exceptions.py
- Missing: export classes

## Tests Required
- Write tests: create ODS from model, verify ZIP structure
- Round-trip: parse -> model -> write -> parse -> compare
- Export: ODS -> CSV, ODS -> JSON at minimum
- Target: 80+ tests

## Package Requirements
- pyproject.toml for format-factory-ods
- __init__.py with __version__, __track__, public API

## Stop Conditions
- Do not attempt ODS write without understanding ZIP/content.xml structure from spec
- Do not implement formula evaluation
- Do not implement styling/formatting in first deepening sprint

## Evidence Required
- Write tests pass
- Round-trip tests pass
- At least 1 export test passes
- Package builds locally
