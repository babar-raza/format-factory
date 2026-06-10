# Package Self-Containment — R104

## Problem
R103 review package ZIP contained 28 entries (all supervisor/state files), zero sprint-specific reports, sample outputs, generated prompts, or raw logs.

## Root Cause
build_declaration_review_package.py had evidence_artifacts packaging code (lines 168-191) but it was added after R103's package was built. Additionally, the builder only walked evidence_artifacts from the declaration — not the evidence_root directory tree.

## Fix (R104)
Enhanced build_declaration_review_package.py with 3 new packaging paths:
1. **evidence_root walk**: Recursively walks declaration's `evidence_root` directory, packaging all files under `sprint-evidence/`
2. **evidence_artifacts**: Packages each artifact listed in `evidence_artifacts` (deduplicates with evidence_root)
3. **work item evidence_paths**: Packages each path from `planned_work_items[].evidence_paths`

## Tests
6 new tests in test_package_self_containment.py:
1. `test_package_includes_evidence_root_files` — evidence root recursive walk
2. `test_package_includes_sample_outputs` — sample-outputs/ subdirectory
3. `test_package_includes_generated_prompts` — generated-stream-prompts/ subdirectory
4. `test_package_includes_raw_log` — raw-test-log.txt
5. `test_package_includes_evidence_manifest` — evidence-manifest.yaml
6. `test_package_no_evidence_root_still_works` — graceful fallback

## Verification
Build for R104 will include all sprint-evidence/ files. The R103 defect (D104-01) is now fixed structurally.
