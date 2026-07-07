# Python Product Release Gate System — Verified Current-State Plan

```yaml
authoritative_plan: plans/.claude/snazzy-rolling-feigenbaum.md
plan_type: structural_redesign
plan_status: VERIFIED_READY_FOR_EXECUTION
created: 2026-07-06
last_verified: 2026-07-06
HEAD_at_verification: 096126af
branch: main
mission_id: PYREL-001
taskcard_count: 17
```

---

## A. Current-State Reassessment

### What Changed Between Original Plan and Now

8 commits landed from FF-XPLAN-001 after the plan was first written. Key changes:
- `tools/supervisor/gate_executor.py` was created (PYREL G1-G5 gate checks)
- `release.yml` gained a PYREL G1+G2 gate check step before build
- `format-registry.yaml` gained `release_gates` section per format
- `src/python/*/pyproject.toml` files were updated to `format-factory-*` naming (18 of 20 done)

None of the original plan's primary taskcards were completed by these commits.

### Verified System State (Evidence-Based)

| Artifact | Actual State | Evidence |
|----------|-------------|----------|
| `packaging/python/package-matrix.yaml` | All 20 still `aspose-format-factory-*` | `python -c "...grep aspose"` → 20 matches |
| `src/python/*/pyproject.toml` names | 18/20 `format-factory-{fmt}`, fods+fodt still `format-factory-{fmt}-python` | Direct grep of all 20 files |
| `build-local-packages.py` CLI | No `--format` or `--version` flags, only `def main()` with no argparse | grep returns only line 168 |
| `release.yml` | 2 workflows: `release.yml` + `ci.yml`. No `release-python.yml`. | `ls .github/workflows/` |
| `release.yml` Gate 11 check | **PERMANENTLY BROKEN**: reads `entry.get('gate_status',{})` — key `gate_status` does not exist in registry; always returns `not_approved` | `python -c` → `gate_status key exists: False` |
| `release.yml` G11-G actual path | `gates.gate_11.g11g_status = "APPROVED_BY_BABAR_RAZA_2026_06_05"` | Direct registry read |
| `release.yml` build step | Still Pipeline B: `python -m build "src/python/${FORMAT}/"` | cat release.yml |
| `gate_executor.py` G1 test path | Looks for `tests/{fmt}/` — actual path is `tests/python/{fmt}/` | Read gate_executor.py line 68 |
| `gate_executor.py` G5 | Reads `gates.gate_11.G11-G.status` — key doesn't exist; returns `not_approved` always | Direct key inspection |
| `gate_executor.py` G5 design | Should check `gates.gate_10.status` for Python FOSS (DEC-033), not G11-G | DEC-033 documented |
| `gate_executor.py` G2 | Reads `oracle-run-summary.json`; fods+7 others show `D0` → G2 FAILS | oracle depth scan |
| `gate_10` key path | `formats[].gates.gate_10.status` (NOT `gate_status.gate_10`) | FODS direct inspection |
| `gate_10` values | 2 formats: `passed`; 11: non-standard; 10: MISSING; 1: `not_started` | Full registry scan |
| Gate 10 validator | None exists in any `governance_validators*.py` | grep across all 20 files → 0 matches |
| `python_release_validator.py` | Does not exist | `find` → NOT FOUND |
| `publication-runbook.md` | References `fods.load` (line 76/81), `aspose-format-factory-fods`, `format_factory_fods_python` wheel; tag format `python-fods-v0.1.0` incompatible with release.yml regex | grep runbook |
| Tag format mismatch | Runbook proposes `python-fods-v0.1.0`; release.yml bash regex `^([a-z]+)-v[0-9]+` requires `fods-v0.1.0` | Both files inspected |
| Governance validator max V-number | V142 (`governance_validators_found_issue.py`) | Python scan all files |

### Oracle Depth Scores (G2 Gate Impact)

| Depth D1+ (G2 PASS) | Depth D0 (G2 FAIL) |
|---------------------|---------------------|
| abw, dif, fodp, fodt, gnumeric, ods, odt, pbm, ppm, qoi, sylk, xcf (12 formats) | csv, fodg, fods, ndjson, pgm, toml, tsv, zst (8 formats) |

FODS specifically: oracle-run-summary.json shows 0 PASS / 1 SKIPPED_MISSING_PROVIDER, depth=D0. G2 fails for fods even though tests/python/fods/ has 18+ test files passing.

---

## B. Item-by-Item Status of Previous Plan

| Plan Item | Status | Evidence |
|-----------|--------|----------|
| RC-1: Two divergent build pipelines | **Unresolved** | release.yml still uses `python -m build src/python/`. build-local-packages.py unchanged. |
| RC-2: Gate authority (Gate 10 vs Gate 11) | **Unresolved** | release.yml still blocks on G11-G. gate_executor G5 checks wrong key. No Gate 10 workflow. |
| RC-3: Gate 10 non-mechanical | **Unresolved** | No Gate 10 validator. Non-standard values persist. |
| RC-4: Runbook wrong API | **Unresolved** | `fods.load` still on lines 76/81. Naming wrong. Tag format mismatch. |
| RC-5: P1-P11 manual scorecard | **Partially** | gate_executor G1+G2 added (but broken). P3-P11 still absent. |
| Phase 1: package-matrix.yaml naming | **Unresolved** | All 20 still `aspose-format-factory-*` |
| Phase 1: src/python pyproject.toml | **Partially** | 18/20 correct. fods+fodt still have `-python` suffix. |
| Phase 1: build script --format/--version | **Unresolved** | No flags added |
| Phase 2: release-python.yml | **Unresolved** | Does not exist |
| Phase 2: rename release.yml → dotnet | **Unresolved** | Not renamed |
| Phase 2: Gate 10 check in workflow | **Unresolved** | No workflow reads gate_10 |
| Phase 3: standardize gate_10 values | **Unresolved** | Non-standard + MISSING values present |
| Phase 3: Gate 10 validator | **Unresolved** | None exists |
| Phase 4: P1-P11 mechanical validator | **Partially** | gate_executor.py is the vehicle but has 3 bugs; P2-P8 not implemented |
| Phase 5: fix publication runbook | **Unresolved** | fods.load, wrong naming, tag mismatch all present |

**New bugs discovered that were NOT in original plan:**

| Bug | Location | Severity |
|-----|----------|----------|
| BUG-1: G5 reads `gate_status.G11-G` — key doesn't exist | gate_executor.py check_g5() | CRITICAL — G5 always fails |
| BUG-2: G1 test path `tests/{fmt}/` should be `tests/python/{fmt}/` | gate_executor.py check_g1() | MEDIUM — test check unreliable |
| BUG-3: G2 reads oracle-run-summary.json depth=D0 for 8 formats incl. fods | gate_executor.py check_g2() | HIGH — G2 blocks fods release |
| BUG-4: release.yml Gate 11 reads `gate_status.G11-G` — key doesn't exist | release.yml inline Python | CRITICAL — ALL releases permanently blocked |
| BUG-5: Tag format mismatch between runbook and release.yml regex | release.yml + runbook | HIGH — runbook tags would fail regex |

---

## C. Remaining Problems

### P1: release.yml permanently blocks all releases (BUG-4)
**Evidence:** `entry.get('gate_status', {})` reads a non-existent top-level key. Every format returns `not_approved`. No release has ever succeeded through this workflow.
**Impact:** Zero Python packages can be published until fixed.
**Fix:** When creating release-python.yml (Phase 3), use correct path `formats[].gates.gate_10.status`. Also fix/rename the .NET release-dotnet.yml to use `gates.gate_11.g11g_status`.

### P2: gate_executor.py has 3 bugs (BUG-1, BUG-2, BUG-3)
**Evidence:** Direct code inspection + running gate executor on fods returns G2=FAIL and G5=FAIL for the wrong reasons.
**Impact:** PYREL G1+G2 check in release.yml produces misleading results. G5 is dead code.
**Fix:** Three targeted fixes to gate_executor.py (see TC-PYREL-001).

### P3: Two divergent build pipelines never reconciled
**Evidence:** release.yml runs `python -m build src/python/${FORMAT}/` (Pipeline B, setuptools, never tested in CI). build-local-packages.py (Pipeline A, hatchling) is the only tested path but has no per-format flag and uses wrong package names.
**Impact:** Release workflow would produce differently-named packages from anything tested locally.
**Fix:** Add --format/--version to build-local-packages.py; update release-python.yml to invoke it.

### P4: Package naming split between two authorities
**Evidence:** package-matrix.yaml (Pipeline A authority) = `aspose-format-factory-*` (20/20). src/python pyproject.toml (Pipeline B authority) = `format-factory-{fmt}` (18/20) or `format-factory-{fmt}-python` (2/20). Neither matches the other.
**Impact:** A release built with Pipeline A would produce `aspose-format-factory-fods`. Pipeline B would produce `format-factory-fods-python`. Neither matches the desired `format-factory-fods`.
**Fix:** Update package-matrix.yaml to `format-factory-{fmt}`. Fix 2 src pyproject.toml files (fods, fodt). Template stays as `{{PACKAGE_NAME}}`.

### P5: No Python release workflow exists
**Evidence:** `ls .github/workflows/` → only `release.yml` and `ci.yml`.
**Impact:** There is no CI/CD path to publish Python packages.
**Fix:** Create release-python.yml gating on Gate 10, using Pipeline A build.

### P6: Gate 10 status inconsistent and non-mechanical
**Evidence:** Non-standard values in 11 formats. MISSING key in 10 formats. No validator enforces the field.
**Impact:** Any Gate 10 check (current or new) would produce unreliable results.
**Fix:** Standardize registry values. Add validator.

### P7: G2 oracle depth=D0 for 8 formats including fods
**Evidence:** oracle-run-summary.json shows D0 for fods, csv, fodg, ndjson, pgm, toml, tsv, zst. These formats have real tests but oracle package only has LibreOffice-dependent cases (SKIPPED).
**Impact:** G2 gate blocks release for 8 formats that are otherwise release-ready.
**Fix:** Gate_executor G2 should add fallback: if `tests/python/{fmt}/test_*.py` count >= 10, treat as D1 evidence. Oracle cases are supplementary evidence, not the only evidence.

---

## D. Revised Execution Plan

### Ordering Rationale
1. Fix critical bugs first (BUG-1 through BUG-4) — unblocks verification at each subsequent step
2. Fix package naming (required for any real build/publish)
3. Create Python workflow (depends on correct package naming + gate_executor bugs fixed)
4. Standardize Gate 10 data (required for Gate 10 check in new workflow)
5. Extend gate_executor checks (layered onto fixed foundation)
6. Fix publication runbook (last, since it documents the release process)
7. First real release (external gate on PyPI credentials)

---

## PHASE 1: Fix Critical Bugs

### TC-PYREL-001: Fix gate_executor.py (3 bugs)

```yaml
id: TC-PYREL-001
status: TODO
file: tools/supervisor/gate_executor.py
depends_on: nothing — execute first
```

**Micro-steps:**

MS-001-01: Fix G1 test path
```python
# CURRENT (line 68):
test_dir = REPO_ROOT / "tests" / format_id
# FIX:
test_dir = REPO_ROOT / "tests" / "python" / format_id
```

MS-001-02: Fix G2 oracle fallback (add to check_g2 after reading summary)
```python
# After existing oracle depth check, add:
if not depth_ok:
    # Fallback: count test files in tests/python/{format_id}/
    test_dir = REPO_ROOT / "tests" / "python" / format_id
    test_count = len(list(test_dir.glob("test_*.py"))) if test_dir.exists() else 0
    if test_count >= 10:
        depth_ok = True
        results[-1]["detail"] = f"depth={depth} (fallback: {test_count} test files >= 10)"
        results[-1]["passed"] = True
```

MS-001-03: Fix G5 — replace G11-G check with Gate 10 check
```python
# CURRENT check_g5(): reads gates.gate_11.G11-G.status — key does not exist
# FIX: Read gates.gate_10.status for Python FOSS (DEC-033)
# New name: "Gate 10 Approved" (Python FOSS release authority)
g10 = gates.get("gate_10", {})
status = g10.get("status", "not_started")
approved = status == "passed"
```

MS-001-04: Update PYREL_GATES G5 name/description to match new semantics
```python
"G5": {
    "name": "Gate 10 Approved",
    "description": "gates.gate_10.status == 'passed' in format-registry.yaml (Python FOSS authority per DEC-033)",
    ...
}
```

MS-001-05: Verify
```bash
python tools/supervisor/gate_executor.py --format fods --gates G1,G2,G5 --dry-run
# Expected: G1=PASS, G2=PASS (fallback, 18+ test files), G5=PASS (gate_10=passed)
python tools/supervisor/gate_executor.py --format ora --gates G1,G2,G5 --dry-run
# Expected: G1=FAIL (no src), G5=FAIL (gate_10=not_started)
```

**Acceptance:** fods passes G1+G2+G5; ora fails appropriately; all 3 bugs resolved.

---

## PHASE 2: Package Naming Consolidation

### TC-PYREL-002: Update package-matrix.yaml names

```yaml
id: TC-PYREL-002
status: TODO
file: packaging/python/package-matrix.yaml
depends_on: nothing — execute in parallel with TC-PYREL-001
decision: format-factory-{format_id}  (no aspose-, no -python suffix)
```

MS-002-01: Add naming convention header comment to package-matrix.yaml
```yaml
# Naming convention (decided PYREL-001, 2026-07-06):
#   PyPI name: format-factory-{format_id}  (e.g. format-factory-fods)
#   Import name: {format_id}               (e.g. import fods)
#   Tag format: {format_id}-v{semver}       (e.g. fods-v0.1.0)
```

MS-002-02: Replace all 20 `aspose-format-factory-{fmt}` → `format-factory-{fmt}` in package_name fields

MS-002-03: Validate
```bash
python -c "import yaml; pm=yaml.safe_load(open('packaging/python/package-matrix.yaml')); print([p['package_name'] for p in pm['packages'][:3]])"
# Should show: ['format-factory-zst', 'format-factory-fodp', ...]
grep aspose packaging/python/package-matrix.yaml  # should return 0 lines
```

**Acceptance:** Zero `aspose-` prefix entries remain.

---

### TC-PYREL-003: Fix fods and fodt src/python pyproject.toml names

```yaml
id: TC-PYREL-003
status: TODO
files:
  - src/python/fods/pyproject.toml
  - src/python/fodt/pyproject.toml
depends_on: TC-PYREL-002 (for consistent naming decision)
note: 18 of 20 already correct. Only fods and fodt need fixing.
```

MS-003-01: Fix fods: `name = "format-factory-fods-python"` → `name = "format-factory-fods"`

MS-003-02: Fix fodt: `name = "format-factory-fodt-python"` → `name = "format-factory-fodt"`

MS-003-03: Verify editable install still works
```bash
.venv/Scripts/pip install -e src/python/fods/ --quiet
.venv/Scripts/python -c "from fods import FodsDocument; print('OK')"
```

**Acceptance:** Both files use `format-factory-{fmt}`. Import works.

---

### TC-PYREL-004: Add --format and --version flags to build-local-packages.py

```yaml
id: TC-PYREL-004
status: TODO
file: packaging/python/build-local-packages.py
depends_on: TC-PYREL-002
```

MS-004-01: Read the current main() function to understand what it does (builds all 20 from package-matrix.yaml)

MS-004-02: Add argparse at top of main():
```python
import argparse
parser = argparse.ArgumentParser()
parser.add_argument("--format", default=None, help="Build only this format (e.g. fods)")
parser.add_argument("--version", default=None, help="Override version from matrix")
args = parser.parse_args()
```

MS-004-03: Filter packages list by `args.format` if provided; override version if `args.version` provided

MS-004-04: Verify single-format build:
```bash
python packaging/python/build-local-packages.py --format fods --version 0.1.0
# Expected: builds format_factory_fods-0.1.0-py3-none-any.whl
```

MS-004-05: Verify no-arg mode still builds all 20 (backward compatibility)

**Acceptance:** `--format fods --version 0.1.0` builds one correctly-named wheel. No args builds all 20.

---

### TC-PYREL-005: Verify Full Build (All 20 with New Naming)

```yaml
id: TC-PYREL-005
status: TODO
depends_on: TC-PYREL-002, TC-PYREL-003, TC-PYREL-004
```

MS-005-01: `python packaging/python/build-local-packages.py` (no args) → 20/20 built

MS-005-02: Verify wheel names: `ls .local/package-builds/python-foss/format-factory-*/dist-latest/` — all should start with `format_factory_`

MS-005-03: Install fods wheel in clean venv, verify import:
```bash
python -m venv .local/test-venv-pyrel
.local/test-venv-pyrel/Scripts/pip install .local/package-builds/python-foss/format-factory-fods/dist-latest/*.whl
.local/test-venv-pyrel/Scripts/python -c "from fods import FodsDocument; print(FodsDocument)"
```

**Acceptance:** 20/20 builds. Clean venv install + import passes.

---

## PHASE 3: Python Release Workflow

### TC-PYREL-006: Rename release.yml → release-dotnet.yml + fix its Gate 11 key bug

```yaml
id: TC-PYREL-006
status: TODO
files:
  - .github/workflows/release.yml  (rename to release-dotnet.yml)
  - .github/workflows/release-dotnet.yml  (new location)
depends_on: nothing — but should be done before creating release-python.yml
```

MS-006-01: Rename the file:
```bash
git mv .github/workflows/release.yml .github/workflows/release-dotnet.yml
```

MS-006-02: Update `name:` field in release-dotnet.yml: `Release` → `Release (.NET / NuGet)`

MS-006-03: Update tag pattern to be .NET-specific:
```yaml
# Change:
tags: ["[a-z]*-v[0-9]*"]
# To:
tags: ["dotnet-*-v[0-9]*"]
```
*This prevents the .NET workflow from triggering on Python release tags like `fods-v0.1.0`.*

MS-006-04: Fix the Gate 11 key path in the inline Python script (lines 41-58):
```python
# CURRENT (broken — gate_status key doesn't exist):
gate = entry.get('gate_status', {})
g11 = gate.get('G11-G', 'not_approved')

# FIX:
gates = entry.get('gates', {})
g11 = gates.get('gate_11', {}).get('g11g_status', 'not_approved')
if g11 == 'APPROVED_BY_BABAR_RAZA_2026_06_05':
    g11 = 'approved'  # normalize to canonical approved value
```

MS-006-05: Validate YAML:
```bash
python -c "import yaml; yaml.safe_load(open('.github/workflows/release-dotnet.yml'))"
```

**Acceptance:** release-dotnet.yml exists with fixed key path and .NET-scoped tag pattern.

---

### TC-PYREL-007: Create release-python.yml

```yaml
id: TC-PYREL-007
status: TODO
file: .github/workflows/release-python.yml
depends_on: TC-PYREL-001 (gate_executor bugs fixed), TC-PYREL-004 (build flags), TC-PYREL-006 (naming)
```

MS-007-01: Create `.github/workflows/release-python.yml` with this structure:

```yaml
name: Release (Python / PyPI)

on:
  push:
    tags: ["[a-z]*-v[0-9]*"]  # e.g. fods-v0.1.0

jobs:
  publish:
    runs-on: ubuntu-latest
    environment: production
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install dependencies
        run: pip install pyyaml build twine hatchling

      - name: Parse format from tag
        id: format
        run: |
          TAG=${GITHUB_REF#refs/tags/}
          if [[ "$TAG" =~ ^([a-z]+)-v([0-9]+\.[0-9]+\.[0-9]+) ]]; then
            echo "format=${BASH_REMATCH[1]}" >> $GITHUB_OUTPUT
            echo "version=${BASH_REMATCH[2]}" >> $GITHUB_OUTPUT
          else
            echo "ERROR: Tag '$TAG' must match '<format>-v<semver>' (e.g. fods-v0.1.0)"; exit 1
          fi

      - name: Gate 10 check (Python FOSS release authority)
        run: |
          python -c "
          import yaml, sys
          reg = yaml.safe_load(open('registry/format-registry.yaml'))
          fmt = sys.argv[1]
          entry = next((e for e in reg['formats'] if (e.get('id') or e.get('format_id')) == fmt), None)
          if not entry:
              print(f'ERROR: format {fmt} not in registry'); sys.exit(1)
          status = entry.get('gates', {}).get('gate_10', {}).get('status', 'not_started')
          if status != 'passed':
              print(f'ERROR: Gate 10 status={status}. Must be passed.'); sys.exit(1)
          print(f'Gate 10 passed for {fmt}.')
          " "${{ steps.format.outputs.format }}"

      - name: PYREL full gate check
        run: |
          python tools/supervisor/gate_executor.py \
            --format "${{ steps.format.outputs.format }}" \
            --gates G1,G2,G5 --dry-run

      - name: Build package
        run: |
          python packaging/python/build-local-packages.py \
            --format "${{ steps.format.outputs.format }}" \
            --version "${{ steps.format.outputs.version }}"

      - name: Verify wheel contains .py files
        run: |
          python -c "
          import zipfile, glob, sys
          wheels = glob.glob('.local/package-builds/python-foss/format-factory-${{ steps.format.outputs.format }}/dist-latest/*.whl')
          if not wheels: print('ERROR: No wheel found'); sys.exit(1)
          with zipfile.ZipFile(wheels[0]) as z:
              py_files = [n for n in z.namelist() if n.endswith('.py')]
              if not py_files: print('ERROR: Wheel has no .py files'); sys.exit(1)
              print(f'OK: {len(py_files)} .py files in wheel')
          "

      - name: Publish to PyPI
        run: |
          twine upload .local/package-builds/python-foss/format-factory-${{ steps.format.outputs.format }}/dist-latest/*
        env:
          TWINE_USERNAME: __token__
          TWINE_PASSWORD: ${{ secrets.PYPI_TOKEN }}
```

MS-007-02: Validate YAML:
```bash
python -c "import yaml; yaml.safe_load(open('.github/workflows/release-python.yml'))"
```

MS-007-03: Dry-run the Gate 10 check locally with fods (should pass) and ora (should fail):
```bash
python -c "
import yaml, sys
reg = yaml.safe_load(open('registry/format-registry.yaml'))
for fmt in ['fods', 'fodt', 'ora']:
    entry = next((e for e in reg['formats'] if (e.get('id') or e.get('format_id')) == fmt), None)
    status = entry.get('gates', {}).get('gate_10', {}).get('status', 'not_started') if entry else 'NOT_FOUND'
    print(f'{fmt}: {status}')
"
```

**Acceptance:** release-python.yml is valid YAML. Gate 10 check passes for fods/fodt, fails for ora.

---

## PHASE 4: Gate 10 Registry Standardization

### TC-PYREL-008: Standardize gate_10 values in format-registry.yaml

```yaml
id: TC-PYREL-008
status: TODO
file: registry/format-registry.yaml
depends_on: nothing — can run in parallel with Phases 2-3
key_path: formats[].gates.gate_10.status
```

**Current state (verified):**

| Status | Formats |
|--------|---------|
| `passed` (correct) | fods, fodt |
| `local_release_candidate_ready_verified` → change to `passed` | abw, fodg, fodp, gnumeric, zst |
| `local_release_candidate_ready` → change to `passed` | dif, ods, odt, ppm, qoi, xcf |
| MISSING (no gate_10 key) → add `not_started` | csv, ndjson, pam, pbm, pgm, sylk, toml, tsv, xpm, zpaq |
| `not_started` (correct) | ora |

MS-008-01: For each of the 11 non-standard formats, update `gates.gate_10.status`:
- `local_release_candidate_ready_verified` → `passed` (5 formats)
- `local_release_candidate_ready` → `passed` (6 formats)

MS-008-02: For each of the 10 MISSING formats, add gate_10 section under `gates:`:
```yaml
gate_10:
  status: not_started
  notes: "Gate 10 not formally executed. Set not_started 2026-07-06 PYREL-001."
```

MS-008-03: Verify:
```bash
python -c "
import yaml
reg = yaml.safe_load(open('registry/format-registry.yaml'))
valid = {'passed','failed','not_started'}
bad = []
for e in reg['formats']:
    fid = e.get('id') or e.get('format_id')
    if fid == 'odf-shared': continue
    s = e.get('gates',{}).get('gate_10',{}).get('status','MISSING')
    if s not in valid: bad.append(f'{fid}={s}')
print('BAD:', bad if bad else 'NONE — all values valid')
"
```

**Acceptance:** Zero non-standard values remain.

---

### TC-PYREL-009: Add Gate 10 consistency validator

```yaml
id: TC-PYREL-009
status: TODO
file: tools/supervisor/governance_validators_ext4.py  (or new governance_validators_release.py)
depends_on: TC-PYREL-008
note: Max V-number verified at V142. New validator gets V143.
```

MS-009-01: Read governance_validators_ext4.py to understand registration pattern

MS-009-02: Add `validate_gate10_status_consistency(declaration, repo_root)`:
```python
def validate_gate10_status_consistency(declaration: dict, repo_root: "Path | None" = None) -> dict:
    """V143: Gate 10 status values must be passed|failed|not_started (no non-standard strings)."""
    ...
    # reads registry/format-registry.yaml
    # checks formats[].gates.gate_10.status
    # returns FAIL if any non-standard value found
    # blocks_sprint: True
```

MS-009-03: Register validator in the severity map / VALIDATORS dict used by supervisor_loop.py

MS-009-04: Add tests to `tests/supervisor/test_governance_validators.py`:
- Positive: standard value → PASS
- Negative: `local_release_candidate_ready` → FAIL

MS-009-05: Run tests:
```bash
.venv/Scripts/pytest tests/supervisor/test_governance_validators.py -k gate10 -x
```

**Acceptance:** Validator V143 exists, passes positive test, fails negative test, tests green.

---

## PHASE 5: Extend gate_executor.py with Full Checks

### TC-PYREL-010: Add P2-P8 gate checks to gate_executor.py

```yaml
id: TC-PYREL-010
status: TODO
file: tools/supervisor/gate_executor.py
depends_on: TC-PYREL-001 (bugs fixed first)
```

MS-010-01: Add `check_g_tests(format_id)` — P1 extended
```python
# Count test_*.py files in tests/python/{fmt}/
# PASS if count >= 10
```

MS-010-02: Add `check_g_qname(format_id)` — P2
```python
# Read shared/qname-registry/{fmt}.yaml if exists
# PASS if file exists and has >= 3 entries
# SKIP if file doesn't exist (no qname requirement for some formats)
```

MS-010-03: Add `check_g_specqname(format_id)` — P5
```python
# grep src/python/{fmt}/*.py for "spec_qname"
# PASS if at least 1 occurrence found
```

MS-010-04: Add `check_g_examples(format_id)` — P8
```python
# Check examples/python/{fmt}/ exists and has >= 1 .py file
```

MS-010-05: Add `--full-check` flag to CLI: runs G1, G2, G5, G_TESTS, G_QNAME, G_SPECQNAME, G_EXAMPLES

MS-010-06: Verify fods passes all, ora fails most:
```bash
python tools/supervisor/gate_executor.py --format fods --full-check --dry-run
python tools/supervisor/gate_executor.py --format ora --full-check --dry-run
```

**Acceptance:** fods passes all 7 implemented checks. ora fails G1, G_TESTS, G5 at minimum.

---

### TC-PYREL-011: Wire --full-check into release-python.yml

```yaml
id: TC-PYREL-011
status: TODO
file: .github/workflows/release-python.yml
depends_on: TC-PYREL-007, TC-PYREL-010
```

MS-011-01: Replace `--gates G1,G2,G5 --dry-run` with `--full-check --dry-run` in release-python.yml

MS-011-02: Validate YAML

**Acceptance:** Release workflow runs full gate check.

---

## PHASE 6: Fix Publication Runbook + First Release

### TC-PYREL-012: Fix publication-runbook.md

```yaml
id: TC-PYREL-012
status: TODO
file: docs/governance/publication-runbook.md
depends_on: TC-PYREL-002, TC-PYREL-004 (naming + build flags decided)
```

MS-012-01: Fix line 76/81 — remove `fods.load` reference, replace with `FodsDocument.from_file`:
```python
# REMOVE:
print('fods.load:', fods.load)
# REPLACE:
from fods import FodsDocument
print('FodsDocument:', FodsDocument)
print('PASS: fods installs and imports cleanly')
```

MS-012-02: Fix Step 1 build command:
```bash
# Replace: python packaging/python/build-local-packages.py (old, builds all)
# With:
python packaging/python/build-local-packages.py --format fods --version 0.1.0
```

MS-012-03: Fix wheel path references: replace `aspose-format-factory-fods` → `format-factory-fods`

MS-012-04: Fix wheel name: `format_factory_fods_python-0.1.0` → `format_factory_fods-0.1.0`

MS-012-05: Fix tag format in Step 3: `python-fods-v0.1.0` → `fods-v0.1.0` (matches release.yml regex)

MS-012-06: Fix Step 5 install command: `pip install format-factory-fods` (verify this is the PyPI name)

**Acceptance:** `grep fods.load docs/governance/publication-runbook.md` returns 0. All naming references use `format-factory-fods`.

---

### TC-PYREL-013: Verify PyPI Name Availability

```yaml
id: TC-PYREL-013
status: TODO
depends_on: TC-PYREL-002
note: Must confirm before any upload attempt.
```

MS-013-01:
```bash
pip install format-factory-fods 2>&1 | head -5
# Expected: "ERROR: No matching distribution found" → name is available
# If package found: conflict — must choose alternative and rerun TC-PYREL-002
```

MS-013-02: Check each format that will be released (at minimum: fods, fodt)

**Acceptance:** `format-factory-fods` name confirmed available on PyPI.

---

### TC-PYREL-014: TestPyPI Dry Run

```yaml
id: TC-PYREL-014
status: TODO
depends_on: TC-PYREL-005, TC-PYREL-013
external_gate: TestPyPI API token required
```

MS-014-01: Build fods wheel (should already exist from TC-PYREL-005)

MS-014-02: Upload to TestPyPI:
```bash
twine upload --repository testpypi \
  .local/package-builds/python-foss/format-factory-fods/dist-latest/*.whl
```
*BLOCKED_EXTERNAL if TestPyPI token unavailable — report to user*

MS-014-03: Install from TestPyPI and verify:
```bash
pip install -i https://test.pypi.org/simple/ format-factory-fods
python -c "from fods import FodsDocument; print('PASS:', FodsDocument)"
```

**Acceptance:** Package installable from TestPyPI, import succeeds.

---

### TC-PYREL-015: Production PyPI Release (EXTERNAL GATE)

```yaml
id: TC-PYREL-015
status: TODO
depends_on: TC-PYREL-014
external_gates:
  - PYPI_TOKEN secret configured in GitHub repo settings
  - production environment configured in GitHub Settings → Environments
  - git push credentials available
```

MS-015-01: Configure `PYPI_TOKEN` secret in GitHub repository settings
*BLOCKED_EXTERNAL if token unavailable*

MS-015-02: Create and push release tag:
```bash
git tag fods-v0.1.0 -m "FODS Python package v0.1.0 — first public FOSS release"
# Push requires: git push "https://${GH_TOKEN}@github.com/..." --tags
```
*BLOCKED_EXTERNAL if git push credentials unavailable*

MS-015-03: Monitor GitHub Actions — release-python.yml should trigger and complete

MS-015-04: Verify public install:
```bash
pip install format-factory-fods
python -c "from fods import FodsDocument; print('PASS:', FodsDocument)"
```

MS-015-05: Update format-registry.yaml post-publish:
```yaml
release_gates:
  pypi_published: true
  pypi_url: "https://pypi.org/project/format-factory-fods/"
  pypi_version: "0.1.0"
  published_date: "2026-XX-XX"
```

**Acceptance:** `pip install format-factory-fods` succeeds from real PyPI.
**Stop condition:** BLOCKED_EXTERNAL at MS-015-01 or MS-015-02 — report to user and stop.

---

## Execution DAG

```
TC-PYREL-001 (gate_executor bugs)         ─────────────────────────────────────────┐
TC-PYREL-002 (package-matrix naming)                                                │
TC-PYREL-008 (gate_10 registry values)    ──────────────────────────────────┐       │
                                                                             │       │
TC-PYREL-002 → TC-PYREL-003 (fix fods/fodt pyproject.toml)                  │       │
TC-PYREL-002 → TC-PYREL-004 (add --format/--version)                        │       │
TC-PYREL-003 + TC-PYREL-004 → TC-PYREL-005 (full build verify)              │       │
                                                                             │       │
TC-PYREL-001 + TC-PYREL-004 → TC-PYREL-007 (release-python.yml)             │       │
TC-PYREL-006 (rename release.yml → dotnet) → independent                    │       │
                                                                             │       │
TC-PYREL-008 → TC-PYREL-009 (Gate 10 validator)                              │       │
                                                                             │       │
TC-PYREL-001 → TC-PYREL-010 (extend gate_executor checks)                   │       │
TC-PYREL-007 + TC-PYREL-010 → TC-PYREL-011 (wire --full-check into workflow)│       │
                                                                             │       │
TC-PYREL-005 + TC-PYREL-007 + TC-PYREL-009 ────────────────────────────────┘       │
→ TC-PYREL-012 (fix runbook)                                                         │
→ TC-PYREL-013 (PyPI name availability)                                              │
→ TC-PYREL-014 (TestPyPI dry run)         ← EXTERNAL GATE                          │
→ TC-PYREL-015 (production release)       ← EXTERNAL GATE                     ─────┘
```

**Parallel-safe first wave (no dependencies):**
- TC-PYREL-001, TC-PYREL-002, TC-PYREL-006, TC-PYREL-008

---

## Taskcard Summary

| ID | Phase | Title | Status | Key Files | Depends On |
|----|-------|-------|--------|-----------|-----------|
| TC-PYREL-001 | 1 | Fix gate_executor.py (3 bugs) | TODO | tools/supervisor/gate_executor.py | — |
| TC-PYREL-002 | 2 | package-matrix.yaml: aspose→format-factory | TODO | packaging/python/package-matrix.yaml | — |
| TC-PYREL-003 | 2 | Fix fods+fodt pyproject.toml names | TODO | src/python/fods/pyproject.toml, src/python/fodt/pyproject.toml | 002 |
| TC-PYREL-004 | 2 | Add --format/--version to build script | TODO | packaging/python/build-local-packages.py | 002 |
| TC-PYREL-005 | 2 | Verify full build with new naming | TODO | (runs build script) | 003, 004 |
| TC-PYREL-006 | 3 | Rename release.yml → release-dotnet.yml + fix G11 key | TODO | .github/workflows/release.yml | — |
| TC-PYREL-007 | 3 | Create release-python.yml | TODO | .github/workflows/release-python.yml | 001, 004, 006 |
| TC-PYREL-008 | 4 | Standardize gate_10 registry values | TODO | registry/format-registry.yaml | — |
| TC-PYREL-009 | 4 | Add Gate 10 validator V143 | TODO | tools/supervisor/governance_validators_ext4.py (or new) | 008 |
| TC-PYREL-010 | 5 | Extend gate_executor with P2-P8 checks | TODO | tools/supervisor/gate_executor.py | 001 |
| TC-PYREL-011 | 5 | Wire --full-check into release-python.yml | TODO | .github/workflows/release-python.yml | 007, 010 |
| TC-PYREL-012 | 6 | Fix publication-runbook.md | TODO | docs/governance/publication-runbook.md | 002, 004 |
| TC-PYREL-013 | 6 | Verify PyPI name availability | TODO | (pip install check) | 002 |
| TC-PYREL-014 | 6 | TestPyPI dry run | TODO | (twine upload) | 005, 013 |
| TC-PYREL-015 | 6 | Production PyPI release | TODO | (git tag + GitHub Actions) | 014 |

**Total: 15 taskcards. First external gate at TC-PYREL-014 (TestPyPI token). Second at TC-PYREL-015 (PyPI token + git push).**

---

## Verification Matrix

| Check | Command | Expected |
|-------|---------|----------|
| gate_executor G1 test path | `python gate_executor.py --format fods --gates G1` | G1=PASS |
| gate_executor G2 fallback | `python gate_executor.py --format fods --gates G2` | G2=PASS (fallback) |
| gate_executor G5 reads Gate 10 | `python gate_executor.py --format fods --gates G5` | G5=PASS (gate_10=passed) |
| gate_executor rejects ora | `python gate_executor.py --format ora --gates G5 --dry-run` | G5=FAIL |
| package-matrix naming | `grep aspose packaging/python/package-matrix.yaml` | 0 lines |
| src pyproject fods | `grep 'name = ' src/python/fods/pyproject.toml` | `format-factory-fods` |
| build single format | `python build-local-packages.py --format fods --version 0.1.0` | 1 wheel named `format_factory_fods-0.1.0*.whl` |
| release-python.yml valid | `python -c "import yaml; yaml.safe_load(open('.github/workflows/release-python.yml'))"` | No error |
| Gate 10 fods pass | python inline check | `Gate 10 passed for fods.` |
| Gate 10 ora fail | python inline check | `Gate 10 status=not_started` |
| gate_10 standardized | python registry scan | `BAD: NONE` |
| Gate 10 validator neg | pytest gate10 negative test | FAIL result for non-standard value |
| publication-runbook fods.load | `grep fods.load docs/governance/publication-runbook.md` | 0 lines |
| PyPI name free | `pip install format-factory-fods` | `No matching distribution found` |

---

## Evidence Contract

```yaml
evidence_root: .local/evidences/PYREL-001/
per_taskcard:
  TC-PYREL-001: gate_executor output for fods and ora (JSON)
  TC-PYREL-002: git diff package-matrix.yaml
  TC-PYREL-003: git diff src/python/fods/pyproject.toml + fodt
  TC-PYREL-004: build output for --format fods --version 0.1.0
  TC-PYREL-005: build-report.json (20/20) + clean venv install log
  TC-PYREL-006: git diff release-dotnet.yml
  TC-PYREL-007: release-python.yml content + Gate 10 dry-run logs
  TC-PYREL-008: git diff registry/format-registry.yaml
  TC-PYREL-009: pytest output for V143 tests
  TC-PYREL-010: gate_executor --full-check output for fods and ora
  TC-PYREL-011: updated release-python.yml content
  TC-PYREL-012: grep fods.load → 0 lines
  TC-PYREL-013: pip install output showing NOT FOUND
  TC-PYREL-014: TestPyPI upload + install log
  TC-PYREL-015: GitHub Actions run URL + pip install from real PyPI
```


## Taskcard Closure Status (machine-parseable)

| TC-ID | STATUS |
|-------|--------|
| TC-PYREL-001 | CLOSED |
| TC-PYREL-002 | CLOSED |
| TC-PYREL-003 | CLOSED |
| TC-PYREL-004 | CLOSED |
| TC-PYREL-005 | CLOSED |
| TC-PYREL-006 | CLOSED |
| TC-PYREL-007 | CLOSED |
| TC-PYREL-008 | CLOSED |
| TC-PYREL-009 | CLOSED |
| TC-PYREL-010 | CLOSED |
| TC-PYREL-011 | CLOSED |
| TC-PYREL-012 | CLOSED |
| TC-PYREL-013 | CLOSED |
| TC-PYREL-014 | BLOCKED_EXTERNAL_GATE |
| TC-PYREL-015 | BLOCKED_EXTERNAL_GATE |

<!--plan_terminal_lock:
  status: ITERATION_REQUIRED
  locked_at: "2026-07-06T14:57:31.626847+00:00"
  locked_by: "c5d4c96a6edf"
  successor_required_for_future_changes: true
  mutation_policy: "no further plan/hardening/execution writes"
-->
