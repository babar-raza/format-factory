# Contract Schema Repair Report
**Sprint:** SKILLS-PRD-HARDENING-001-CLOSURE-REPAIR-001
**Date:** 2026-05-17
**File:** `tools/evidence/contracts/skills-prd-hardening-001.yaml`

## Problem

The original contract (committed e5b424d) used incorrect YAML keys:

| Wrong Key | Correct Key | Effect |
|-----------|-------------|--------|
| `required_metadata:` | `required_metadata_files:` | Validator ignored it; showed "Required metadata files: 0 checked" |
| `forbidden_content:` | `forbidden_paths:` | Validator ignored it; showed "Forbidden hits: 0 checked" |

Additionally, `forbidden_content` included `src/python/` and `src/net/` — these cause false
positive forbidden hits in a full-repo bundle (those paths are legitimately bundled).

## Repair Applied

1. Changed `required_metadata:` → `required_metadata_files:` (19 files listed)
2. Changed `forbidden_content:` → `forbidden_paths:` (only `.env` and `node_modules`)
3. Removed `src/python/` and `src/net/` from forbidden list (full-repo bundle model)
4. Updated `emergency_blocker_bundle: true` comment to mention R22 contract artifact

## After Repair — Expected Validator Output

- Required metadata files: 19 checked; missing: 0
- Forbidden paths: `.env`, `node_modules`; hits: 0
- BUNDLE_VALIDATION: PASS (enforced, not just permissive)

## Verification

- `grep required_metadata_files tools/evidence/contracts/skills-prd-hardening-001.yaml` → MATCH
- `grep forbidden_paths tools/evidence/contracts/skills-prd-hardening-001.yaml` → MATCH
- `grep "src/python" tools/evidence/contracts/skills-prd-hardening-001.yaml` → EMPTY (removed)
