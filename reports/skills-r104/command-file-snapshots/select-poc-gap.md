---
version: "1.0"
last-updated: "2026-06-03"
created-by: skills-r104
---

# /select-poc-gap

Select the next product gap from the POC matrix for sprint execution based on priority and readiness.

## Usage

Analyze the POC target matrix and select the highest-priority gap that is ready for execution, considering dependencies, skill availability, and current sprint capacity.

## Required Inputs

- `matrix_path`: Path to POC targets YAML (default: `product-capability-matrix/poc-targets.yaml`)

## What This Skill Does

1. Read the POC target matrix
2. Filter gaps by status (not_started or in_progress)
3. Score gaps by priority, dependency readiness, and skill availability
4. Return the top N gaps suitable for the next sprint
5. For each gap, identify the skill_id that should execute it

## Allowed Paths

- `tools/supervisor/select_poc_gaps.py` (read-only)
- `product-capability-matrix/poc-targets.yaml` (read-only)
- `.supervisor/skill-registry.yaml` (read-only)
- `reports/supervisor/` (read-only)
- `reports/skills-r*/` (write selection results)

## Forbidden Paths

- `src/net/**` (no product source)
- `src/python/**` (no product source)
- `registry/format-registry.yaml` (no gate authority)

## Stop Conditions

- Matrix file not found
- No gaps available for execution

## Evidence Output

Write selection to `reports/skills-r{N}/selected-gaps.json` or `reports/supervisor/product-gap-selection.md`.

## Validation

```bash
.local/venv/Scripts/python tools/supervisor/select_poc_gaps.py
```

## Rollback

No state changes to roll back. This is a read-only selection tool.

## Transcript Requirement

Record gap selection results in evidence declaration when part of a sprint.

## Sample Invocation

```bash
.local/venv/Scripts/python tools/supervisor/select_poc_gaps.py
```

## Changelog

- v1.0 (2026-06-03): Initial command file for promotion from draft to active (Skills R104)
