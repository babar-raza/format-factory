# Proof Sufficiency Evaluation

Generated: 2026-06-05T03:39:47.244622+00:00

**Overall verdict:** `COVERAGE_BLOCKED`

| Metric | Value |
|--------|-------|
| total_claims | 20 |
| passed | 15 |
| blocked | 5 |
| partial | 0 |
| requires_policy | 0 |
| coverage_pct | 75.0 |
| overall_verdict | COVERAGE_BLOCKED |

## Per-Claim Results

| Claim | Achieved Level | Min Required | Verdict |
|-------|---------------|-------------|--------|
| claim:dif:inspect | ? | TESTED | PASS |
| claim:dif:parse | ? | TESTED | PASS |
| claim:fods:edit | ? | DOGFOODED | PASS |
| claim:fods:export_csv | ? | TESTED | BLOCKED |
| claim:fods:export_html | ? | TESTED | BLOCKED |
| claim:fods:load | ? | TESTED | PASS |
| claim:fods:save | ? | DOGFOODED | PASS |
| claim:fodt:edit | ? | DOGFOODED | PASS |
| claim:fodt:export_markdown | ? | TESTED | BLOCKED |
| claim:fodt:export_txt | ? | TESTED | BLOCKED |
| claim:fodt:load | ? | TESTED | PASS |
| claim:fodt:save | ? | DOGFOODED | PASS |
| claim:netpbm:edit | ? | DOGFOODED | PASS |
| claim:netpbm:inspect | ? | TESTED | PASS |
| claim:netpbm:load | ? | TESTED | PASS |
| claim:netpbm:save | ? | DOGFOODED | PASS |
| claim:zst:compress | ? | DOGFOODED | PASS |
| claim:zst:decompress | ? | TESTED | PASS |
| claim:zst:old-compress | ? | DOGFOODED | BLOCKED |
| claim:zst:roundtrip | ? | DOGFOODED | PASS |

## Architecture-Blocked Claims

FODS export_csv: BLOCKED (no FormatFactory.Csv target writer)
FODS export_html: BLOCKED (no FormatFactory.Html target writer)
FODT export_markdown: BLOCKED (no FormatFactory.Markdown target writer)
FODT export_txt: BLOCKED (no FormatFactory.Txt target writer)
