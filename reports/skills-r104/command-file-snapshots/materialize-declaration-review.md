---
version: "1.0"
last-updated: "2026-06-03"
created-by: skills-r104
---

# /materialize-declaration-review

Build a declaration review package ZIP from an evidence declaration YAML for supervisor grading.

## Usage

Take an evidence declaration YAML and produce a self-contained ZIP package that includes all declared evidence paths, supervisor state, and validation results.

## Required Inputs

- `declaration_path`: Path to the evidence declaration YAML file

## What This Skill Does

1. Read the evidence declaration YAML
2. Validate the declaration schema (required fields, status enums)
3. Collect all files referenced in evidence_paths
4. Include supervisor state files (context-pack, skill-registry, approval-gates)
5. Include validator results and raw logs
6. Build a ZIP with structured directories
7. Compute SHA-256 of the output ZIP
8. Report package contents and any missing files

## Allowed Paths

- `tools/supervisor/build_declaration_review_package.py` (read-only)
- `.local/evidences/*/evidence-declaration.yaml` (read-only)
- `reports/` (read-only, for evidence collection)
- `.supervisor/` (read-only, for state inclusion)
- `.local/supervisor/reviews/` (write ZIP output)

## Forbidden Paths

- `src/net/**` (no product source)
- `src/python/**` (no product source)
- `registry/format-registry.yaml` (no gate authority)

## Stop Conditions

- Declaration file not found
- Declaration YAML is invalid
- Output directory not writable

## Evidence Output

ZIP package at `.local/supervisor/reviews/{run_id}/declaration-review-package.zip` with SHA-256.

## Validation

```bash
.local/venv/Scripts/python tools/supervisor/build_declaration_review_package.py --declaration <path>
```

## Rollback

Delete the generated ZIP file.

## Transcript Requirement

Record package build results in evidence declaration (SHA-256, entry count, missing count).

## Sample Invocation

```bash
.local/venv/Scripts/python tools/supervisor/build_declaration_review_package.py \
  --declaration .local/evidences/skills-r104/evidence-declaration.yaml
```

## Changelog

- v1.0 (2026-06-03): Initial command file for promotion from draft to active (Skills R104)
