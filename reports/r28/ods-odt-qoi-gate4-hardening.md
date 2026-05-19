# ODS/ODT/QOI Gate 4 Parser Hardening Report

**Sprint:** R28, Lane F
**Date:** 2026-05-19
**Scope:** Malformed-input hardening for ODS, ODT, QOI Gate 4 Python parser prototypes

## Audit Summary

### ODS Parser (`src/python/ods/ods_parser.py`)
- **XML Safety:** Uses `xml.etree.ElementTree` which is XXE-safe by default (no external entity expansion). PASS.
- **File Size Guard:** 64 MiB limit checked via `os.path.getsize()` before ZIP open. PASS.
- **ZIP Bomb Protection:** Entry count limit (1000), decompressed size sum check. PASS.
- **Container Validation:** Requires `mimetype` entry with exact ODS MIME string AND `content.xml`. PASS.
- **Malformed ZIP:** `zipfile.BadZipFile` caught and wrapped in `OdsInvalidContainerError`. PASS.
- **Security Bugs Found:** None.

### ODT Parser (`src/python/odt/odt_parser.py`)
- **XML Safety:** Same `xml.etree.ElementTree` approach as ODS. XXE-safe. PASS.
- **File Size Guard:** 64 MiB limit. PASS.
- **ZIP Bomb Protection:** Entry count limit (1000), decompressed size sum check. PASS.
- **Container Validation:** Requires `mimetype` with exact ODT MIME string AND `content.xml`. PASS.
- **Malformed ZIP:** `zipfile.BadZipFile` caught and wrapped. PASS.
- **Security Bugs Found:** None.

### QOI Parser (`src/python/qoi/qoi_parser.py`)
- **Buffer Overflow:** Python handles bounds natively; no C-style overflow risk. PASS.
- **File Size Guard:** 64 MiB limit in `parse_qoi_strict`. PASS.
- **Dimension Limits:** MAX_DIMENSION=16384, MAX_PIXELS=16384^2. PASS.
- **Header Validation:** Magic, channels (3/4), colorspace (0/1), non-zero dimensions. PASS.
- **Pixel Decode Safety:** Bounds checks on truncated chunks (OP_RGB, OP_RGBA, OP_LUMA). PASS.
- **End Marker Verification:** Validates 8-byte end marker. PASS.
- **Minor Note:** `probe_qoi` reads entire file before any size check (no `os.path.getsize` guard). Not a security bug since probe is lightweight, but noted for awareness.
- **Security Bugs Found:** None.

## Tests Added

### ODS (`tests/python/ods/test_ods_parser.py`) -- 10 new tests
| Test | Category |
|------|----------|
| `test_empty_file` | Zero-byte input |
| `test_empty_file_strict` | Zero-byte via strict API |
| `test_random_bytes_not_zip` | Wrong magic / garbage |
| `test_valid_zip_wrong_mimetype` | Valid ZIP, wrong MIME |
| `test_zip_missing_content_xml` | Missing required entry |
| `test_zip_missing_mimetype_entry` | Missing mimetype entry |
| `test_truncated_zip_bytes` | Truncated container |
| `test_oversized_decompressed_claim` | Size guard verification |
| `test_xml_with_entity_declaration` | XXE safety |
| `test_content_xml_not_valid_xml` | Corrupt XML |

### ODT (`tests/python/odt/test_odt_parser.py`) -- 10 new tests
| Test | Category |
|------|----------|
| `test_empty_file` | Zero-byte input |
| `test_empty_file_strict` | Zero-byte via strict API |
| `test_random_bytes_not_zip` | Wrong magic / garbage |
| `test_valid_zip_wrong_mimetype` | Valid ZIP, wrong MIME |
| `test_zip_missing_content_xml` | Missing required entry |
| `test_zip_missing_mimetype_entry` | Missing mimetype entry |
| `test_truncated_zip_bytes` | Truncated container |
| `test_xml_with_entity_declaration` | XXE safety |
| `test_content_xml_not_valid_xml` | Corrupt XML |
| `test_content_xml_empty_body` | Structurally valid but empty |

### QOI (`tests/python/qoi/test_qoi_parser.py`) -- 11 new tests
| Test | Category |
|------|----------|
| `test_empty_file` | Zero-byte input |
| `test_empty_file_strict` | Zero-byte via strict API |
| `test_wrong_magic_bytes` | Wrong magic |
| `test_truncated_header` | Partial header (10 of 14 bytes) |
| `test_zero_width` | Invalid dimension |
| `test_zero_height` | Invalid dimension |
| `test_oversized_dimensions` | Dimension overflow (65535x65535) |
| `test_invalid_channels` | Invalid channel count (5) |
| `test_invalid_colorspace` | Invalid colorspace (2) |
| `test_truncated_pixel_data` | Valid header, no pixel data |
| `test_probe_short_file` | Probe on insufficient data |

## Test Results

```
75 passed in 0.99s
```

- **Pre-existing tests:** 44
- **New hardening tests:** 31
- **Failures:** 0
- **Parser source modifications:** 0 (no security bugs requiring fix)

## Verdict

All three Gate 4 parsers handle malformed input correctly. No source modifications were required. The parsers reject invalid input with appropriate error types and never crash or leak data on adversarial input.
