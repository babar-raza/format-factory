---
report_id: r27-python-foss-publication-blocker-reduction-report-20260519
sprint: R27
lane: I
title: "Python FOSS Publication Packet -- Non-Authority Blocker Reduction"
date: "2026-05-19"
author: claude-opus-4-6
publication_authorized: false
blocked_external_authority: true
---

# R27 Lane I: Python FOSS Publication Blocker Reduction Report

## Summary

This report documents the resolution of non-authority blockers identified in R26
for the 5 Python FOSS packages. No publication was performed. Publication remains
blocked on external authority (Babar Raza).

## Packages in Scope

| Package | Module | Format |
|---|---|---|
| aspose-format-factory-zst | `zst` | Zstandard (.zst) |
| aspose-format-factory-fodp | `fodp` | Flat OpenDocument Presentation (.fodp) |
| aspose-format-factory-fodg | `fodg` | Flat OpenDocument Graphics (.fodg) |
| aspose-format-factory-gnumeric | `gnumeric` | Gnumeric (.gnumeric) |
| aspose-format-factory-abw | `abw` | AbiWord (.abw) |

## Blockers Resolved

### 1. Missing per-package README.md (RESOLVED)

Created `README.md` for all 5 packages in `src/python/{format}/README.md`, following
the template pattern established by `src/python/fods/README.md`. Each README includes:

- Package name, version (0.1.0.dev0), track (python-foss), capability level (alpha-foss-preview)
- License (Apache-2.0)
- Specification reference
- Gate history
- Quick-start code example using the actual public API from `__init__.py`
- Security notes relevant to the format
- Dependency listing
- Package structure

Files created:
- `src/python/zst/README.md`
- `src/python/fodp/README.md`
- `src/python/fodg/README.md`
- `src/python/gnumeric/README.md`
- `src/python/abw/README.md`

### 2. Missing per-package LICENSE (RESOLVED)

Created Apache-2.0 full license text in `src/python/{format}/LICENSE` for all 5 packages.
Copyright holder: Aspose Pty Ltd 2026.

Files created:
- `src/python/zst/LICENSE`
- `src/python/fodp/LICENSE`
- `src/python/fodg/LICENSE`
- `src/python/gnumeric/LICENSE`
- `src/python/abw/LICENSE`

### 3. Missing CHANGELOG.md (NOT REQUIRED)

Reviewed `packaging/python/package-matrix.yaml`. No CHANGELOG.md requirement exists
in the packaging policy. CHANGELOG.md was not created. This blocker is dismissed as
not applicable.

## Remaining Blockers (External Authority Only)

| Blocker | Status | Owner |
|---|---|---|
| `publication_authorized: false` in package-matrix.yaml | Awaiting human authority | Babar Raza |
| `publish_status: local_only_not_published` | Awaiting publication decision | Babar Raza |
| PyPI account/token setup | Not yet provisioned | Babar Raza |

All remaining blockers require external human authority. No further non-authority
blockers exist for the publication packet.

## Test Results

```
tests/packaging: 68 passed in 23.53s
```

All 68 packaging tests pass with no failures or errors.

## Metadata Verification

All 5 packages share identical metadata attributes:
- `__version__` = `"0.1.0.dev0"`
- `__track__` = `"python-foss"`
- `__commercial_ready__` = `False`
- `__capability_level__` = `"alpha-foss-preview"`

## Constraints Honored

- Did NOT publish to PyPI
- Did NOT set `publication_authorized: true`
- Did NOT modify `tools/ai/**` or `tests/ai/**`
- Did NOT create CHANGELOG.md (not required by packaging policy)
