# R51 Artifact Manifest Integrity

**Sprint:** FORMAT-FACTORY-R51-INSTALLED-ARTIFACT-BASELINE-AND-AI-ACCELERATION-001
**Run:** R51
**Date:** 2026-05-22

---

## R50 Artifact Manifest Defects (History)

R50 fixed 3/5 R49 manifest hash mismatches. R50 manifest was correct in `.local/r50-metadata/`, but the R50 bundle was built before the manifest was updated — resulting in a bundle-internal manifest with stale entries.

R51 repair: All artifacts rebuilt; manifest built fresh from actual artifact bytes.

---

## R51 Artifact Manifest

All 8 artifacts are present and verified:

| Artifact | SHA-256 | Size | Type |
|----------|---------|------|------|
| aspose_format_factory_fods-0.1.0.dev0-py3-none-any.whl | 7ffdb7d9cc0062c6287382671602c9585edd8cd1aa12d722dcb0bb2e182c24df | 14,525 B | Python wheel (NEW — includes csv_exporter.py) |
| aspose_format_factory_fods-0.1.0.dev0.tar.gz | 7d01b0cadaf2b48e6db51982505db329d4a64e23138b54bcd657492fc02e8468 | 1,252,980 B | Python sdist |
| aspose_format_factory_fodt-0.1.0.dev0-py3-none-any.whl | 33cd5a3cae3a06004474450bc80e264120244751415d7657c6733a75cba646b1 | 14,602 B | Python wheel |
| aspose_format_factory_fodt-0.1.0.dev0.tar.gz | 548412c9cf8e6b3df8c74fd8a27f67ede88df8ce921cb4d8ea995eaec491ae50 | 1,400,806 B | Python sdist |
| aspose_format_factory_zst-0.1.0.dev0-py3-none-any.whl | 328561e74bd7f89bf7743e429065ee12232b3d61ec6eb1373ebe02766be0c8e0 | 9,780 B | Python wheel |
| aspose_format_factory_zst-0.1.0.dev0.tar.gz | 180da7768d9a7246af366e463d2a5f138103ca902ebf9f2edbb29745811e36b9 | 9,704 B | Python sdist |
| FormatFactory.Fods.0.1.0-tier0.nupkg | 1f81b3cf6d90cefd4deb3d91fd070347e168c854550f9593299a79ee2ea62a58 | 14,617 B | .NET nupkg |
| FormatFactory.Fodt.0.1.0-tier0.nupkg | a9b2426daa925f8e0ac751a7483c516ef96ff0648f9236b7e15c2e91a367a2dc | 13,670 B | .NET nupkg |

**ARTIFACT_MANIFEST_R51: PASS** (all 8 artifacts verified from actual bytes)

---

## Validator Fix (R51)

R50 validator missed `check_artifact_inventory()` when manifest was inside the bundle ZIP. R51 ensures:
1. Manifest is built AFTER artifacts are finalized
2. Bundle is built AFTER manifest is written
3. Validator checks bundle-internal manifest against bundle-internal artifact files

---

## Provenance

All artifacts built locally:
- Python packages: `packaging/python/build-local-packages.py`
- .NET packages: `dotnet pack src/net/fods/` and `dotnet pack src/net/fodt/`
- `publication_authorized: false` — NOT published to PyPI, NuGet, or any registry
