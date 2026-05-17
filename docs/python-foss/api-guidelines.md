# Python FOSS API Guidelines

**Sprint:** FORMAT-FACTORY-R21-FOSS-RELEASE-READINESS-AND-GATE11-COMMERCIAL-PREEXECUTION-TRAIN-001
**Date:** 2026-05-17
**Status:** ACTIVE

## Overview

These guidelines define the required API policy for all format-factory Python FOSS packages.
They apply to: `zst`, `fodp`, `fodg`, `gnumeric`, `abw` (and any future FOSS-track packages).

## Required Package Attributes

Every package `__init__.py` must expose:

| Attribute | Type | Example |
|-----------|------|---------|
| `__version__` | str | `"0.1.0.dev0"` |
| `__track__` | str | `"python-foss"` |
| `__commercial_ready__` | bool | `False` |
| `__capability_level__` | str | `"alpha-foss-preview"` |

## Required API Shape

Every package must expose:

1. **Primary load/read/validate function** — `load(source)` accepting `str | bytes | Path`
2. **Typed result** — `dict[str, Any]` with documented keys, or a named result type
3. **Exception hierarchy** — `FormatError` base + `FormatParseError` subclass
4. **Size guard** — `MAX_FILE_SIZE` constant (≤ 64 MiB for XML formats; ≥ 256 MiB output limit for ZST)

## Exception Naming Convention

```
FormatError          # Base — e.g. ZstError, FodpError, GnumericError
  FormatParseError   # Parse failures
  FormatSizeError    # Optional: file too large
```

## Size Guards (Non-Negotiable)

Every `load()` implementation must reject inputs exceeding its guard:

| Package | Guard | Default |
|---------|-------|---------|
| `zst`   | `DEFAULT_MAX_OUTPUT_BYTES` | 256 MiB decompressed |
| `fodp`  | `MAX_FILE_SIZE` | 64 MiB |
| `fodg`  | `MAX_FILE_SIZE` | 64 MiB |
| `gnumeric` | `MAX_FILE_SIZE` | 64 MiB (compressed) |
| `abw`   | `MAX_FILE_SIZE` | 64 MiB |

## Network Policy

Zero network calls. All parsing uses stdlib only (or `zstandard` for ZST — pure-Python/C extension, no network).

## Commercial Dependency Policy

No commercial dependencies. No Aspose .NET libraries. No proprietary parsers.

## Capability Level Labels

All packages are labeled `alpha-foss-preview`. This means:

- Not production-ready
- Not commercially authorized for release
- APIs may change without notice
- `commercial_product_ready: false`
- No PyPI publication authorized

## Format-Specific API Summary

### `zst` — Zstandard Compression

```python
from zst import compress_bytes, decompress_bytes, probe_frame, validate_file
```

Primary operations: compress/decompress/probe/validate. Not a document format (no page/sheet model).

### `fodp` — Flat OpenDocument Presentation

```python
from fodp import load, get_page_count, extract_text, get_page_metadata
```

Primary structure: pages. `load()` returns dict with `page_count`, `pages`, `title`.

### `fodg` — Flat OpenDocument Graphics

```python
from fodg import load, get_page_count, get_shape_count, extract_text, get_page_metadata
```

Primary structure: pages with shapes. Adds `get_shape_count()`.

### `gnumeric` — Gnumeric Spreadsheet

```python
from gnumeric import load, get_sheet_count, get_cell_count, extract_values, get_sheet_metadata
```

Primary structure: sheets with cells. Gzip+XML, requires decompression.

### `abw` — AbiWord Document

```python
from abw import load, get_section_count, get_paragraph_count, extract_text
```

Primary structure: sections with paragraphs. DOCTYPE-stripped for safety.

## What Is NOT Supported (Alpha Limits)

- No format conversion or export
- No write/modify operations
- No streaming for large files
- No rendering or display
- No commercial-grade error recovery
- No localization
- No encryption/DRM handling

## R21 Normalization Changes

The following were added in R21 to normalize APIs:

- `__capability_level__ = "alpha-foss-preview"` added to all five `__init__.py` files
- This attribute makes it machine-checkable that no package claims production readiness
