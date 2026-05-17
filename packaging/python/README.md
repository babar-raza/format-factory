# Python FOSS Package Metadata

**Status:** local_only_not_published
**publication_authorized:** false
**commercial_product_ready:** false
**Capability:** alpha-foss-preview

## Contents

| File | Purpose |
|------|---------|
| `package-matrix.yaml` | Authoritative list of all Python FOSS packages with metadata |
| `pyproject.template.toml` | Template for generating per-package `pyproject.toml` files |
| `build-local-packages.py` | Script to build local wheel/sdist artifacts (no PyPI upload) |

## Packages

| Package Name | Module | Format |
|-------------|--------|--------|
| aspose-format-factory-zst | zst | Zstandard (.zst) |
| aspose-format-factory-fodp | fodp | Flat OpenDocument Presentation (.fodp) |
| aspose-format-factory-fodg | fodg | Flat OpenDocument Graphics (.fodg) |
| aspose-format-factory-gnumeric | gnumeric | Gnumeric Spreadsheet (.gnumeric) |
| aspose-format-factory-abw | abw | AbiWord Document (.abw) |

## Local Build

```bash
python packaging/python/build-local-packages.py
```

Artifacts are written to `.local/package-builds/python-foss/` (gitignored).

## What Is NOT Allowed

- No `pip publish`, `twine upload`, or `poetry publish` to PyPI
- No version tags on git for release purposes
- No GitHub release artifacts uploaded
- No credentials or API tokens used

## License

All packages: Apache-2.0 (FOSS track).
The underlying format specifications are royalty-free (OASIS ODF) or FOSS-compatible (Gnumeric, ABW, ZST/RFC 8878).

## Gate Evidence

Gates 1-7 passed for all five formats. See `acquisition-packs/{format}/pack.yaml` for per-format gate records.
