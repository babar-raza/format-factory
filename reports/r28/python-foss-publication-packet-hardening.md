# Python FOSS Publication Packet Hardening Report

- **Sprint:** R28 Lane I
- **Date:** 2026-05-19
- **Author:** Agent (Claude Opus 4.6)
- **publication_authorized:** false
- **Verdict:** AUDIT COMPLETE — blockers identified for ODS/ODT/QOI

---

## 1. Publication Readiness Matrix — Gate 10 Formats (ZST, FODP, FODG, Gnumeric, ABW)

| Check                     | ZST    | FODP   | FODG   | Gnumeric | ABW    |
|---------------------------|--------|--------|--------|----------|--------|
| `__init__.py` present     | PASS   | PASS   | PASS   | PASS     | PASS   |
| `__version__`             | PASS (0.1.0.dev0) | PASS (0.1.0.dev0) | PASS (0.1.0.dev0) | PASS (0.1.0.dev0) | PASS (0.1.0.dev0) |
| `__track__`               | PASS (python-foss) | PASS (python-foss) | PASS (python-foss) | PASS (python-foss) | PASS (python-foss) |
| `__commercial_ready__`    | PASS (False) | PASS (False) | PASS (False) | PASS (False) | PASS (False) |
| `__capability_level__`    | PASS (alpha-foss-preview) | PASS (alpha-foss-preview) | PASS (alpha-foss-preview) | PASS (alpha-foss-preview) | PASS (alpha-foss-preview) |
| `README.md` present       | PASS   | PASS   | PASS   | PASS     | PASS   |
| `LICENSE` present          | PASS   | PASS   | PASS   | PASS     | PASS   |
| In package-matrix.yaml    | PASS   | PASS   | PASS   | PASS     | PASS   |
| Packaging test coverage   | PASS (artifacts + imports) | PASS (artifacts + imports) | PASS (artifacts + imports) | PASS (artifacts + imports) | PASS (artifacts + imports) |
| Blockers                  | None   | None   | None   | None     | None   |

**Summary:** All 5 Gate 10 formats have complete publication packets. All are present in `packaging/python/package-matrix.yaml` with `publication_authorized: false` and `commercial_ready: false`. Packaging tests cover all 5 formats via parametrized tests in `tests/packaging/test_python_local_package_artifacts.py` (wheel + sdist existence and size) and `tests/packaging/test_python_local_package_imports.py` (importability + API surface).

---

## 2. Publication Readiness Matrix — New Formats (ODS, ODT, QOI)

| Check                     | ODS         | ODT         | QOI         |
|---------------------------|-------------|-------------|-------------|
| `__init__.py` present     | PASS        | PASS        | PASS        |
| `__version__`             | PASS (0.1.0.dev0) | PASS (0.1.0.dev0) | PASS (0.1.0.dev0) |
| `__track__`               | PASS (python-foss) | PASS (python-foss) | PASS (python-foss) |
| `__commercial_ready__`    | PASS (False) | PASS (False) | PASS (False) |
| `__capability_level__`    | PASS (alpha-foss-preview) | PASS (alpha-foss-preview) | PASS (alpha-foss-preview) |
| `README.md` present       | **MISSING** | **MISSING** | **MISSING** |
| `LICENSE` present          | **MISSING** | **MISSING** | **MISSING** |
| In package-matrix.yaml    | **NO**      | **NO**      | **NO**      |
| Packaging test coverage   | NOT TESTED  | NOT TESTED  | NOT TESTED  |
| Blockers                  | See below   | See below   | See below   |

### ODS/ODT/QOI Blockers

1. **README.md missing** — `src/python/{ods,odt,qoi}/README.md` do not exist. Required for pyproject template (`readme = "README.md"`).
2. **LICENSE missing** — `src/python/{ods,odt,qoi}/LICENSE` do not exist. Required for FOSS distribution.
3. **Not in package-matrix.yaml** — No entries for `aspose-format-factory-ods`, `aspose-format-factory-odt`, or `aspose-format-factory-qoi`.
4. **Not in packaging tests** — `tests/packaging/test_python_local_package_imports.py` MODULES list and `test_python_local_package_artifacts.py` PACKAGES list only cover the original 5 formats.
5. **No public API exports** — The `__init__.py` files for ODS/ODT/QOI contain only metadata attributes; no codec functions are exported (no `__all__`, no `from .xxx_codec import ...`). These are Gate 4 prototypes; actual parsers may or may not exist yet.

### Should ODS/ODT/QOI be added to package-matrix now?

**Recommendation: No, not yet.** These formats are at Gate 4 (parser prototype). The existing 5 formats were added to the matrix at Gate 7+. Adding ODS/ODT/QOI prematurely would create packages with no functional API. They should be added when:
- Gate 7 is passed (or equivalent maturity milestone)
- A functional codec is exported from `__init__.py`
- README.md and LICENSE files are authored
- Packaging tests are extended to cover them

---

## 3. Pyproject Template Validity

The template at `packaging/python/pyproject.template.toml` uses `hatchling` as build backend and substitution variables (`{{PACKAGE_NAME}}`, `{{MODULE_NAME}}`, `{{VERSION}}`, `{{DESCRIPTION}}`, `{{DEPENDENCIES}}`). For all 5 matrix packages:

- All substitution variables have corresponding values in `package-matrix.yaml`
- `license = {text = "Apache-2.0"}` matches the `license: Apache-2.0` in the matrix
- `requires-python = ">=3.9"` matches `python_version: ">=3.9"` in the matrix
- `packages = ["src/python/{{MODULE_NAME}}"]` correctly maps to the source layout
- The template carries `publication_authorized: false` and `commercial_product_ready: false` comments

**Template verdict: VALID for all 5 Gate 10 packages.**

---

## 4. Package-Matrix Coverage Summary

| Format    | In Matrix | publication_authorized | commercial_ready | gates_passed |
|-----------|-----------|----------------------|------------------|--------------|
| ZST       | Yes       | false                | false            | [1-7]        |
| FODP      | Yes       | false                | false            | [1-7]        |
| FODG      | Yes       | false                | false            | [1-7]        |
| Gnumeric  | Yes       | false                | false            | [1-7]        |
| ABW       | Yes       | false                | false            | [1-7]        |
| ODS       | No        | n/a                  | n/a              | [1-4]        |
| ODT       | No        | n/a                  | n/a              | [1-4]        |
| QOI       | No        | n/a                  | n/a              | [1-4]        |
| FODS      | No (*)    | n/a                  | n/a              | [1-10] (.NET only) |
| FODT      | No (*)    | n/a                  | n/a              | [1-10] (.NET only) |

(*) FODS/FODT have Python source in `src/python/fods/` and `src/python/fodt/` but are NOT in the Python FOSS package matrix. These are .NET-primary formats; Python FOSS packaging was not planned for them.

---

## 5. Key File Paths

- Package matrix: `packaging/python/package-matrix.yaml`
- Pyproject template: `packaging/python/pyproject.template.toml`
- Packaging tests: `tests/packaging/test_python_local_package_artifacts.py`, `tests/packaging/test_python_local_package_imports.py`
- Source directories: `src/python/{zst,fodp,fodg,gnumeric,abw,ods,odt,qoi}/`

---

## 6. Conclusion

- **5 Gate 10 formats (ZST, FODP, FODG, Gnumeric, ABW):** Publication packets are COMPLETE. All checks pass. No blockers. `publication_authorized` remains `false` pending human authorization.
- **3 Gate 4 formats (ODS, ODT, QOI):** NOT READY for packaging. Missing README.md, LICENSE, package-matrix entries, functional API exports, and test coverage. These should not be added until they reach sufficient gate maturity.
- **No action required** on FODS/FODT Python sources — they are not part of the Python FOSS publication track.
