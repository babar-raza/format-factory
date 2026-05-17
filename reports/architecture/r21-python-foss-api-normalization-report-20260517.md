---
artifact_id: r21-python-foss-api-normalization-report
artifact_type: report
sprint: FORMAT-FACTORY-R21-FOSS-RELEASE-READINESS-AND-GATE11-COMMERCIAL-PREEXECUTION-TRAIN-001
date: "2026-05-17"
gate: "2"
status: PASS
visibility: internal
---

# R21 Gate 2 — Python FOSS API Normalization Report

## Policy Source

`docs/python-foss/api-guidelines.md` (created this sprint)

## Pre-Normalization Audit

| Package | __version__ | __track__ | __commercial_ready__ | __capability_level__ | load() | Exception base | Size guard |
|---------|-------------|-----------|----------------------|----------------------|--------|----------------|------------|
| zst     | ✓ 0.1.0.dev0 | ✓ python-foss | ✓ False | MISSING | ✓ (probe_frame/validate_file) | ✓ ZstError | ✓ 256 MiB |
| fodp    | ✓ 0.1.0.dev0 | ✓ python-foss | ✓ False | MISSING | ✓ load() | ✓ FodpError | ✓ 64 MiB |
| fodg    | ✓ 0.1.0.dev0 | ✓ python-foss | ✓ False | MISSING | ✓ load() | ✓ FodgError | ✓ 64 MiB |
| gnumeric | ✓ 0.1.0.dev0 | ✓ python-foss | ✓ False | MISSING | ✓ load() | ✓ GnumericError | ✓ 64 MiB |
| abw     | ✓ 0.1.0.dev0 | ✓ python-foss | ✓ False | MISSING | ✓ load() | ✓ AbwError | ✓ 64 MiB |

**Finding:** `__capability_level__` missing from all five packages. All other attributes present.

## Changes Applied

Added `__capability_level__ = "alpha-foss-preview"` to all five `__init__.py` files:
- src/python/zst/__init__.py — UPDATED
- src/python/fodp/__init__.py — UPDATED
- src/python/fodg/__init__.py — UPDATED
- src/python/gnumeric/__init__.py — UPDATED
- src/python/abw/__init__.py — UPDATED

No other source changes required. No API breakage.

## Post-Normalization State

| Package | All Required Attributes | Network-Free | No Commercial Dep | Size Guard |
|---------|------------------------|--------------|-------------------|------------|
| zst     | ✓ | ✓ | ✓ (zstandard = pure FOSS C ext) | ✓ |
| fodp    | ✓ | ✓ | ✓ | ✓ |
| fodg    | ✓ | ✓ | ✓ | ✓ |
| gnumeric | ✓ | ✓ | ✓ | ✓ |
| abw     | ✓ | ✓ | ✓ | ✓ |

## API Differences Across Packages (By Design)

The APIs differ by domain — ZST is a compression codec, not a document format:

- ZST: `compress_bytes`, `decompress_bytes`, `probe_frame`, `validate_file`
- FODP/FODG: `load`, `get_page_count`, `extract_text`, `get_page_metadata`
- Gnumeric: `load`, `get_sheet_count`, `get_cell_count`, `extract_values`, `get_sheet_metadata`
- ABW: `load`, `get_section_count`, `get_paragraph_count`, `extract_text`

These differences are correct and intentional. The normalization policy does not require identical APIs.

## Gate 2 Verdict

GATE_2: PASS — API normalization complete. `__capability_level__` added to all five packages.
Tests unchanged (no behavioral changes).
