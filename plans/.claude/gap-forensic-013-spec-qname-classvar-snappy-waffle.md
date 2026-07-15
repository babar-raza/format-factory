# GAP-FORENSIC-013: Add ClassVar Annotations to spec_qname Across 8 Formats

## Taskcard Status Summary

| TC-ID | Status |
|---|---|
| TC-GF013-001 | CLOSED |
| TC-GF013-002 | CLOSED |
| TC-GF013-003 | CLOSED |
| TC-GF013-004 | CLOSED |
| TC-GF013-005 | CLOSED |
| TC-GF013-COMMIT-001 | CLOSED |

- **TC-GF013-001** — Create AST-aware transformation script (`tools/backfill/classvar_annotation_backfill.py`). CLOSED: script created, validated idempotent against DIF reference (0 changes on dry-run).
- **TC-GF013-002** — Apply backfill to gnumeric, toml, tsv, zst; restore-and-reapply to isolate from pre-existing unrelated uncommitted drift; verify tests. CLOSED: 24 files annotated, 6006 tests passed.
- **TC-GF013-003** — Apply backfill to csv, abw; verify tests. CLOSED: 15 files annotated, 3247 tests passed.
- **TC-GF013-004** — Apply backfill to fodt, fods (including nested `fods/fods/`); fix fodt literal-string test assertion; verify tests. CLOSED: 79 files annotated, 1 test file fixed, 4129 tests passed (3 pre-existing unrelated failures excluded and independently confirmed via git HEAD comparison).
- **TC-GF013-005** — Cross-format verification (zero bare `spec_qname=` remain via AST scan) and update `/qname-backfill` skill templates to emit ClassVar by default. CLOSED: verified 0/118 bare assignments remain; skill template updated.
- **TC-GF013-COMMIT-001** — *(added during Stage 1 audit, resolves L1-002 and L2-001)* Commit this sprint's work with a **file-list-precise** `git add` (never directory-wildcard or `git add -A`), since ~72 unrelated pre-existing uncommitted files are interleaved in the same 8 package directories. CLOSED: staged exactly 122 files (118 ClassVar source files + tool + test fix + skill template + this plan file) via `git add --pathspec-from-file`, verified staged-set == intended-set exactly (122/122, 0 discrepancy), committed as `f81f1a8b22335d821d53a2ab88251991955ccc6d`. Post-commit re-verification: 12,746 tests passed across all 8 formats (3 pre-existing unrelated failures correctly excluded); 0 of the 122 intended files remain dirty; 365 unrelated pre-existing files remain untouched in the working tree, as intended.

## Context

Every Python model class in the project should declare `spec_qname: ClassVar[str] = "ns:element"` — a typed, machine-readable link to the spec element it implements. 8 of 20 formats (abw, csv, fods, fodt, gnumeric, toml, tsv, zst) use bare assignments instead (`spec_qname = "value"` without the `ClassVar[str]` annotation). This breaks automated tooling that relies on `ClassVar` metadata for type-safe spec tracing.

The qname *values* are correct everywhere — only the type annotation is missing. This is a pure annotation fix with zero runtime behavioral impact.

**Scale:** ~118 files, ~123 classes, ~459 individual attribute annotations across models.py, spec/, and Compat/ layers in the 8 formats.

## Approach: AST-Aware Transformation Script + Format-by-Format Execution

### Step 1 — Create transformation script

Create `tools/backfill/classvar_annotation_backfill.py` with `--format` and `--dry-run` flags.

The script handles three import-mutation categories:

| Category | Current state | Example file | Action |
|----------|--------------|--------------|--------|
| A | `from typing import Any` exists | `csv/models.py` | Append `, ClassVar` to that import |
| B | `from __future__ import annotations` but no typing import | `toml/Compat/toml_table.py` | Insert `from typing import ClassVar` after the `__future__` line |
| C | No imports at all (only docstring + class) | `fods/spec/office/body.py` | Insert `from typing import ClassVar` between docstring and class |

Attribute transformations (class-level only, not module-level):
- `spec_qname = "..."` → `spec_qname: ClassVar[str] = "..."`
- `spec_fact_ref = "..."` → `spec_fact_ref: ClassVar[str] = "..."`
- `namespace_uri = "..."` → `namespace_uri: ClassVar[str] = "..."`
- `local_name = "..."` → `local_name: ClassVar[str] = "..."`
- `facade_names = [...]` → `facade_names: ClassVar[list] = [...]`
- `authority_only = True/False` → `authority_only: ClassVar[bool] = True/False`
- `spec_source = "..."` → `spec_source: ClassVar[str] = "..."`

Skip `build/`, `__pycache__/`, and nested duplicate packages like `fods/fods/` (handle separately).

### Step 2 — Validate against DIF reference

Run in `--dry-run` on `src/python/dif/` (which already has ClassVar). Must produce zero changes — confirming the script is idempotent on correctly-annotated files.

### Step 3 — Execute format-by-format (smallest first)

Process order: gnumeric (6 files) → toml (6) → tsv (6) → zst (6) → csv (7) → abw (8) → fodt (19) → fods (60, including fods/fods/).

Per format:
1. Run the script: `python tools/backfill/classvar_annotation_backfill.py --format {fmt}`
2. Run format tests: `.venv/Scripts/pytest tests/python/{fmt}/ -x -q`
3. Verify no module-level attributes were touched (spot-check analytics files)

### Step 4 — Cross-format verification

- Grep for remaining bare `spec_qname = ` inside class bodies of the 8 formats (should be zero)
- Run V51 validator to confirm all formats pass
- Run full test suite for the 8 formats

### Step 5 — Update the qname-backfill skill template

Update `.claude/commands/qname-backfill.md` code examples (lines ~53, ~81) to use `ClassVar` in their templates, preventing regression when the skill generates new spec classes.

## Key Files

| File | Role |
|------|------|
| `src/python/dif/models.py` | Reference pattern (correct ClassVar form) |
| `src/python/dif/spec/table/header.py` | Reference pattern for spec classes |
| `tools/supervisor/governance_validators_spec.py:45-75` | V51 `_has_spec_qname()` — already handles both forms |
| `.claude/commands/qname-backfill.md` | Governed skill authorizing these changes; templates need updating |
| `registry/python-qname-architecture.json` | Registry showing all 8 as ACCEPTED_VERIFIED (no changes needed) |

## Verification

1. `.venv/Scripts/pytest tests/python/{fmt}/ -x -q` for each format
2. `grep -r "spec_qname = " src/python/{fmt}/ --include="*.py"` should only match module-level (analytics) assignments, not class-level
3. V51 validator continues to pass (it already accepts both forms)
4. Spot-check 2-3 transformed files per format against the DIF reference pattern

## Exclusions

- **Module-level `spec_qname`** in analytics files (e.g., `gnumeric_analytics.py`, `csv/tabular_document.py`) — ClassVar is meaningless at module level
- **Other formats' Compat/spec files** that also lack ClassVar (e.g., DIF Compat, SYLK Compat) — documented as follow-up GAP-FORENSIC-013b
- **Validator changes** — V51 already accepts both forms; no tightening needed for this fix

## Hardening Log (Stage 2 — Convergence Loop, 2026-07-15)

Source: `.supervisor/state/convergence-loop-GAP-FORENSIC-013/stage1-issue-model.json`

| Finding | Disposition |
|---|---|
| L1-001 (fodt literal-string test coupling) | `fixed_by_existing_plan_item` — resolved in TC-GF013-004, no further action |
| L1-002 (work not yet committed) | `taskcard_required` — TC-GF013-COMMIT-001 added above |
| L2-001 (commit-scoping risk from unrelated interleaved files) | `taskcard_required` — folded into TC-GF013-COMMIT-001's required-implementation (file-list-precise staging) |
| L2-002 (3 pre-existing unrelated test failures in fods/zst) | `rejected_with_reason` — independently confirmed via git HEAD comparison to predate this session; VALID_DEFERRED, owned by the unrelated session that performed the FACT→SAL renames |
| L3-001 (V51 validator tolerates bare + ClassVar equally) | `rejected_with_reason` — already a deliberate, documented exclusion above; recorded for visibility only |
| L3-002 (no per-session working-tree isolation) | `rejected_with_reason` — repo-wide infrastructure gap, out of scope for this plan; mitigated here via manual hunk-level diff verification before staging |

Plan revision after hardening: `v2-hardened-with-commit-taskcard`.
