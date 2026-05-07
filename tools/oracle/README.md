---
artifact_id: fods-oracle-tooling-readme
artifact_type: documentation
path: tools/oracle/README.md
format_id: fods
visibility: internal
publish_allowed: false
generated_by: claude
generated_at: "2026-05-07"
notes: "Gate 6 oracle tooling README. Created run035 (2026-05-07). LibreOffice harness."
---

# FODS Oracle Tooling — tools/oracle/

## Purpose

Gate 6 oracle comparison tooling for FODS. Compares prototype parser output (via the neutral model) against LibreOffice headless reference exports to validate correctness.

## Status (run035)

**BLOCKED — LibreOffice not installed.**

Oracle preflight failed: `soffice` and `libreoffice` commands not found on PATH or standard Windows install paths.

To unblock: install LibreOffice from https://www.libreoffice.org/download/libreoffice-still/ then re-run `python tools/oracle/preflight_oracle.py`.

## Tools

| File | Purpose |
|---|---|
| `preflight_oracle.py` | Checks oracle tool availability and records version |
| `run_fods_oracle.py` | Runs LibreOffice headless to export each FODS sample to CSV |
| `compare_fods_oracle.py` | Compares prototype output with oracle CSV export cell-by-cell |
| `summarize_oracle_results.py` | Produces sanitized YAML/JSON comparison summary |

## Workflow

1. Run preflight: `python tools/oracle/preflight_oracle.py`
2. If preflight passes, run oracle exports: `python tools/oracle/run_fods_oracle.py`
3. Run comparison: `python tools/oracle/compare_fods_oracle.py`
4. Summarize results: `python tools/oracle/summarize_oracle_results.py`
5. Review report at `acquisition-packs/fods/gate6-oracle-comparison-report.md`

## Inputs

- `samples/by-format/fods/*.fods` — 4 synthetic Gate 3 samples
- `prototypes/by-format/fods/fods_parser.py` — Gate 4 prototype parser
- `schemas/neutral-model/fods/` — Gate 5 neutral model

## Outputs

### Local-only (gitignored, under .local/oracle/fods/)
- `oracle-manifest.yaml` — oracle run metadata
- `per-sample-results/*.json` — per-sample comparison results
- `raw-exports/` — LibreOffice CSV exports
- `comparison-summary.json` — summary of all comparisons

### Committed sanitized summaries
- `acquisition-packs/fods/gate6-oracle-comparison-report.md` — human-readable report
- (updated) `acquisition-packs/fods/oracle-scope.md`
- (updated) `acquisition-packs/fods/oracle-risk-register.md`

## Rules

- No network calls
- No LLM calls
- No product source code
- Raw oracle outputs stay local-only (.local/oracle/fods/ — gitignored)
- Only sanitized summaries are committed
- Only the 4 synthetic Gate 3 samples are used
- Gate 6 approval is human-only (never agent self-approval)
