# R109 Lane I: Evidence Package Hardening

## Raw Logs Packaged
| Log File | Content | Size |
|----------|---------|------|
| raw-logs/fods-dotnet-test.log | 421 tests passed | Full test output |
| raw-logs/fodt-dotnet-test.log | 409 tests passed | Full test output |
| raw-logs/netpbm-dotnet-test.log | 335 tests passed | Full test output |
| raw-logs/python-all-test.log | 3104 passed, 29 skipped | Full pytest output |

## Source Diffs Packaged
| Diff File | Content | Lines |
|-----------|---------|-------|
| raw-logs/fods-source-diff.txt | All uncommitted FODS changes | 655 |
| raw-logs/fodt-source-diff.txt | All uncommitted FODT changes | 370 |
| raw-logs/netpbm-source-diff.txt | All uncommitted Netpbm changes | 916 |

## Skill Transcripts Packaged
| Transcript | API | Ledger Entry |
|-----------|-----|-------------|
| skill-transcripts/r109-fods-hassheet.md | HasSheet | R109-GOVERNED-DOTNET-FODS-HASSHEET-001 |
| skill-transcripts/r109-fodt-exporttohtmlfile.md | ExportToHtmlFile | R109-GOVERNED-DOTNET-FODT-EXPORTTOHTMLFILE-001 |
| skill-transcripts/r109-netpbm-posterize.md | Posterize | R109-GOVERNED-DOTNET-NETPBM-POSTERIZE-001 |

## Package Identity
- Stream: **Mainstream** (not Skills, not Acceleration, not Supervisor)
- Run ID: mainstream-r109
- Sprint ID: FORMAT-FACTORY-MAINSTREAM-R109-VERIFIED-PRODUCT-DEPTH-CLEAN-CLOSURE-RAW-PROOF-AND-DOGFOOD-MEGA-TRAIN-001
- No cross-stream references in evidence artifacts

## Work-Item Grade Backing
Each item's evidence_paths contain:
- For governed API items: test file + source file + product depth report + skill transcript + raw log + source diff
- For FOSS items: test file + raw log (python-all-test.log)
- For dogfood items: dogfood test file + raw log
- For report-only items: report file(s)

## Verdict
Evidence package is Mainstream-primary, self-contained, with raw logs and source diffs.
