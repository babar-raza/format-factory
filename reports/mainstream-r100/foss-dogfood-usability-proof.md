# R100 Train I: FOSS Dogfood/Usability Proof

Sprint: FORMAT-FACTORY-MAINSTREAM-R100-PRODUCT-POC-DEEP-COMMERCIAL-FOSS-DOGFOOD-PARALLEL-MEGA-TRAIN-001
Date: 2026-06-03

## Purpose

Verify that R100 FOSS capabilities (ZST probe workflow, Netpbm PBM/PPM/PGM chain, SYLK CSV/malformed hardening) use FF libraries exclusively.

## Dogfood Verification Matrix

| Capability | Format | Backend | External Deps | Status |
|-----------|--------|---------|---------------|--------|
| compress/decompress/validate | ZST | zst_codec (FF) | zstandard (declared) | PASS |
| PBM->PPM->PGM chain | Netpbm | write_pbm/write_ppm/write_pgm (FF) | None | PASS |
| SYLK->CSV export | SYLK | sylk_to_csv (FF) | None | PASS |
| SYLK write/read roundtrip | SYLK | write_sylk/parse_sylk_strict (FF) | None | PASS |
| probe_sylk malformed input | SYLK | probe_sylk (FF) | None | PASS |

## Evidence

### ZST Probe Workflow (10 tests)
- File: `tests/python/zst/test_r100_zst_probe_workflow.py`
- validate_file for valid/nonexistent/corrupt files
- ZSTD_MAGIC constant verification
- Binary data roundtrip, empty input, deterministic compression
- All tests use `zst.zst_codec` (FF library); zstandard is a declared dependency

### Netpbm PBM/PPM/PGM Chain (8 tests)
- File: `tests/python/ppm/test_r100_pbm_ppm_pgm_chain.py`
- Full chain: PBM -> PPM -> PGM with pixel mapping verification
- PGM -> PPM expansion, all-black/all-white chains
- Dimension preservation across all formats
- All conversions use FF writers (write_pbm, write_ppm, write_pgm)

### SYLK CSV/Malformed Hardening (9 tests)
- File: `tests/python/sylk/test_r100_sylk_csv_malformed.py`
- CSV export: commas in values, empty cells, multirow, large grid (10x10)
- Malformed input: random bytes, empty file, minimal valid header
- Special character roundtrip
- All tests use `sylk.sylk_parser` (FF library)

## Usability Improvements in R100

1. ZST: validate_file now exercised with 3 input classes (valid/missing/corrupt)
2. Netpbm: Full PBM->PPM->PGM pipeline proven end-to-end
3. SYLK: CSV export hardened for commas, empty cells, multirow

## TRAIN_I_STATUS: COMPLETE
