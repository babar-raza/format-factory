---
artifact_id: fods-gate10-packaging-plan
artifact_type: acquisition-pack
path: acquisition-packs/fods/gate10-packaging-plan.md
format_id: fods
visibility: internal
publish_allowed: false
license: null
provenance_required: false
provenance_status: not-applicable
source_hash: null
generated_by: claude-sonnet-4-6
generated_at: "2026-05-08"
stale: false
open_source_allowed: false
commercial_allowed: false
release_blockers: []
notes: "FODS Gate 10 Python packaging plan. run048 (2026-05-08)."
---

# FODS Gate 10 — Python Packaging Plan

**Gate:** 10 — OSS Release Readiness
**Format:** FODS
**Run:** run048 (2026-05-08)
**Status:** APPROVED — Babar Raza (2026-05-08, run048)

---

## Package Identity

| Property | Value |
|---|---|
| Package name | `format-factory-fods` |
| Import name | `format_factory_fods` |
| First version | `0.1.0` |
| Python requirement | `>=3.11` |
| Dependencies | None (Python stdlib only) |
| License | Apache-2.0 |
| Distribution target | PyPI (primary) + GitHub Releases |

---

## Version Scheme

| Version | Scope |
|---|---|
| 0.1.0 | First OSS release — Tiers 0, 1, 2 (12 features) |
| 0.2.0 | Tier 3 (Formulas + References) |
| 0.3.0+ | Tier 4 (Advanced) |
| 1.0.0 | Production-ready milestone (all OSS tiers stable) |

---

## Source Layout (Phase 4+)

```
src/python/fods/
    __init__.py
    parser.py          # Core FODS parser (iterparse-based)
    types.py           # Typed value extraction
    identity.py        # Format detection + identity
    structural.py      # Sheet/row/column extraction
    py.typed           # PEP 561 marker
    VERSION
```

---

## Package Build

```
pyproject.toml         # Build metadata (PEP 517/518)
setup.cfg              # Backward compatibility
MANIFEST.in            # Include py.typed + VERSION
```

Build system: `flit` or `setuptools` (TBD at Phase 4 implementation).

---

## CI/CD Plan (Phase 4+)

- GitHub Actions workflow: `.github/workflows/fods-python-ci.yml`
- Triggers: push to main, PR, release tag
- Steps: lint (ruff), type-check (mypy), tests (pytest), build wheel, upload to PyPI
- Test matrix: Python 3.11, 3.12, 3.13

---

## Notes

- No third-party dependencies. Zero-dependency policy for Tier 0-2.
- Product source creation (`src/python/fods/`) requires a separate explicit Phase 4
  Python implementation execution prompt AFTER Gate 10 approval.
- DEC-033 (.NET FOSS packaging) is deferred; .NET product track is separate (Gate 10 .NET).
