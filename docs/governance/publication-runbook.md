# Format Factory — Package Publication Runbook
# Taskcard: TC-HARD-010
# Created: 2026-06-21
# Authority: TC-HARD-010 (polished-hopping-glacier.md H5)

---

## 1. Purpose

This runbook documents the complete sequence for publishing a Format Factory Python package
to PyPI. It identifies every step, whether the step is agent-owned or human-gated, and
classifies all credential and authorization requirements.

The first target is FODS (format-factory-fods). The sequence is generic and applies
to all 20 Python packages.

---

## 2. Prerequisites

Before starting the publication sequence, verify all of the following:

| Pre-condition | Check | Who Verifies |
|--------------|-------|-------------|
| Gate 11 G11-G approved | `poc-targets.yaml gate_11_g11g: approved` | Agent |
| customer-readiness-checklist.md met | All 8 criteria checked | Agent (verifies) + Babar Raza (approves) |
| Tests passing (all format tests) | `pytest tests/python/fods/ -x` → 0 failures | Agent |
| Source structure violations none | `source_structure_validator.py` clean | Agent |
| Wheel built with source files | `zipfile.ZipFile(whl).namelist()` includes `.py` files | Agent |
| Version is release-ready | No `.dev0`/`.dev`/`.alpha`/`.beta` suffix in version string | Agent |
| CHANGELOG.md entry prepared | `src/python/{format}/CHANGELOG.md` exists with release entry | Agent |
| PyPI API token available | Token configured in env or `~/.pypirc` | **HUMAN GATE** |

---

## 3. Full Publication Sequence

### Step 1 — Build (Agent-Owned)

```bash
# From repo root — builds format-factory-fods v0.1.0 wheel in dist-latest/
python packaging/python/build-local-packages.py --format fods --version 0.1.0
```

**Verify wheel is non-empty:**
```python
import zipfile
with zipfile.ZipFile('.local/package-builds/python-foss/format-factory-fods/dist-latest/format_factory_fods-0.1.0-py3-none-any.whl') as z:
    names = z.namelist()
    py_files = [n for n in names if n.endswith('.py')]
    assert len(py_files) > 0, f"FAIL: wheel has no .py files. Contents: {names}"
    print(f"PASS: wheel contains {len(py_files)} .py files")
```

**Authorization:** Agent-owned. No human authorization required.

---

### Step 2 — Install and Test in Clean Virtualenv (Agent-Owned)

```bash
# Create isolated test environment
python -m venv .local/pub-test-venv
.local/pub-test-venv/Scripts/pip install .local/package-builds/python-foss/format-factory-fods/dist-latest/format_factory_fods-0.1.0-py3-none-any.whl

# Run smoke test
.local/pub-test-venv/Scripts/python -c "
from fods import FodsDocument
print('FodsDocument:', FodsDocument)
print('PASS: fods installs and imports cleanly')
"
```

**Accept criteria:** Import succeeds, `FodsDocument` is importable, no import errors.

**Authorization:** Agent-owned.

---

### Step 3 — Version Tag (Agent-Preparable / Human-Authorized for Push)

```bash
# Agent creates tag locally (tag format must match release-python.yml regex: [a-z]*-v[0-9]*)
git tag fods-v0.1.0 -m "FODS Python package v0.1.0 — first public release"

# Push requires human authorization (branch protection + credentials)
# EXTERNAL_GATE: git push --tags
```

**Agent action:** Create local tag.
**Human action required:** `git push --tags` (requires git push credentials + explicit authorization).

---

### Step 4 — Upload to PyPI (TRUE EXTERNAL GATE)

```bash
# Using twine (recommended):
pip install twine
twine upload \
  .local/package-builds/python-foss/format-factory-fods/dist-latest/format_factory_fods-0.1.0-py3-none-any.whl

# OR using poetry (if project uses poetry):
cd src/python/fods
poetry publish
```

**EXTERNAL_GATE: pypi_credentials_unavailable**

Required credential: PyPI API token
- How to obtain: https://pypi.org/manage/account/token/
- How to configure: set `TWINE_PASSWORD=pypi-<token>` and `TWINE_USERNAME=__token__`
- OR: add to `~/.pypirc`:
  ```
  [pypi]
  username = __token__
  password = pypi-<token>
  ```

**Who authorizes:** User / Babar Raza (explicit authorization required per session).

---

### Step 5 — Verify Public Installation (Agent-Owned, after upload)

```bash
# In a completely clean environment (no local packages):
pip install format-factory-fods

# Smoke test:
python -c "import fods; print('PASS:', fods.__version__)"
```

**This step confirms** the package is publicly installable from PyPI, not just locally.

---

### Step 6 — Update Registry (Agent-Owned)

After confirmed PyPI publication:

1. Update `product-capability-matrix/poc-targets.yaml`:
   ```yaml
   commercial_product_ready: true
   commercial_product_ready_date: "2026-XX-XX"
   pypi_url: "https://pypi.org/project/format-factory-fods/"
   ```

2. Update `packaging/python/package-matrix.yaml`:
   ```yaml
   publish_status: published
   pypi_url: https://pypi.org/project/format-factory-fods/
   publish_date: "2026-XX-XX"
   ```

3. Write evidence declaration confirming all steps complete.

---

### Step 7 — Final Sign-Off (TRUE EXTERNAL GATE)

After publication confirmed:
- **Babar Raza** reviews the published package on PyPI
- Approves `commercial_product_ready: true` in `poc-targets.yaml`
- This is the final commercial release gate (Gate 11 G11-G execution complete)

---

## 4. Credential Requirements Summary

| Credential | Purpose | Status | Resolution |
|-----------|---------|--------|------------|
| PyPI API token | Upload to pypi.org | **UNAVAILABLE** | Human obtains from pypi.org/manage/account |
| Git push credentials | Push version tags to remote | **UNAVAILABLE** | User authorizes per-session |
| Babar Raza sign-off | Final commercial release approval | **EXTERNAL GATE** | Business decision, cannot be automated |

---

## 5. Steps That Can Be Automated vs. Require Human Authorization

| Step | Automatable? | Notes |
|------|-------------|-------|
| Build wheel | YES | `build-local-packages.py` or `python -m build` |
| Run tests | YES | `pytest tests/python/fods/` |
| Install from wheel (local) | YES | `pip install <whl>` in virtualenv |
| Create local git tag | YES | `git tag fods-v0.1.0` |
| Upload to PyPI | NO | Requires PyPI token |
| Push git tag | NO | Requires git push credentials + authorization |
| Verify public install from PyPI | YES (after upload) | `pip install format-factory-fods` |
| Update registry files | YES | Agent writes YAML updates |
| Babar Raza final approval | NO | Business decision |

---

## 6. Failure Modes and Recovery

| Failure | Recovery |
|---------|---------|
| Wheel build fails (empty wheel) | Fix `pyproject.toml` package discovery; ensure `find: where: src/python/fods` points to correct location |
| `twine upload` authentication failure | Check `TWINE_USERNAME=__token__` and `TWINE_PASSWORD=pypi-<token>` format |
| Package name collision on PyPI | Check name availability at pypi.org first; adjust `name` field in `pyproject.toml` |
| Import error after installation | Check `__init__.py` exports; verify wheel contents before upload |
| Version already exists on PyPI | PyPI does not allow overwriting versions — must increment version number |

---

## 7. Runbook Status

| Section | Status |
|---------|--------|
| Step-by-step sequence documented | COMPLETE |
| Human-required steps labeled EXTERNAL_GATE | COMPLETE |
| Credential gaps classified | COMPLETE |
| Failure modes documented | COMPLETE |
| First test target identified (FODS) | COMPLETE |
| Actual publication executed | NOT DONE — awaiting PyPI credentials (EXTERNAL_BLOCKER) |

**Runbook is ready for use. Publication blocked only by `EXTERNAL_BLOCKER: pypi_credentials_unavailable`.**
