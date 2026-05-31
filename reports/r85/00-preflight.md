# R85 Preflight Report

Sprint: FORMAT-FACTORY-R85-POC-DIRECTION-LOCAL-SUPERVISOR-AUTONOMOUS-PRODUCT-FACTORY-MEGA-TRAIN-001
Date: 2026-05-31

## Repository State (as of preflight)

### Latest sprint
R84 — R84_BROAD_CLOSURE_RAW_LOGS_FINAL_AUTHORITY_PUBLICATION_BLOCKED
Full Python suite: 6634 passed, 19 isolation-only (csv-shadow), 34 skipped
.NET: 306 passed (FODS 161 + FODT 145)

### Source layouts verified
| Component | Path | Status |
|-----------|------|--------|
| Python FODS | src/python/fods/ | 7 files (parser, writer, neutral_model, csv_exporter, constants, exceptions, __init__) |
| Python FODT | src/python/fodt/ | 8 files (parser, writer, neutral_model, list_traversal, constants, exceptions, __init__, README) |
| Python PBM | src/python/pbm/ | 2 files (pbm_parser, __init__) — parse+write_pbm exported |
| Python PGM | src/python/pgm/ | 2 files (pgm_parser, __init__) — parse+write_pgm exported |
| Python PPM | src/python/ppm/ | 3 files (ppm_parser, ppm_stats, __init__) — parse only (no writer) |
| Python SYLK | src/python/sylk/ | 2 files (sylk_parser, __init__) — sylk_to_csv exported |
| Python DIF | src/python/dif/ | 3 files (dif_parser, dif_stats, __init__) — dif_to_csv exported |
| Python ZST | src/python/zst/ | 2 files (zst_codec, __init__) — compress/decompress/probe |
| Python QOI | src/python/qoi/ | 3 files (qoi_parser, qoi_encoder, __init__) — Gate 7 prototype |
| .NET FODS | src/net/fods/ | FodsDocument, FodsParser, FodsWriter, FodsCsvExporter, FodsHtmlExporter, FodsJsonExporter + Model/ |
| .NET FODT | src/net/fodt/ | FodtDocument, FodtParser, FodtWriter, FodtTxtExporter, FodtMarkdownExporter, FodtHtmlExporter + Model/ |

### .NET tests verified
- FODS: 161 passed, 0 failed (confirmed by background task bfvw11gqb/bp24oon9k)
- FODT: 145 passed, 0 failed

### Supervisor control plane
- .supervisor/: config.yaml, policies.yaml, project-memory.md, prompts/, schemas/, state/
- tools/supervisor/supervisor_loop.py: CLI with {discover, review, next, run-on-latest, export-taskmaster, export-ruflo}
- reports/supervisor/: all outputs present (committed)
- No ChatGPT web automation. No paid OpenAI API dependency. No MCP activation needed.

### Known R84 invariant issues (not blocking R85)
- INV-006: reports/r84/r84-pass3-final.sha256-proof.json is git-tracked (should be gitignored)
- INV-014: final-verdict.md SHA field format mismatch (state_snapshot.py regex issue)

### Direction problem identified
Current master-plan/state framing: evidence closure = sprint success.
R85 mission: correct to product-factory POC = sprint success.

## Preflight Verdict

PREFLIGHT_PASS — all required sources verified, supervisor loop operational, product candidates identified.

### Third Commercial Candidate Decision (preflight)
SELECTED: Netpbm family (PBM/PGM/PPM) as third commercial .NET product candidate.
Rationale:
- Three Python libraries already exist (PBM/PGM/PPM all Gate 10 RC)
- .NET load/inspect/save trivially implementable (simple text/binary format)
- Family-based dogfooding: PBM→PGM→PPM export using Format Factory's own libraries
- Lower complexity than QOI (no run-length state machine for .NET first slice)
- QOI remains a HOLD candidate for future commercial consideration

### FOSS Dogfooding Status (preflight)
FODS→CSV: IMPLEMENTED — Python fods/csv_exporter.py (export_fods_to_csv)
FODT→TXT: IMPLEMENTED — Python fods/document_to_text (R84 Train I)
SYLK→CSV: IMPLEMENTED — Python sylk/sylk_to_csv (R84 Train N)
DIF→CSV: IMPLEMENTED — Python dif/dif_to_csv (R84 Train N)
Netpbm PBM→PGM: NOT_IMPLEMENTED (R85 Train M target)
