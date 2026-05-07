---
artifact_id: fods-oracle-tooling-readme
artifact_type: documentation
path: tools/oracle/README.md
format_id: fods
visibility: internal
publish_allowed: false
generated_by: claude
generated_at: "2026-05-07"
notes: "Gate 6 oracle tooling README. Created run035. Hardened run036 (oracle_common.py, env var support, path reconciliation)."
---

# FODS Oracle Tooling — tools/oracle/

## Purpose

Gate 6 oracle comparison tooling for FODS. Compares prototype parser output (via the neutral model) against LibreOffice headless reference exports to validate correctness.

## Status (run036)

**BLOCKED — LibreOffice not installed.**

Oracle preflight failed: `soffice` and `libreoffice` commands not found on PATH or standard Windows install paths. The `FORMAT_FACTORY_SOFFICE` environment variable is also unset.

To unblock:
1. Install LibreOffice from https://www.libreoffice.org/download/libreoffice-still/
2. Optionally set `FORMAT_FACTORY_SOFFICE=C:\Program Files\LibreOffice\program\soffice.exe`
3. Re-run `python tools/oracle/preflight_oracle.py`
4. Issue explicit TC-0026 execution prompt when preflight passes.

## Tools

| File | Purpose |
|---|---|
| `oracle_common.py` | Shared constants, path model, and LibreOffice discovery (import by other tools) |
| `preflight_oracle.py` | Checks oracle tool availability and records version |
| `run_fods_oracle.py` | Runs LibreOffice headless to export each FODS sample to CSV |
| `compare_fods_oracle.py` | Compares prototype output with oracle CSV export cell-by-cell |
| `summarize_oracle_results.py` | Produces sanitized YAML/JSON comparison summary |

## LibreOffice Discovery Priority

All tools use `oracle_common.find_soffice()` with this priority order:
1. `--soffice-path` CLI argument (if provided)
2. `FORMAT_FACTORY_SOFFICE` environment variable
3. `soffice` on PATH
4. `libreoffice` on PATH
5. `C:\Program Files\LibreOffice\program\soffice.exe`
6. `C:\Program Files (x86)\LibreOffice\program\soffice.exe`
7. `/usr/bin/soffice`, `/usr/bin/libreoffice`
8. `/usr/lib/libreoffice/program/soffice`
9. `/Applications/LibreOffice.app/Contents/MacOS/soffice`

## Workflow

1. Run preflight: `python tools/oracle/preflight_oracle.py [--soffice-path PATH]`
2. If preflight passes, run oracle exports: `python tools/oracle/run_fods_oracle.py [--soffice-path PATH]`
3. Run comparison: `python tools/oracle/compare_fods_oracle.py`
4. Summarize results: `python tools/oracle/summarize_oracle_results.py`
5. Review report at `acquisition-packs/fods/gate6-oracle-comparison-report.md`

## Canonical Path Model

| Path | Location | Committed? |
|---|---|---|
| Raw oracle exports | `.local/oracle/fods/raw-exports/` | NO — local-only |
| Per-sample results | `.local/oracle/fods/per-sample-results/` | NO — local-only |
| Oracle manifest | `.local/oracle/fods/oracle-manifest.yaml` | NO — local-only |
| Preflight result | `.local/oracle/fods/oracle-preflight.yaml` | NO — local-only |
| Comparison summary | `.local/oracle/fods/comparison-summary.json` | NO — local-only |
| Sanitized summary | `.local/oracle/fods/oracle-summary-sanitized.yaml` | NO — local-only |
| Oracle comparison report | `acquisition-packs/fods/gate6-oracle-comparison-report.md` | YES — sanitized only |
| Blocker report (if blocked) | `acquisition-packs/fods/gate6-oracle-blocker-report.md` | YES |

## Inputs

- `samples/by-format/fods/*.fods` — 4 synthetic Gate 3 samples
- `prototypes/by-format/fods/fods_parser.py` — Gate 4 prototype parser
- `schemas/neutral-model/fods/` — Gate 5 neutral model

## Rules

- No network calls
- No LLM calls
- No product source code
- Raw oracle outputs stay local-only (.local/oracle/fods/ — gitignored)
- Only sanitized summaries are committed
- Only the 4 synthetic Gate 3 samples are used
- Gate 6 approval is human-only (never agent self-approval)
- Gate 6 is NOT approved by this tooling
