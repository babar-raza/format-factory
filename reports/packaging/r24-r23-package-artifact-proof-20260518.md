# R24 — R23 Package Artifact Proof
# Sprint: FORMAT-FACTORY-R24-PARALLEL-CLOSURE-REPAIR-FORWARD-TRAIN-AND-AI-PLATFORM-PLAN-001
# Date: 2026-05-18
# Gate: 3 — R23 package artifact proof
# Lane: C

## Artifact Exclusion Policy

Binary artifacts (.whl, .tar.gz, .nupkg) are stored under `.local/package-builds/`
which is gitignored by project policy. They are NOT committed to the repository.
Evidence is provided through this artifact manifest + SHA-256 checksums + installed-wheel
validation tests (25/25 PASS) that prove the wheels install and import correctly.

This document supersedes reports/packaging/r23-closure-package-artifact-proof-20260518.md
and confirms the artifact state from the R23 sprint remains valid at R24 sprint start.

## Python FOSS Wheel/Sdist Artifacts

Location: `.local/package-builds/python-foss/{pkg}/dist/`
Build script: `packaging/python/build-local-packages.py`
Build result: 5/5 built, 0 errors (from R23 sprint)

| Package | Artifact | Bytes | SHA-256 (truncated) |
|---------|----------|-------|---------------------|
| aspose-format-factory-zst | aspose_format_factory_zst-0.1.0.dev0-py3-none-any.whl | 4998 | 8efba8814a1627c5... |
| aspose-format-factory-zst | aspose_format_factory_zst-0.1.0.dev0.tar.gz | 5372 | e9b41d6f0d2d69d7... |
| aspose-format-factory-fodp | aspose_format_factory_fodp-0.1.0.dev0-py3-none-any.whl | 4136 | 05ab0df22add9419... |
| aspose-format-factory-fodp | aspose_format_factory_fodp-0.1.0.dev0.tar.gz | 4490 | 00a4e2eec60213b7... |
| aspose-format-factory-fodg | aspose_format_factory_fodg-0.1.0.dev0-py3-none-any.whl | 4237 | 609b14dbde2727c1... |
| aspose-format-factory-fodg | aspose_format_factory_fodg-0.1.0.dev0.tar.gz | 4595 | 15b1468aa0e0c991... |
| aspose-format-factory-gnumeric | aspose_format_factory_gnumeric-0.1.0.dev0-py3-none-any.whl | 3949 | 15454389eae0c827... |
| aspose-format-factory-gnumeric | aspose_format_factory_gnumeric-0.1.0.dev0.tar.gz | 4282 | bf6ca82c4a7c5695... |
| aspose-format-factory-abw | aspose_format_factory_abw-0.1.0.dev0-py3-none-any.whl | 3703 | b02a9cf1d329443c... |
| aspose-format-factory-abw | aspose_format_factory_abw-0.1.0.dev0.tar.gz | 4127 | 7145e886e9c2e6d1... |

Artifact reproducibility confirmed: SHA-256 hashes match across three independent
background builds in R23 session. Artifacts are deterministic for version 0.1.0.dev0.

## NuGet Local Pack Artifacts

Location: `.local/package-builds/r23-nuget/`
Build command: `dotnet pack --no-build -o .local/package-builds/r23-nuget/{format}/`
Status: LOCAL PACK ONLY — not pushed to NuGet.org

| Package | Artifact | Bytes | SHA-256 (truncated) |
|---------|----------|-------|---------------------|
| FormatFactory.Fods | FormatFactory.Fods.0.1.0-tier0.nupkg | 7290 | 70e8ded6016c5e80... |
| FormatFactory.Fodt | FormatFactory.Fodt.0.1.0-tier0.nupkg | 7387 | 92fb586157f5ecc1... |

## Installed-Wheel Validation

```
PACKAGE_INSTALL_RESULT: tests/packaging/test_python_installed_wheels.py — 25 passed, 0 failed
```

Tests use `pip install --target={tmpdir}` to install each wheel into an isolated directory,
then subprocess-import the module and verify IMPORT_OK + __version__/__track__/__commercial_ready__
/__capability_level__.

Post-R23-commit validation confirms: **25/25 PASS**

## Package Metadata Verification

All 5 Python packages have consistent metadata (verified by test_cross_format_api_consistency.py):
- `__version__` = "0.1.0.dev0"
- `__track__` = "python-foss" (NOT "foss")
- `__commercial_ready__` = False
- `__capability_level__` = "alpha-foss-preview"

## Publication Status

- PyPI: NOT PUBLISHED (`publication_authorized: FALSE` in all 5 release manifests)
- NuGet.org: NOT PUBLISHED (local pack only, `commercial_product_ready: false`)
- No upload commands have been run

## Python FOSS Publication Packet State

All 7 files in release-manifests/python-foss/publication-packet/ are committed (b341d0d).
Publication is explicitly blocked pending human review.
See: release-manifests/python-foss/publication-packet/publication-blocked-checklist.md

**Gate 3 — PASS (artifact proof confirmed)**
**Lane C — Package Artifact Proof: COMPLETE**
