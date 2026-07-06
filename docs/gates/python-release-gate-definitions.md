# Python Release Gate Definitions (PYREL-001)

**Mission:** FF-XPLAN-001 | **Taskcard:** W2B-001
**Authority:** This document governs gate execution via `tools/supervisor/gate_executor.py`

---

## Gate Overview

Python product release gates are sequential checks that a format package must pass before publication. Each gate must pass before the next is evaluated.

| Gate | Name | Blocks |
|------|------|--------|
| G1 | Source Readiness | All subsequent gates |
| G2 | Oracle Evidence | G3 and beyond |
| G3 | Package Build | G4 and beyond |
| G4 | Install Verification | G5 |
| G5 | Publication Authorization | Release |

---

## G1 — Source Readiness

**Description:** Format has complete Python source structure.

**Checks:**
- `has_pyproject_toml` — `src/python/{format_id}/pyproject.toml` exists
- `has_init_py` — `src/python/{format_id}/__init__.py` exists
- `has_tests` — `tests/{format_id}/test_*.py` exists OR `tests/packaging/test_*{format_id}*` exists

**Entry criteria:** Format is registered in `registry/format-registry.yaml`
**Exit criteria:** All 3 checks PASS
**Failure action:** CRITICAL (must fix before proceeding)

---

## G2 — Oracle Evidence

**Description:** Oracle has verified verdicts at depth D1 or higher.

**Checks:**
- `oracle_verdicts_exist` — `oracle/formats/{format_id}/reports/oracle-run-summary.json` exists with PASS verdicts > 0
- `oracle_depth_minimum_d1` — `format_depth_score` in {D1, D2, D3}

**Depth levels:**
- D0 — Load didn't crash (insufficient for release)
- D1 — Model property comparison (minimum for G2 pass)
- D2 — Schema validation via lxml RelaxNG (ODF formats)
- D3 — External tool interop (LibreOffice, etc.)

**Entry criteria:** G1 passed
**Exit criteria:** Both checks PASS
**Failure action:** HIGH — run oracle, fix expected_model_properties in oracle YAML

---

## G3 — Package Build

**Description:** Clean build produces wheel and sdist artifacts.

**Checks:**
- `build_succeeds` — `python -m build` exits 0 in clean environment

**Entry criteria:** G2 passed
**Exit criteria:** Build artifacts exist, exit code 0
**Status:** NOT_IMPLEMENTED (requires execution environment)

---

## G4 — Install Verification

**Description:** Clean venv install succeeds and package imports correctly.

**Checks:**
- `install_succeeds` — `pip install <wheel>` in fresh venv exits 0
- `import_succeeds` — `import {format_id}` succeeds

**Entry criteria:** G3 passed
**Exit criteria:** Both checks PASS in clean environment
**Status:** NOT_IMPLEMENTED (requires execution environment)

---

## G5 — Publication Authorization

**Description:** Gate 11 G11-G (commercial release approval) is approved.

**Checks:**
- `gate11_approved` — `registry/format-registry.yaml` has `gates.gate_11.G11-G.status = "approved"` for this format

**Entry criteria:** G1-G4 passed
**Exit criteria:** G11-G approved by Babar Raza
**Failure action:** EXTERNAL — requires Babar Raza business decision (TRUE_EXTERNAL_GATE)

---

## Risk Classification (PYREL-001 W2B-003)

Failures are classified via `tools/supervisor/risk_taxonomy.py`:

| Failure | Risk | Action |
|---------|------|--------|
| G1 structure missing | CRITICAL | Fix source structure |
| G2 no oracle verdicts | HIGH | Run oracle |
| G2 D0-only depth | HIGH | Add expected_model_properties to oracle YAML |
| G3/G4 build/install | HIGH | Fix packaging or environment |
| G5 not approved | EXTERNAL | Babar Raza sign-off |

---

## Implementation

**Executor:** `tools/supervisor/gate_executor.py`
**Usage:**
```bash
python tools/supervisor/gate_executor.py --format fods --gates G1,G2 --dry-run
python tools/supervisor/gate_executor.py --format fods --gates G1,G2,G5
```

**Integration:** Gates G1 and G2 run automatically in `autonomous_cycle.py` Step 2g for any format declared in evidence.
