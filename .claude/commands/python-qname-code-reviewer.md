---
version: "1.1"
last-updated: "2026-07-14"
phase-available: "all"
gate-required: null
created-by: TC-QHARD-004
spec_qname_required: "true"
product_track: "spec_literal_healing"
---

# /python-qname-code-reviewer

Review a Python format package against the QName architecture standard.
Produces a machine-readable `verdict.json` and 8 additional evidence artifacts.

## Trigger Conditions

Invoke this skill after ANY of the following:
- Added or modified files in `src/python/{format}/spec/`
- Added or modified files in `src/python/{format}/Compat/`
- Modified `src/python/{format}/models.py` to add or rename model classes
- Updated `shared/qname-registry/{format}.yaml` status entries
- Before declaring a QName hardening taskcard complete (TC-QHARD-*)

## Required Input

- `format_id` — target format (e.g., `fods`, `fodt`, `csv`, `xcf`)

## 13 Structural Checks

Run all 13 checks in order. Each check produces a `PASS`, `WARN`, or `FAIL` result.
A single `FAIL` result → overall verdict `REWORK_REQUIRED`.
All `PASS` (WARN allowed) → overall verdict `ACCEPTED_VERIFIED`.

### Check 1 — Directory Structure (D5)
Verify the package follows the canonical three-layer layout:
- `src/python/{format}/spec/{namespace}/{element}.py` — spec authority classes
- `src/python/{format}/Compat/{format}_{entity}.py` — public facades
- `src/python/{format}/__init__.py` — stable public API

**FAIL** if `Compat/` files exist but `spec/` directory is empty (facades without authority).
**WARN** if `spec/` directory does not exist yet (Phase 0 state — acceptable if registry status is `seeded`).
**PASS** if full three-layer structure is present.

### Check 2 — Codec I/O Purity
Verify `src/python/{format}/{format}_codec.py` (or `{format}_parser.py`) contains ONLY:
- `load` / `write` / `parse` entry points
- I/O helpers (file open, byte operations)
- Exception classes

**FAIL** if codec file contains `class` definitions for domain model objects.
**FAIL** if codec file defines functions containing `spec_qname` attribute assignment.
**PASS** if domain logic is in `spec/` or `models.py` only.

### Check 3 — Analytics Boundary
Verify no NEW analytical functions were added to `{format}_analytics.py` without a corresponding
`gap_ledger_ref` in `reports/capability-layer/gap-ledger.json`.

**FAIL** if `{format}_analytics.py` has functions with no `GAP-*` reference in their docstring.
**WARN** if analytics file is at `baseline_loc_cap` (no room for growth).
**PASS** if all analytics functions have traceable `GAP-*` references.

### Check 4 — spec_qname Coverage
For every class exported in `src/python/{format}/__init__.py`:
- Skip Error subclasses (`*Error`, `*Exception`).
- Skip constants (`FORMAT_ID`, `SPEC_VERSION`, `PACKAGE_VERSION`).
- All others must have `spec_qname` as a class-level attribute.

**FAIL** if any non-exempt exported class lacks `spec_qname`.
**WARN** if the class is in `models.py` (legacy location) rather than `spec/`.
**PASS** if all non-exempt exported classes have `spec_qname`.

### Check 5 — QName → SAL Fact Traceability
For each `spec_qname` value found in `src/python/{format}/`:
- Look up the value in `.local/spec-cache/sal-facts-latest.json` (field `qname`).
- OR verify it matches a `qname` entry in `shared/qname-registry/{format}.yaml`.

**FAIL** if a `spec_qname` value exists in code but cannot be traced to either source.
**WARN** if the registry entry has `status: seeded` (not yet confirmed against spec).
**PASS** if every `spec_qname` value traces to a known fact or registry entry.

### Check 6 — Registry Fact Reference Existence
For each entry in `shared/qname-registry/{format}.yaml` with `spec_fact_ref != null`:
- Verify the fact reference exists in `.local/spec-cache/sal-facts-latest.json`.

**FAIL** if a `spec_fact_ref` value in the registry does not exist in the SAL cache.
**WARN** if the SAL cache is unavailable (`.local/spec-cache/` does not exist).
**PASS** if all non-null spec_fact_refs resolve successfully.

### Check 7 — Compat Facade Inheritance
For every file in `src/python/{format}/Compat/*.py` (excluding `__init__.py`):
- The primary class defined in the file must inherit from exactly one spec authority class.
- The spec authority class must exist in `src/python/{format}/spec/` (not in `models.py`).

**FAIL** if a Compat facade has no base class.
**FAIL** if a Compat facade inherits directly from `object` or `models.py` class (should use `spec/`).
**WARN** if base class is in `models.py` (legacy state during Phase 1 transition).
**PASS** if all facades inherit from `spec/` authority classes.

### Check 8 — Public API Stability
Compare current `src/python/{format}/__init__.py` exports against the previous commit:
- Removed symbols are **FAIL** (breaking change).
- Added symbols are **PASS** (backwards compatible).
- Renames are **FAIL** (breaking change).

**FAIL** if any previously exported symbol is absent from current `__all__`.
**PASS** if exports are stable or additive only.
**SKIP** if this is the first commit for this file (no previous version to compare).

### Check 9 — Source File LOC Caps
For each modified file under `src/python/{format}/`:
- Read `baseline_loc_cap` from `registry/source-structure-baseline.json`.
- Compute current LOC using `sum(1 for _ in open(path, encoding='utf-8', errors='replace'))`.

**FAIL** if any file exceeds its `baseline_loc_cap`.
**WARN** if any file is within 10% of its `baseline_loc_cap` (approaching cap).
**PASS** if all files are within caps.

### Check 10 — Test Coverage Layers
Verify tests exist for the modified format covering all four layers:
- Import test: `from src.python.{format} import {ClassName}` succeeds.
- Metadata test: `{cls}.spec_qname == "{expected_qname}"` asserts correct value.
- Behavioral test: class methods return expected output on sample data.
- Regression test: previously passing tests still pass (no regressions introduced).

**FAIL** if import test or regression tests do not exist or fail.
**WARN** if behavioral tests are present but use only `spec_qname` assertions (Check V36).
**PASS** if all four layers have passing tests.

### Check 11 — No Forbidden Stub Terms
Scan all modified Python files for forbidden placeholder patterns:
- `# TODO: implement`
- `pass  # stub` or bare `pass` as entire class/function body (single-pass)
- `# placeholder`
- `# stub`
- `# mock`
- `# dummy`
- `raise NotImplementedError`

**FAIL** if any of these patterns appear in a class or function that is exported in `__init__.py`.
**WARN** if patterns appear in non-exported internal helpers.
**PASS** if no forbidden stub terms found.

### Check 12 — Backfill Inventory Updated
Verify `docs/audits/python-qname-backfill-inventory.csv` contains rows for the target format
with `migration_status` updated to reflect current progress:
- Classes with `spec_qname` implemented → `migration_status = DONE`
- Classes in progress → `migration_status = IN_PROGRESS`
- Not yet started → `migration_status = PENDING`

**FAIL** if the CSV has no rows for this format at all.
**WARN** if any class newly having `spec_qname` is still marked `PENDING` in the CSV.
**PASS** if CSV rows exist and statuses reflect current implementation state.

### Check 13 — State Transition Evidence
For each entry in `shared/qname-registry/{format}.yaml` with `status` other than `seeded`:
- `architecture_only` → evidence: spec/ directory exists with matching file
- `implementing` → evidence: class exists in python_file with spec_qname attribute
- `implemented` → evidence: class has spec_qname + behavioral test exists
- `stable` → evidence: `implemented` evidence + no regressions in last test run

**FAIL** if a registry entry claims `implemented` or `stable` status but the python_file
lacks the class or the behavioral test does not exist.
**WARN** if a registry entry claims `implementing` but python_file is missing.
**PASS** if all status transitions have supporting evidence.

## Verdicts

| Verdict | Condition |
|---|---|
| `ACCEPTED_VERIFIED` | All 13 checks PASS or WARN (no FAIL) |
| `REWORK_REQUIRED` | One or more checks FAIL — list which checks |
| `BLOCKED_EXTERNAL_AUTHORITY` | Check 8 (API stability) flags a breaking change that requires Gate 11 approval |
| `DEFERRED_WITH_APPROVED_REASON` | One or more checks WARN but the agent has an approved reason (must cite plan taskcard ID) |

## Steps

1. **Collect target files:** List all Python files modified in `src/python/{format}/`.
   If running in pre-commit mode, use `git diff --name-only HEAD`.
   If running as post-implementation review, scan all files in the format package.

2. **Run Checks 1-13** in order. Record result (`PASS`, `WARN`, `FAIL`) and a one-line
   reason for each check.

3. **Compute overall verdict** from check results using verdict table above.

4. **Write evidence artifacts** to `.local/qname-review/{format}-{run_id}/`:
   - `verdict.json` — machine-readable verdict + per-check results
   - `qname-map.json` — `{symbol: spec_qname}` for all exported symbols
   - `facade-map.json` — `{facade_file: spec_authority_class}` for all Compat/ files
   - `sal-fact-trace.json` — `{spec_qname: fact_ref}` verification results
   - `no-stub-scan.txt` — output of forbidden-term grep across modified files
   - `import-check.log` — results of import smoke tests
   - `test-run.log` — full pytest output for format's test suite
   - `source-baseline-diff.json` — `{file: {current_loc, cap, delta}}` for all modified files
   - `reviewer-notes.md` — human-readable summary of findings

5. **Print summary** to stdout:
   ```
   python-qname-code-reviewer: {format_id}
   Verdict: {verdict}
   Checks passed: {N}/13
   Checks warned: {W}/13
   Checks failed: {F}/13
   Evidence at: .local/qname-review/{format}-{run_id}/verdict.json
   ```

6. **If REWORK_REQUIRED:** List each failing check with its FAIL reason. Do NOT proceed
   to declare the taskcard complete. Fix the findings and re-run the reviewer.

7. **If ACCEPTED_VERIFIED:** The result can be cited as evidence in an evidence declaration.
   `verdict.json` path is the canonical evidence artifact.

## Evidence Output Format

### verdict.json
```json
{
  "skill_id": "python-qname-code-reviewer",
  "format_id": "fods",
  "run_id": "fods-20260623-001",
  "verdict": "ACCEPTED_VERIFIED",
  "checks": [
    {"check": 1, "name": "directory_structure", "result": "PASS", "reason": "..."},
    {"check": 2, "name": "codec_io_purity", "result": "PASS", "reason": "..."},
    ...
    {"check": 13, "name": "state_transition_evidence", "result": "PASS", "reason": "..."}
  ],
  "pass_count": 13,
  "warn_count": 0,
  "fail_count": 0,
  "evidence_root": ".local/qname-review/fods-20260623-001/",
  "timestamp": "2026-06-23T00:00:00Z"
}
```

## Allowed Paths (evidence writes only)

- `.local/qname-review/{format}-{run_id}/` (CREATE evidence directory)
- `docs/audits/python-qname-backfill-inventory.csv` (UPDATE migration_status fields)

## Forbidden Paths

- `src/python/**` (read-only during review)
- `shared/qname-registry/**` (read-only during review)
- `registry/source-structure-baseline.json` (read-only)
- `plans/**`, `reports/**`, `tools/**` (out of scope)

## Stop Conditions

- `BLOCKED_SAL_CACHE_UNAVAILABLE` — Check 5/6 cannot run; `.local/spec-cache/` missing.
  Degrade gracefully: skip SAL fact checks, mark as WARN with reason.
- `BLOCKED_NO_REGISTRY_ENTRY` — `shared/qname-registry/{format}.yaml` does not exist.
  Create it first using the QName registry seed pattern.
- `BLOCKED_BREAKING_API_CHANGE` — Check 8 detects removed exports. Escalate to
  `BLOCKED_EXTERNAL_AUTHORITY` verdict; do NOT auto-fix.

## Sample Invocation

```
/python-qname-code-reviewer
# Inputs:
#   format_id: fods
```

Expected output:
```
python-qname-code-reviewer: fods
Verdict: ACCEPTED_VERIFIED
Checks passed: 13/13
Checks warned: 0/13
Checks failed: 0/13
Evidence at: .local/qname-review/fods-20260623-001/verdict.json
```

## Reference Notes: Additional Python Tooling Awareness (informational, non-blocking)

> Source: `modern-python` skill (Trail of Bits, CC-BY-SA-4.0) — non-hook guidance content only.
> This section does NOT add a 14th check, does NOT change any verdict, and does NOT introduce
> any lifecycle-triggered PATH-manipulation shim or new blocking gate (that mechanism was
> deliberately excluded from import — see plan `yes-my-earlier-answer-humming-waffle.md` §7.1
> item 3). It is supplementary awareness content sitting alongside — never replacing — this
> reviewer's own stricter, binding rules (spec_qname coverage, `.venv/Scripts/pytest`
> execution per project convention, and the `baseline_loc_cap` LOC-cap governance in
> `registry/source-structure-baseline.json`).

### Tool-replacement table (external guidance, not FF policy)

| Legacy tool | Modern replacement (per modern-python) | FF's actual current tool (verified) |
|---|---|---|
| pip, virtualenv, pip-tools, pipx, pyenv | `uv` | `pip` — CI installs deps with `pip install ruff` (`.github/workflows/ci.yml`); no `uv.lock` or `uv` invocation found anywhere in the repo |
| flake8, black, isort, pyupgrade | `ruff` | `ruff` — FF already uses ruff (`[tool.ruff]` block in `pyproject.toml`; `ruff check` step in CI; `astral-sh/ruff-pre-commit` in `.pre-commit-config.yaml`). **Aligned.** |
| mypy, pyright | `ty` | Neither `ty` nor mypy/pyright are configured in `pyproject.toml` or CI — FF currently runs no static type checker. **Gap; noted for awareness only, not a recommendation to adopt `ty` specifically.** |
| unittest, nose | `pytest` | `pytest` — FF already uses pytest exclusively; project convention is the `.venv/Scripts/pytest` binary (not `python -m pytest`, see MEMORY.md). **Aligned.** |
| pre-commit | `prek` | `pre-commit` — `.pre-commit-config.yaml` uses the classic `pre-commit` framework (ruff, ruff-format, and local governance hooks); `prek` is not used anywhere in the repo. **Diverges from modern-python's recommendation; no change proposed by this note.** |

### Security-tooling table (external guidance, informational)

| Tool | Purpose |
|---|---|
| shellcheck | Shell script static analysis |
| detect-secrets | Secret/credential scanning |
| actionlint | GitHub Actions workflow linting |
| zizmor | GitHub Actions security auditing |
| pip-audit | Python dependency vulnerability scanning |
| Dependabot | Automated dependency update PRs |

### Anti-patterns table (external guidance, informational)

| Anti-pattern | Prefer instead |
|---|---|
| `uv pip install <pkg>` | `uv add <pkg>` (project dependency) or `uv sync` (install from lockfile) |
| Poetry | `uv` |
| mypy / pyright | `ty` |

**Precedence:** where this reference content conflicts with FF's own rules elsewhere in this
file (Checks 1-13, LOC caps, spec_qname requirements, `.venv/Scripts/pytest`), FF's own rules
govern. This section never overrides a check result and cannot change a verdict.

## Changelog

- 1.0 (2026-06-23): Initial governed command for QName architecture compliance review.
  13 checks from TC-QHARD-004 (imperative-drifting-lecun plan §Phase 0).
  4 verdicts; 9 evidence artifacts. spec_qname_required: true.
- 1.1 (2026-07-14): Added "Reference Notes: Additional Python Tooling Awareness" section
  (TC-EXT-019-01) — tool-replacement and anti-patterns tables merged from the `modern-python`
  skill (non-hook guidance only; lifecycle-hook PATH-manipulation mechanism explicitly
  excluded per plan §7.1 item 3). Informational only; does not alter checks or verdicts.

## Required Inputs

- `format_id` — format identifier from the format registry
