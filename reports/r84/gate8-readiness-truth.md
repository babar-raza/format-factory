# R84 Train P: Gate 8 Readiness Truth

**Sprint:** FORMAT-FACTORY-R84
**Train:** P
**Date:** 2026-05-31
**Status:** COMPLETE

## Gate 8 Matrix

| Format   | Gate 8 Status       | Blocker                                          |
|----------|---------------------|--------------------------------------------------|
| ODS      | not_approved        | Security test coverage insufficient              |
| ODT      | not_approved        | Security test coverage insufficient              |
| QOI      | not_approved        | Needs external spec compliance test              |
| XCF      | not_approved        | File structure validation incomplete             |
| DIF      | not_approved        | Boundary fuzz testing not complete               |
| PPM      | not_approved        | Parser too new (R84 Train M); needs full G7      |

Gate 8 matrix file: `gate-readiness/gate8-matrix.yaml`
(updated with R84 PPM addition)

## New Security Tests

File: `tests/security/test_r84_gate8_security_assertions.py`

1. `test_ods_no_external_entity_expansion` — XXE guard for ODS ZIP+XML
2. `test_odt_zip_bomb_guard` — decompression size limit for ODT

## Approval Status

**gate_8_approved: false** for all formats listed above.
No format is approved for Gate 8 in R84.

## Result

PASS — Gate 8 matrix documented; 2 new security tests added.
