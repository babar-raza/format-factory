# Package Self-Containment v3 Plan

## Root Cause: Reports missing from ZIP
`build_declaration_review_package.py` had a hardcoded file list.
Sprint-specific reports (reports/supervisor-r102/*.md) were not included.
Evidence artifacts from the declaration were not included.

## Fix Applied
Added two new sections to `build_declaration_review_package.py`:
1. **Sprint reports**: Iterates `decl.evidence_artifacts`, packages each under `sprint-reports/`
2. **Review directory**: Packages all files from `.local/supervisor/reviews/<run_id>/`

## Evidence Manifest Fix
`evidence_manifest.py` `generate_from_declaration()` now also includes declared
`evidence_artifacts` that live outside the evidence_root directory.

## Package Contents (after fix)
- evidence/ (declaration + manifest)
- materialized/ (materialized manifest, missing report, diffs)
- supervisor/ (grades, review, cycle manifest, MCP, approval gates, etc.)
- state/ (context pack, continuation signal, product gaps, ledger, POC matrix)
- sprint-reports/ (all declared evidence_artifacts)
- review/ (all files from review directory)
- package-manifest.json
