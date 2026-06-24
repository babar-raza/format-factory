# Production Code Governance Standard

**Authority:** Format Factory project governance for all production source code.
**Effective:** 2026-06-24
**Binding contract:** [`docs/code-quality/production-readiness-standard.md`](../code-quality/production-readiness-standard.md)

---

## Purpose

This document is the governance companion to the
[Production Readiness Standard](../code-quality/production-readiness-standard.md) (PRS).
The PRS is the **single authoritative code-quality contract** for Format Factory. This
document does not duplicate PRS content. Instead it:

1. Cross-references PRS sections for areas already governed there.
2. Adds governance rules for areas not covered by the PRS (testing process, documentation,
   build/CI, cross-language parity, source generation, and validator compliance).
3. Defines enforcement expectations and escalation paths.

All `src/` code changes must satisfy both documents. In case of conflict, the PRS wins
for code-quality rules; this document wins for governance process rules.

---

## A. Architecture and Library Design

Governed by **PRS Section 1** (Architecture and Library Design).

- Python package boundaries: PRS SS1.1 (module table, max LOC per file type).
- .NET project boundaries: PRS SS1.2 (file-per-concern, 800 LOC cap).
- Shared infrastructure: PRS SS1.3 (base classes in `src/python/_shared/`).

No additional governance rules beyond PRS Section 1.

---

## B. Object Model Quality

Governed by **PRS Section 2** (Object Model Quality).

- ODF spec traceability (`spec_qname`): PRS SS2.1.
- Non-ODF spec traceability (`spec_concept:` docstring tag): PRS SS2.2.

No additional governance rules beyond PRS Section 2.

---

## C. Naming Conventions

Governed by **PRS Section 2.3** (Canonical Naming) and **PRS Section 5** (Naming and
Organization).

- Canonical class names derive from spec QNames, not format prefixes: PRS SS2.3.
- Analytics function naming (`{format}_{property}_{formula}`): PRS SS5.1.
- Parse function naming (`parse_{format}`, `parse_{format}_strict`, `probe_{format}`): PRS SS5.2.
- Prohibited module names (`utils.py`, `helpers.py`, etc.): PRS SS5.3.

No additional governance rules beyond PRS Sections 2.3 and 5.

---

## D. File and Folder Organization

Governed by **PRS Section 1.1** (Python), **PRS Section 1.2** (.NET), and **PRS Section 3.4**
(No Orphan Files).

- Target directory layout per format: see also
  [`plans/product-code-healing-plan.md`](../../plans/product-code-healing-plan.md) SS "Target
  Architecture Per Python Format Module".
- Every `.py` file under `src/` must have a recognized owning purpose: PRS SS3.4.

No additional governance rules beyond PRS Sections 1.1, 1.2, and 3.4.

---

## E. Error Handling

Governed by **PRS Section 3.5** (Production Readiness) — bullet "Error handling via
format-specific exception hierarchy" — and **PRS Section 1.1** (`exceptions.py` row in
module table, hard cap 50 LOC).

### E.1 Exception Hierarchy (governance addition)

All format-specific exceptions must inherit from the shared base:

```
src.python._shared.exceptions.FormatFactoryError
```

New format packages must wire this from day one. Existing packages migrate per their
decomposition taskcard (PRS SS1.3).

### E.2 Fail-Fast at System Boundaries

Library entry points (`parse_{format}`, `load_{format}`) must validate inputs and raise
immediately on:

- Missing or unreadable file path.
- File magic bytes inconsistent with declared format.
- Truncated or zero-length input.

Internal helper functions may assume pre-validated input.

---

## F. Testing Standards

PRS Section 6 covers test layers and basic requirements. This section adds governance
process rules.

### F.1 Test File Naming

| Convention | Example |
|------------|---------|
| Unit tests | `tests/python/{format}/test_{format}_{feature}.py` |
| Regression tests | `tests/python/{format}/test_{format}_regression_{issue}.py` |
| Integration tests | `tests/python/integration/test_{format}_cross_{target}.py` |
| Supervisor/governance tests | `tests/supervisor/test_{validator_or_feature}.py` |

Test files that do not follow these patterns are flagged during audit
(`tools/audit_deepening_tests.py`).

### F.2 Test Layer System

The five-layer model is defined in PRS SS6.1. Governance enforcement:

| Layer | Gate requirement |
|-------|-----------------|
| L0 (model unit) | Must pass before ANY commit touching model files |
| L1 (parser) | Must pass before ANY commit touching parser files |
| L2 (roundtrip) | Must pass before ANY commit touching writer files |
| L3 (analytics) | Must pass before ANY commit touching analytics files |
| L4 (integration) | Must pass before cross-format or packaging changes |

Layer adequacy is checked by `sprint_executor_validate.py` (WARN until 2026-07-18,
then ERROR).

### F.3 Minimum Coverage Expectations

- Every public function exported in `__all__` must have at least one test exercising it.
- Every analytics function must have at least one assertion verifying its return value
  against a known input.
- Zero-test functions are flagged by `governance_validators.py` validator V36
  (`validate_no_stub_tests`).

### F.4 No Stub Tests

Tests containing only trivial assertions (e.g., `assert result is not None`,
`assert callable(fn)`, or `assert obj.spec_qname == "..."` with no behavioral check) are
classified as stub tests. V36 warns when >80% of assertions in a test file are weak.

### F.5 Test Runner

- Always use `.venv/Scripts/pytest` (Windows) or `.venv/bin/pytest` (Linux/macOS).
- Never use `python -m pytest` — system Python may lack pytest.
- Marker-based collection (`-m "layer0"`) is prohibitively slow on this codebase (46k+
  tests). Use direct path-based invocation instead.

---

## G. Documentation Standards

### G.1 Public API Docstrings

Every function exported via `__all__` must have a docstring containing:

1. A one-line summary of what the function does.
2. Parameter types and descriptions (may use Google-style or NumPy-style).
3. Return type and description.

Docstrings may be brief but must not be auto-generated boilerplate (e.g., "This function
does X" restating the function name with no added information).

### G.2 Module-Level Docstrings

Every Python module under `src/python/` must have a module-level docstring identifying:

- The format it belongs to.
- Its role (parser, model, analytics, writer, exceptions).
- For non-ODF formats: a `spec_concept:` tag (PRS SS2.2).

### G.3 No Auto-Generated Boilerplate

Files must not contain large blocks of auto-generated documentation that restate code
structure without adding semantic value. Docstrings must describe intent and behavior,
not merely echo signatures.

### G.4 Changelog Discipline

Source changes that alter public API surface (add/remove/rename exported functions) must
be noted in the sprint evidence declaration. There is no separate CHANGELOG file; the
evidence trail in `.local/evidences/` serves as the project changelog.

---

## H. Packaging Standards

### H.1 Package Matrix

All packaged formats are listed in `packaging/python/package-matrix.yaml`. A format
must appear in this matrix before wheels are built for it.

### H.2 Wheel Build Requirements

- Wheels are built via `packaging/python/build-local-packages.py`.
- Output directory: `.local/package-builds/python-foss/`.
- Install verification requires the `--user` flag on Windows.
- A format's wheel must import cleanly (`python -c "import {format}"`) after install.

### H.3 No Architecture-Only Stubs in Packages

Files marked `# GENERATED -- architecture_only` must not be included in published
packages. V48 (`validate_architecture_only_stub_gate`) blocks RELEASE_GATE items that
cite architecture-only stub files as evidence.

---

## I. Build and CI Standards

### I.1 Python Build Gate

Before any Python format change is committed:

```bash
.venv/Scripts/pytest tests/python/{format}/ --tb=short -q
```

Must exit 0 with zero test failures. Passing test count must be >= the pre-change count
(no regressions).

### I.2 .NET Build Gate

Before any .NET format change is committed:

```bash
dotnet build src/net/{Format}/{Format}.csproj --no-restore
```

Must exit 0 with zero errors. Warnings are acceptable but should trend downward.

### I.3 Pytest Collection Gate

Full pytest collection must succeed without import errors:

```bash
.venv/Scripts/pytest --collect-only tests/python/{format}/ -q
```

Collection failures (e.g., `ImportError` on test module load) indicate broken imports
and block the commit.

### I.4 Architecture Validator Gate

```bash
python tools/validators/validate_source_architecture.py src/python/{format}/
```

Must exit 0. Any FAIL result blocks the commit. See PRS SS7.1 for the full validator
table.

---

## J. Cross-Language Parity

### J.1 Scope

Cross-language parity applies to **commercial-track formats** — formats where both Python
and .NET implementations exist under `src/python/` and `src/net/`.

### J.2 Parity Requirements

| Aspect | Requirement |
|--------|-------------|
| Public API surface | Same set of operations available in both languages |
| Parse output | Equivalent domain model (field names may follow language conventions) |
| Spec traceability | Same `spec_qname` values in both implementations |
| Test coverage | Equivalent test scenarios (not identical code) |

### J.3 Parity Tracking

Cross-language parity status is tracked per format in `registry/format-registry.yaml`
under the `cross_language_parity` field. Values: `full`, `partial`, `python_only`,
`dotnet_only`.

### J.4 Gate 11 Parity Criterion

Gate 11 (commercial release) requires cross-language parity for all formats included in
the release. This is assessed via criteria C1-C20 (.NET) and P1-P11 (Python) in
`plans/spec-to-feature-radical-correction-plan.md`.

---

## K. Analytics Separation

Governed by **PRS Section 3.1** (RULE-AM-001) and **PRS Section 8.1** (Analytics
Separation Protocol).

- Analytics functions must reside in `analytics.py` or `analytics/` subpackage.
- Detection pattern: PRS SS3.1.
- Separation protocol (move procedure): PRS SS8.1.
- GOV_BLOCK enforcement for violations: PRS SS7.4.

### K.1 Analytics Suspension Rule (governance addition)

Arithmetic analytics rotation (functions matching `{format}_*_mod_*_times_*`) is
**suspended** as of 2026-06-18. New analytics functions must:

1. Trace to a GAP-* entry in `reports/capability-layer/gap-ledger.json`.
2. Reference a spec fact (FACT-{FORMAT}-*) from `.local/spec-cache/`.
3. Route to `{format}_analytics.py` (not the main codec/parser file).

Functions without gap-ledger backing are rejected by TC-GUARD-001 (unconditional BLOCK
mode in `autonomous_cycle.py`).

---

## L. Source Generation Rules

### L.1 Generated File Marker

All files produced by code generators must include a marker comment on the first
non-blank, non-shebang line:

- Python: `# GENERATED` (optionally followed by ` -- {generator_name}`)
- C#: `// GENERATED` (optionally followed by ` -- {generator_name}`)

### L.2 Architecture-Only Marker

Spec skeleton stubs produced by `tools/spec/generate_canonical_stubs.py` must include:

```python
# GENERATED -- architecture_only
```

These files are NOT behavioral implementations. They exist as spec-parity placeholders
and must not be cited as product-progress evidence.

### L.3 No Manual Edits to Generated Files

Files bearing the `# GENERATED` marker must not be manually edited. Changes must flow
through the generator. If manual edits are required, remove the `# GENERATED` marker
and document the reason.

### L.4 Generator Registration

All code generators must be listed in `tools/` with a clear entry point. Ad-hoc
generation scripts in `.local/` are permitted for one-time use but must not produce
files committed to the repository without the `# GENERATED` marker.

---

## M. Governance Validator Compliance

### M.1 Validator Suite

All `src/` changes must pass the governance validator suite. The validators are defined
in:

- `tools/supervisor/governance_validators.py` — 48 validators (as of 2026-06-24)
- `tools/validators/validate_source_architecture.py` — anti-monolith rules
- `tools/validators/source_structure_validator.py` — LOC and function count checks

See PRS SS7.1 for the validator table.

### M.2 Validator Execution

Validators run automatically during `autonomous-cycle` via `supervisor_loop.py`. They
can also be run manually:

```bash
python tools/supervisor/governance_validators.py
python tools/validators/validate_source_architecture.py src/python/{format}/
python tools/validators/source_structure_validator.py
```

### M.3 Severity Levels

| Severity | Meaning | Effect |
|----------|---------|--------|
| FAIL | Structural violation | Blocks sprint, blocks commit |
| WARN | Known issue or soft limit | Logged, does not block |
| PASS | Compliant | No action needed |

### M.4 Adding New Validators

New validators must:

1. Be added to `governance_validators.py` or a dedicated validator file in `tools/validators/`.
2. Be registered in `governance_validator_runner.py`.
3. Have regression tests in `tests/supervisor/test_governance_validators.py`.
4. Start as WARN for one sprint cycle before being promoted to FAIL (unless the
   violation is structural and safety-critical).

### M.5 Baseline JSON Integrity

`registry/source-structure-baseline.json` is the single source of truth for file-level
caps. Rules:

- `baseline_loc_cap` is **write-once** — it may only decrease, never increase.
- `baseline_functions_cap` is **write-once** — same monotonicity rule.
- `loc` and `functions` fields are mutable (updated to reflect current state).
- New violations detected by the pre-closeout scanner are added with `category:
  new_violation_detected`.
- Updates after healing use `tools/supervisor/update_source_baseline.py --path <file>`.

---

## Enforcement Summary

| Area | Primary enforcer | Cross-reference |
|------|-----------------|-----------------|
| Architecture (A) | `validate_source_architecture.py` | PRS SS1 |
| Object model (B) | `governance_validators.py` | PRS SS2 |
| Naming (C) | `validate_source_architecture.py` | PRS SS2.3, SS5 |
| File organization (D) | `check_orphan_files` | PRS SS1.1, SS3.4 |
| Error handling (E) | Code review + exception hierarchy check | PRS SS3.5 |
| Testing (F) | `sprint_executor_validate.py`, V36 | PRS SS6 |
| Documentation (G) | Code review (no automated enforcer yet) | -- |
| Packaging (H) | `build-local-packages.py`, V48 | -- |
| Build/CI (I) | pytest + dotnet build + architecture validator | PRS SS7 |
| Cross-language (J) | `format-registry.yaml` tracking | -- |
| Analytics separation (K) | `validate_source_architecture.py`, TC-GUARD-001 | PRS SS3.1, SS8.1 |
| Source generation (L) | `# GENERATED` marker convention | -- |
| Validator compliance (M) | `governance_validators.py` (48 validators) | PRS SS7.1 |

---

## Reference Documents

- **Production Readiness Standard (PRS):** [`docs/code-quality/production-readiness-standard.md`](../code-quality/production-readiness-standard.md)
- **Product Code Healing Plan:** [`plans/product-code-healing-plan.md`](../../plans/product-code-healing-plan.md)
- **Spec-to-Feature Correction Plan:** [`plans/spec-to-feature-radical-correction-plan.md`](../../plans/spec-to-feature-radical-correction-plan.md)
- **Source Structure Baseline:** `registry/source-structure-baseline.json`
- **Format Registry:** `registry/format-registry.yaml`
- **Governance Validators:** `tools/supervisor/governance_validators.py`
- **Architecture Validator:** `tools/validators/validate_source_architecture.py`
- **Structure Validator:** `tools/validators/source_structure_validator.py`
