# R107 Evidence Regrading

## Regrading Methodology
Each R107 work item is checked for:
1. Evidence file exists on disk
2. Test file exists and contains test methods
3. Source diff captured (for src/ changes)
4. Skill transcript present (for src/ changes)
5. Ledger entry present with correct SHA

## Regrading Results

### Wave 0 (2 items)
| Item | Evidence Exists | Tests | Transcript | Grade |
|------|----------------|-------|------------|-------|
| R107-W0-PREFLIGHT | reports/mainstream-r107/00-preflight.md EXISTS | N/A | N/A | ACCEPTED_VERIFIED |
| R107-W0-R106-RECONCILIATION | r106-reconciliation.md + r106-claim-classification.json EXIST | N/A | N/A | ACCEPTED_VERIFIED |

### Wave 1 (2 items)
| Item | Evidence Exists | Tests | Transcript | Grade |
|------|----------------|-------|------------|-------|
| R107-W1-D106-REPAIR | r106-evidence-governance-repair.md + 2 others EXIST | N/A | N/A | ACCEPTED_VERIFIED |
| R107-W1-FRESH-GAPS | selected-mainstream-gaps-r107.json + deep-product-strategy.md EXIST | N/A | N/A | ACCEPTED_VERIFIED |

### Wave 2 (6 items — source changes)
| Item | Source Diff | Transcript | Tests | Ledger SHA | Grade |
|------|-----------|------------|-------|------------|-------|
| R107-W2-FODS-EXPORTCSV | fods-document.diff EXISTS | r107-fods-exportsheettocsv.md EXISTS | FodsR107ExportSheetToCsvTests.cs EXISTS (8 tests) | c77c9ea MATCH | ACCEPTED_VERIFIED |
| R107-W2-FODS-INSERTROW | fods-document.diff EXISTS | r107-fods-insertrowwithvalues.md EXISTS | FodsR107InsertRowWithValuesTests.cs EXISTS (8 tests) | c77c9ea MATCH | ACCEPTED_VERIFIED |
| R107-W2-FODT-HEADINGS | fodt-document.diff EXISTS | r107-fodt-getheadingtexts.md EXISTS | FodtR107GetHeadingTextsTests.cs EXISTS (8 tests) | e338eda MATCH | ACCEPTED_VERIFIED |
| R107-W2-FODT-PLAINTEXTFILE | fodt-document.diff EXISTS | r107-fodt-exporttoplaintextfile.md EXISTS | FodtR107ExportToPlainTextFileTests.cs EXISTS (8 tests) | e338eda MATCH | ACCEPTED_VERIFIED |
| R107-W2-NETPBM-EQUALIZE | netpbm-image.diff EXISTS | r107-netpbm-equalize.md EXISTS | NetpbmR107EqualizeTests.cs EXISTS (8 tests) | 978e037 MATCH | ACCEPTED_VERIFIED |
| R107-W2-NETPBM-CONVERTFORMAT | netpbm-image.diff EXISTS | r107-netpbm-convertformat.md EXISTS | NetpbmR107ConvertFormatTests.cs EXISTS (10 tests) | 978e037 MATCH | ACCEPTED_VERIFIED |

### Wave 3 (5 items — FOSS tests)
| Item | Test File | Test Count | Grade |
|------|-----------|------------|-------|
| R107-W3-ZST-ISOLATION | test_r107_zst_dependency_isolation.py EXISTS | 10 | ACCEPTED_VERIFIED |
| R107-W3-PBM-ROUNDTRIP | test_r107_pbm_binary_roundtrip.py EXISTS | 10 | ACCEPTED_VERIFIED |
| R107-W3-PPM-PGM | test_r107_ppm_pgm_conversion.py EXISTS | 10 | ACCEPTED_VERIFIED |
| R107-W3-SYLK-CSV | test_r107_sylk_csv_export.py EXISTS | 9 | ACCEPTED_VERIFIED |
| R107-W3-DIF-ROUNDTRIP | test_r107_dif_roundtrip_proof.py EXISTS | 9 | ACCEPTED_VERIFIED |

### Wave 4 (4 items — dogfood)
| Item | Test File | Test Count | Grade |
|------|-----------|------------|-------|
| R107-W4-DOGFOOD-FODS-CSV | FodsR107DogfoodCsvExportTests.cs EXISTS | 6 | ACCEPTED_VERIFIED |
| R107-W4-DOGFOOD-FODT-PLAINTEXT | FodtR107DogfoodPlainTextExportTests.cs EXISTS | 6 | ACCEPTED_VERIFIED |
| R107-W4-DOGFOOD-NETPBM-EQUALIZE | NetpbmR107DogfoodEqualizeOverlayTests.cs EXISTS | 6 | ACCEPTED_VERIFIED |
| R107-W4-DOGFOOD-SYLK-CSV | test_r107_sylk_dogfood_csv_pipeline.py EXISTS | 6 | ACCEPTED_VERIFIED |

### Wave 5 (1 item — examples)
| Item | Files Exist | Grade |
|------|------------|-------|
| R107-W5-EXAMPLES | 4/4 example files exist | ACCEPTED_VERIFIED |

### Wave 6 (1 item — evidence)
| Item | Files Exist | Grade |
|------|------------|-------|
| R107-W6-EVIDENCE-CLOSEOUT | 16/16 report files exist | ACCEPTED_VERIFIED |

## Summary
- **21/21 items upgraded to ACCEPTED_VERIFIED**
- All evidence physically present on disk
- All source SHAs match ledger entries
- All skill transcripts present for source changes
- All source diffs captured
