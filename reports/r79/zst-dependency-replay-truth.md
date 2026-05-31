# R79 Train H — ZST Dependency Replay Truth

**sprint_id:** FORMAT-FACTORY-R79-PACKAGE-SOURCE-SYNC-FIRST-REAL-FODS-PRODUCT-RC-ZST-DEPENDENCY-REPLAY-MEGA-TRAIN-001
**date:** 2026-05-30
**train:** H

## D78-12: ZST No-Network Install Classification

### Defect Summary
The ZST wheel requires `zstandard>=0.21.0` as a runtime dependency.
The R78 supervisor review package does NOT include the `zstandard` wheel.
Installing ZST with `pip install --no-index --find-links package-artifacts/ zst`
fails because `zstandard` is not found locally.

### Classification

**Classification:** `ZST_LOCAL_RC_DEPENDENCY_RESOLUTION_REQUIRED`

This is NOT a bug — it is an accurate reflection of ZST's dependency model:
- ZST is a wrapper around the `zstandard` C-extension package
- `zstandard` must be installed from PyPI (or bundled separately)
- ZST cannot do offline installation without `zstandard` available

### Why This Is NOT Being Fixed in R79

Bundling `zstandard` (a C-extension package) would require:
1. Building platform-specific wheels for `zstandard` for each target platform
2. Downloading the official wheel from PyPI (authorized download required)
3. Including a ~200KB platform-specific binary in the review package

This is out of scope for R79 (Package Source Sync sprint). The honest classification is:
`ZST_LOCAL_RC_DEPENDENCY_RESOLUTION_REQUIRED`

### What "Product RC Ready" Means for ZST

ZST's Gate 10 status: `local_release_candidate_ready_verified`

This means: the ZST source is RC-ready AS A PACKAGE, but offline-only installation
is not supported without `zstandard` bundled. Consumer of ZST wheel must have
`pip` with network access or pre-installed `zstandard`.

This is normal for packages with C-extension dependencies (numpy, pandas, lxml, etc.)

### Guidance for Consumers

```bash
pip install aspose-format-factory-zst  # requires network (PyPI) or pre-installed zstandard
# OR
pip install zstandard  # install dependency first
pip install --no-index --find-links . aspose_format_factory_zst-0.1.0.dev0-py3-none-any.whl
```

### ZST API Verification (from source)

`zst.__version__ = "0.1.0.dev0"` (already correct — no fix needed)
`zst.__track__ = "python-foss"`

ZST_DEPENDENCY_REPLAY_TRUTH: CLASSIFICATION_ZST_LOCAL_RC_DEPENDENCY_RESOLUTION_REQUIRED
D78_12: CLASSIFIED
