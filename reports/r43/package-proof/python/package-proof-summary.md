# R43 Python Package Proof — FODS + FODT

**Sprint:** R43
**Date:** 2026-05-21
**Build tool:** python -m build (build==1.5.0, hatchling backend)
**Venv:** `.local/build-venv` (Python 3.13.2, isolated)
**Smoke venv:** `.local/smoke-venv-r43` (clean install, Python 3.13.2)

---

## Build Results

| Artifact | SHA-256 | Size | Build Status |
|----------|---------|------|--------------|
| `aspose_format_factory_fods-0.1.0.dev0-py3-none-any.whl` | `0d9e6826515d849052bcda7f8546515063e51ab93d23e7183715c96b45c26014` | 10696 bytes | PASS |
| `aspose_format_factory_fods-0.1.0.dev0.tar.gz` | `1fb38822831b73f79ccc4d5430da8c081f8ac94d33b5227fdf16799beb8a3482` | 9553 bytes | PASS |
| `aspose_format_factory_fodt-0.1.0.dev0-py3-none-any.whl` | `513e84aaa5b29c90128d11d4c80f3ce2c451cc0d5d9c8801b044b7b49ca391a5` | 12290 bytes | PASS |
| `aspose_format_factory_fodt-0.1.0.dev0.tar.gz` | `e99cb85f8d17adc6d6dc767b29fcd7203be20c7918dfcf5329b6b72fe945279f` | 10617 bytes | PASS |

**Wheel SHA-256 matches R42 chain-of-custody** (fods: `0d9e6826...`, fodt: `513e84aa...`).

---

## Raw Build Logs

- `fods-build-log.txt` — `python -m build` output for FODS
- `fodt-build-log.txt` — `python -m build` output for FODT
- `fods-install-log.txt` — `pip install` in clean venv for FODS wheel
- `fodt-install-log.txt` — `pip install` in clean venv for FODT wheel
- `fods-smoke-log.txt` — 4/4 sample parse smoke test from clean venv
- `fodt-smoke-log.txt` — 4/4 sample parse smoke test from clean venv

---

## Smoke Test Results

```
FODS_SMOKE: PASS — 4/4 samples (formula-basic, minimal-spreadsheet, multi-sheet-basic, typed-values-basic)
FODT_SMOKE: PASS — 4/4 samples (headings-and-paragraphs, list-basic, minimal-document, table-basic)
```

---

## Consumer Import Proof

```python
import fods
print(fods.__version__)   # 0.1.0
fods.parse_fods("sample.fods")  # returns dict with format_id, sheets
```

```python
import fodt
print(fodt.__version__)   # 0.1.0
fodt.parse_fodt("doc.fodt")  # returns dict with format_id, blocks
```

---

## Status

- `PYTHON_BUILD_PROOF: PASS`
- `PYTHON_SMOKE_PROOF: PASS`
- All artifacts in `.local/` (gitignored). Not pushed. Local POC only.
- Gate 11 (commercial approval): NOT_STARTED
