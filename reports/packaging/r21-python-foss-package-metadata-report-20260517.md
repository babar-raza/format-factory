---
artifact_id: r21-python-foss-package-metadata-report
artifact_type: report
sprint: FORMAT-FACTORY-R21-FOSS-RELEASE-READINESS-AND-GATE11-COMMERCIAL-PREEXECUTION-TRAIN-001
date: "2026-05-17"
gate: "3"
status: PASS
visibility: internal
---

# R21 Gate 3 — Python FOSS Package Metadata Report

## Deliverables Created

| File | Purpose |
|------|---------|
| `packaging/python/package-matrix.yaml` | Authoritative 5-package registry |
| `packaging/python/pyproject.template.toml` | Build template |
| `packaging/python/build-local-packages.py` | Local build script (no PyPI) |
| `packaging/python/README.md` | Package metadata documentation |
| `tests/evidence/test_python_package_matrix.py` | 13 tests validating matrix |

## Package Matrix Summary

| Package | Module | License | Dependencies | publish_authorized |
|---------|--------|---------|-------------|-------------------|
| aspose-format-factory-zst | zst | Apache-2.0 | zstandard>=0.21.0 | false |
| aspose-format-factory-fodp | fodp | Apache-2.0 | (none) | false |
| aspose-format-factory-fodg | fodg | Apache-2.0 | (none) | false |
| aspose-format-factory-gnumeric | gnumeric | Apache-2.0 | (none) | false |
| aspose-format-factory-abw | abw | Apache-2.0 | (none) | false |

## Invariants Confirmed

- publication_authorized: false for ALL packages
- commercial_ready: false for ALL packages
- capability_level: alpha-foss-preview for ALL packages
- publish_status: local_only_not_published for ALL packages
- No PyPI credentials created
- No push performed
- No release tag created

## License Analysis

| Format | Spec License | Implementation License |
|--------|-------------|----------------------|
| ZST | RFC 8878 (IETF) — public | Apache-2.0 |
| FODP | OASIS ODF 1.3 RF Category 1 | Apache-2.0 |
| FODG | OASIS ODF 1.3 RF Category 1 | Apache-2.0 |
| Gnumeric | GNOME Project (LGPL spec) | Apache-2.0 |
| ABW | AbiWord/AbiSource (LGPL) | Apache-2.0 |

Note: Gnumeric and ABW spec licenses are LGPL for the applications, but the XML formats
themselves are open and documented. Implementation in Apache-2.0 is compatible with FOSS use.
This is planning-level licensing confirmation — formal legal review required before any commercial use.

## Gate 3 Verdict

GATE_3: PASS — Package metadata created for all five Python FOSS tracks.
No publication performed. Tests written.
