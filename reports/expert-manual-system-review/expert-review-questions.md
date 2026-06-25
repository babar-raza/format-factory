# Expert Review Questions
# These questions guide the deep investigation in Phase A

## Product Questions

### .NET Commercial Products

1. FODS — FodsOdsExporter has "PROTOTYPE STATUS" in source comments but PASS in poc-targets. Is the ODS exporter actually functional? Do the test outputs verify the ZIP structure is valid?
2. FODS — FodsPdfExporter is Latin-1 only. Does any test verify that non-ASCII content (e.g. é, ü, 中) fails gracefully or is the behavior undefined?
3. FODT — FodtBody.Paragraphs explicitly excludes tables/lists. The Spec/Table/ folder has TableCell.cs, TableRow.cs. Are these exposed anywhere in the public API?
4. NetPBM — 56 test files but no dogfood export. Is NetPBM a standalone library (image manipulation) or is it missing an export story?
5. ZST .NET — ZstParser is explicitly probe-only. Is there any path in the codebase that decompresses ZST content? Does any test verify content extraction?
6. CSV .NET — CsvDocument has no AddRow or SetCell methods in the source. Can a developer use this library to build a CSV programmatically, or only parse?
7. HTML/Markdown/TXT — These are only target writers. Are they listed as format products in poc-targets.yaml? Do they inflate the format count unfairly?

### Python FOSS Products

8. FODP — export_to_txt/csv/json exists but there is no write_fodp. Is FODP useful for a developer who wants to create or modify a presentation? What is the actual use case?
9. ODS — ods_writer.py exists. Does write_ods() produce a file that LibreOffice can open? Are there roundtrip tests?
10. PPM/PBM/PGM — No writers exist. Is this acceptable for an image format FOSS library? What is the user story for a developer using these?
11. XCF — xcf_parser.py is 1272 LOC. How much of that is actually needed for core parsing vs. analytics functions?
12. ZST Python — zst_codec.py is 1549 LOC. How much is compress/decompress core vs. analytics? Is the analytics-to-core ratio appropriate?
13. GNUMERIC — load() returns a dict, not a typed model directly. GnumericDocument wraps it. Is this two-layer approach clear to a FOSS user?
14. SYLK — set_cell_value is file-based (takes src+dest paths, not a document object). Is this design intentional given SYLK's flat format?

## System Questions

15. Gap Ledger — 1131/1132 gaps have "unknown" category. Which pipeline step is supposed to populate the category field? Is gap_ledger_to_work_items.py the root cause?
16. SAL chain — 10 formats have CHAIN_BROKEN_AT_SAL. What would it take to build a SAL extractor for CSV or TOML specs? Are there spec documents accessible?
17. LLM grader — When GPT_OSS_ENDPOINT is unavailable, spec-parity items get DEFERRED_WITH_REASON. How many current sprint items would be affected? Is this degradation transparent to users?
18. autonomous_cycle.py — 2406 LOC (known_violation). The file enforces LOC caps on source files. Does any validator check that autonomous_cycle.py itself respects caps?
19. Skill transcripts — skill_invocation_transcript_required=true in global_controls but ci_transcript_verification is backlog. How are skill transcripts actually verified today?
20. Evidence quality — evidence_quality_zero is a warning-only. Has any sprint ever produced evidence quality zero? What happened?

## Architecture Questions

21. spec/ vs Compat/ — The spec/ folder contains "canonical spec-shaped model classes" and Compat/ contains facades. For FODS, the Compat/ facades (FodsCell, FodsSheet) inherit from spec/ architecture stubs. Are the spec/ stubs genuinely useful or just structural markers?
22. Product count — Format Factory claims 25+ formats. How many of these are genuinely usable libraries vs. thin parsers, target writers, or inspection-only tools?
23. Dogfood strategy — FODS exports to FormatFactory.Csv.CsvWriter (dogfood). ZST .NET has no export. NetPBM has no export. Is the dogfood strategy consistently applied?
24. .NET vs Python asymmetry — Some formats have only Python (ABW, DIF, GNUMERIC, ODS, ODT, QOI, SYLK, XCF) and some have only .NET (HTML, Markdown, TXT). Is this asymmetry governed by a deliberate decision or by sprint opportunism?

## Process Questions

25. poc-targets.yaml PASS claims — How are PASS statuses verified? Is there a review step that checks PASS against actual test output, or is PASS self-declared in the sprint?
26. Sprint selection — How are next sprints selected? Does the next-sprint.md genuinely reflect the highest priority gaps, or does it reflect whatever the autonomous cycle found convenient?
27. Plan precedence — When a plan is not active, the autonomous loop follows next-sprint.md. Does next-sprint.md ever select work that contradicts what an expert would prioritize?
