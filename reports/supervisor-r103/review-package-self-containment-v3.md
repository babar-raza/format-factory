# Review Package Self-Containment v3

## What R103 Package Now Includes

### Core (existing)
- evidence/evidence-declaration.yaml
- evidence/evidence-manifest.yaml
- materialized/ (manifest, missing report, diffs)

### Supervisor Outputs (existing)
- supervisor/ (grades, review, cycle manifest, MCP, approval gates, etc.)
- state/ (context pack, continuation signal, gaps, ledger, POC matrix)

### New in R103
- sprint-reports/ — all evidence_artifacts from the declaration (reports, generated prompts)
- review/ — all review-directory outputs (grades, prompts, inspection, cycle manifest)

### Missing (deferred)
- Raw test logs — not yet captured by autonomous-cycle
- Raw build logs — not yet captured
- Per-stream state snapshots — deferred to R104
