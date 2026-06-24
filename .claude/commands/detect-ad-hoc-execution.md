---
version: "1.0"
last-updated: "2026-06-24"
phase-available: "all"
gate-required: null
skill_type: ATOMIC_SKILL
idempotency: "Re-scan same tree produces same list; classification is deterministic (name match against registry)"
loc_budget: "<90 lines"
test_path: "tests/supervisor/test_detect_ad_hoc_execution.py"
---

# /detect-ad-hoc-execution

Scan `tools/supervisor/*.py` for scripts not referenced in any `skill-registry.yaml` entry's
`implementation_paths` or `command_file`; classify each as GOVERNED vs AD_HOC.

## Purpose

Identify Python scripts in the supervisor tools directory that have no skill registration.
AD_HOC scripts are candidates for promotion (create a skill) or archival.

## Steps

1. Read `.supervisor/skill-registry.yaml` — extract all `implementation_paths` and `command_file` values
2. Scan `tools/supervisor/*.py` (excluding `__init__.py`, `__pycache__`)
3. For each file: if filename in governed set → GOVERNED; else → AD_HOC
4. Write inventory to `.supervisor/ad-hoc-execution-inventory.yaml`

```bash
python tools/supervisor/detect_ad_hoc_execution.py
```

## Output

`.supervisor/ad-hoc-execution-inventory.yaml` with fields:
- `total_files`, `governed_count`, `ad_hoc_count`
- `entries[]`: `file`, `path`, `classification`

## Allowed Paths

- `.supervisor/ad-hoc-execution-inventory.yaml` (write)
- `tools/supervisor/` (read)
- `.supervisor/skill-registry.yaml` (read)

## Forbidden Paths

- `src/**`
- `AGENTS.md`, `CLAUDE.md`

## Constraints

- Read-only scan except for output file
- On file read error: log warning and continue scan; never abort

## Idempotency Contract

Running twice against unchanged tree produces identical output. Classification is a
deterministic filename substring match — no LLM inference.

## Error Handling

On skill-registry.yaml parse failure: write `status: error` to output; exit 0.
Per-file read errors: log to stderr, skip file, continue.

## Usage

```
/detect-ad-hoc-execution
```
