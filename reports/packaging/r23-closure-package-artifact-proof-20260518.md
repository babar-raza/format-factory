# R23 Closure — Package Artifact Proof
# Sprint: FORMAT-FACTORY-R23-CLOSURE-RECONSTRUCTION-AND-EVIDENCE-HARDENING-001
# Date: 2026-05-18
# publication_authorized: false — no PyPI/NuGet.org upload

## Artifact Exclusion Policy

Binary artifacts (`.whl`, `.tar.gz`, `.nupkg`) are stored under `.local/package-builds/`
which is gitignored by project policy. They are NOT committed to the repository.
The evidence bundle includes this artifact manifest + SHA-256 checksums as proof.
Installed-wheel validation tests (`test_python_installed_wheels.py`, 25/25 PASS) prove
the wheels install and import correctly without committing the binary files.

## Python FOSS Wheel/Sdist Artifacts

Location: `.local/package-builds/python-foss/{pkg}/dist/`
Build script: `packaging/python/build-local-packages.py`
Build result: 5/5 built, 0 errors

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
then subprocess-import the module and verify IMPORT_OK + __version__/__track__/__commercial_ready__/__capability_level__.

## Artifact Reproducibility

SHA-256 hashes match across three independent background builds in R23 session:
- Background task bbxxngwrc: 5/5 built (same hashes)
- Background task baqusncpt: 5/5 built (same hashes)
- Manual build for test_python_installed_wheels.py: 25/25 pass

Artifacts are deterministic for the given source at version 0.1.0.dev0.

## Publication Status

- PyPI: NOT PUBLISHED (`publication_authorized=false`)
- NuGet.org: NOT PUBLISHED (local pack only, `commercial_product_ready=false`)
- No upload commands were run
