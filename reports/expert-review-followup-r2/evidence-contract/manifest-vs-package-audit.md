# Manifest-vs-Package Audit — Sprint expert-review-followup

## Sprint ID
FORMAT-FACTORY-EXPERT-REVIEW-FOLLOWUP-REPAIR-PLUS-ADVANCEMENT-001

## Review Package (prior sprint, package 103)
`.local/supervisor/reviews/expert-review-followup/declaration-review-package.zip`
82 entries.

## Root Cause of Defect

`build_declaration_review_package.py` packages items declared in:
- `evidence_artifacts[]` in the evidence declaration
- `evidence_paths[]` in each `planned_work_items[]` entry

It does NOT package items declared only in `evidence-manifest.yaml`'s `artifacts:` section.

## Items Present in evidence-manifest.yaml but ABSENT from ZIP

| Path | Type | In Declaration evidence_artifacts? | In ZIP? |
|------|------|--------------------------------------|---------|
| `reports/expert-review-followup/raw-logs/python-tests.log` | raw_log | NO | NO |
| `reports/expert-review-followup/lane-execution-ledger.json` | lane_ledger | NO | NO |

## Items Correctly Present in ZIP

| Path | Type | Status |
|------|------|--------|
| `.local/evidences/expert-review-followup/sample-outputs/sample.abw` | sample_output | PRESENT |
| `.local/evidences/expert-review-followup/sample-outputs/gnumeric-export.csv` | sample_output | PRESENT |
| `.local/evidences/expert-review-followup/sample-outputs/sample-4x4.ppm` | sample_output | PRESENT |
| `.local/evidences/expert-review-followup/sample-outputs/sample.zst` | sample_output | PRESENT |
| `reports/expert-review-followup/00-preflight.md` | report_md | PRESENT |
| `reports/expert-review-followup/package-artifacts/FormatFactory.Fods.0.1.0-tier0.nupkg` | nupkg | PRESENT |
| `reports/expert-review-followup/package-artifacts/FormatFactory.Fodt.0.1.0-tier0.nupkg` | nupkg | PRESENT |
| `reports/expert-review-followup/package-artifacts/FormatFactory.Netpbm.0.1.0-r85-poc.nupkg` | nupkg | PRESENT |
| All 10 pyproject.toml files | package_toml | PRESENT |
| `src/net/netpbm/README.md` | readme_md | PRESENT |

## Fix for This Sprint

In the R2 sprint declaration (FORMAT-FACTORY-EXPERT-REVIEW-FOLLOWUP-QUALITY-AND-PACKAGING-HARDENING-002),
add the following to `evidence_artifacts` in the declaration:

```yaml
- type: raw_log
  path: reports/expert-review-followup/raw-logs/python-tests.log
- type: lane_ledger
  path: reports/expert-review-followup/lane-execution-ledger.json
```

This ensures these files appear in the new review ZIP.

## Anti-Skip Result (from prior ZIP)

The anti-skip check in the prior ZIP (`review/anti-skip-check-result.json`) shows:
- `total_checks: 16`, `violations: 0`, `all_pass: true`
- `missing_raw_logs`: PASS (found python-tests.log on disk)
- `missing_lane_ledger`: PASS (found lane-execution-ledger.json on disk)

The anti-skip checker searches the repo filesystem — it finds these files on disk.
The defect is purely that they are absent from the ZIP (the deliverable).
