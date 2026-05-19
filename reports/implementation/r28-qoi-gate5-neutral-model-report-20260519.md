# QOI Gate 5 — Neutral Model and API Hardening Report
# Sprint: FORMAT-FACTORY-R28-GATE5-GATE7-ORACLE-FUZZ-XCF-ZPAQ-G11-C9-PUBLICATION-HARDENING-001
# Date: 2026-05-19

## Gate 5 Status: PASS

## Changes

### Source: src/python/qoi/qoi_parser.py
- Added `UNSUPPORTED_FEATURES` frozenset (10 features): animation, multi_frame, metadata_embedding, icc_profiles, exif, encoding, streaming_decode, partial_decode, thumbnail_extraction, color_management
- Added `SUPPORTED_FEATURES` frozenset (15 features): header_parse, full_pixel_decode, op_rgb, op_rgba, op_index, op_diff, op_luma, op_run, 3_channel_mode, 4_channel_mode, srgb_colorspace, linear_colorspace, end_marker_validation, size_guard, probe_without_decode
- Added `get_capabilities()` function returning neutral model dict

### Tests: tests/python/qoi/test_qoi_gate5_neutral_model.py
- 17 new tests (9 capability + 8 edge-case)
- All 17 PASS

### Edge Cases Covered
- 3-channel mode (RGB without alpha)
- Colorspace=1 (all-linear)
- Zero width (raises QoiInvalidHeaderError)
- Zero height (raises QoiInvalidHeaderError)
- Invalid channels (5 — raises QoiInvalidHeaderError)
- Invalid colorspace (2 — raises QoiInvalidHeaderError)
- Dict API error fields (error_type present)
- Run-length decode (OP_RUN with default pixel)

## No Gate 5 Overclaim
- commercial_product_ready: false
- Gate 5 does NOT claim production readiness
