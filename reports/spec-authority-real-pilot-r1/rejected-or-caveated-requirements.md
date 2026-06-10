# Rejected or Caveated Requirements
Pilot: FORMAT-FACTORY-SPECIFICATION-AUTHORITY-LAYER-REAL-PILOT-R1-001
Generated: 2026-06-05

## Summary

No requirements were ANTI_BYPASS_REJECTED during Pilot R1. All 46 candidate requirements
passed the anti-bypass checks (registered source_id, non-empty text_fragment).

10 requirements from `src-dif-empirical` are classified `EMPIRICAL_ONLY` and carry a
mandatory downstream caveat.

## EMPIRICAL_ONLY Requirements (10 total)

These requirements are NOT rejected — they are valid as empirical observations. However,
they MUST NOT be used as authoritative spec evidence in capability claims.

| req_id | keyword | text_fragment (truncated) |
|--------|---------|--------------------------|
| REQ-src-dif-empirical-s0001-0001 | MUST | A DIF file MUST begin with the TABLE keyword... |
| REQ-src-dif-empirical-s0002-0001 | MUST | The VECTORS record MUST appear after TABLE... |
| REQ-src-dif-empirical-s0003-0001 | MUST | The DATA block MUST be terminated by an EOD... |
| REQ-src-dif-empirical-s0001-0002 | MUST | Each record type MUST be on its own line... |
| REQ-src-dif-empirical-s0002-0002 | MUST | TUPLES value MUST equal the number of data rows... |
| REQ-src-dif-empirical-s0003-0002 | SHOULD | String values SHOULD be enclosed in double quotes... |
| REQ-src-dif-empirical-s0004-0001 | MUST | The BOT record MUST appear at the start of each tuple... |
| REQ-src-dif-empirical-s0004-0002 | MUST | Numeric values MUST be unquoted... |
| REQ-src-dif-empirical-s0005-0001 | MUST | The EOD record MUST be the last record in the file... |
| REQ-src-dif-empirical-s0005-0002 | SHOULD | Integer values SHOULD NOT have decimal points... |

**Downstream rule:** Any capability claim that references these requirements MUST annotate
with `authority_status: EMPIRICAL_ONLY` and MUST NOT assert conformance to a spec.

## ACCEPTED_WITH_CAVEAT Requirements (24 total — caveated, not rejected)

Netpbm requirements (11): caveat = `public_domain_spec_no_formal_body`
FODS requirements (13): caveat = `odf_standard_license_unconfirmed`

These requirements may be used in capability claims with caveat annotation.

## Anti-Bypass Rejected

**None.** All 46 candidates had valid registered source_ids and non-empty text_fragments.

## Verdict

`NO_REJECTIONS — 10_EMPIRICAL_CAVEATS_DOCUMENTED — 24_ACCEPTED_WITH_CAVEAT`
