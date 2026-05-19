---
artifact_id: qoi-gate8-security-report
artifact_type: report-security
path: reports/security/qoi.md
format_id: qoi
product_family: imaging
visibility: internal
publish_allowed: false
generated_by: claude-opus-4-6
generated_at: "2026-05-19"
notes: "QOI Gate 8 security review packet. AWAITING HUMAN SIGN-OFF."
---

# Security Report — QOI Parser

**Format:** QOI (Quite OK Image)
**Gate:** 8 — Security Review (PACKET READY, AWAITING APPROVAL)
**Report date:** 2026-05-19
**Sprint:** R30
**Parser reviewed:** `src/python/qoi/qoi_parser.py` (Gate 4 prototype)
**Parser language:** Python 3 (stdlib only — `struct`)

---

## Reviewer Sign-off

**GATE8_SECURITY_REVIEW: AWAITING_HUMAN_APPROVAL**

---

## Attack Surface Analysis

### 1. Binary Parsing
- Uses `struct.unpack` for fixed-size header (14 bytes). No dynamic allocation from untrusted sizes.
- Pixel decode reads sequential bytes with known op-code patterns.

### 2. Memory Safety
- MAX_FILE_SIZE = 64 MiB. Dimension guards (MAX_DIMENSION = 65536).
- Pixel buffer allocated based on validated width * height * channels.
- Running pixel array fixed at 64 entries (QOI spec).

### 3. Input Validation
- Magic validated ("qoif" 4-byte header). Channels (3/4) and colorspace (0/1) validated.
- End marker (8-byte padding) checked.

### 4. Integer Overflow
- Width * height * channels computed in Python (arbitrary precision). No overflow risk.
- Dimension guards prevent allocation of arrays > 65536 * 65536.

### 5. Denial of Service
- 64 MiB file size limit. Dimension limits. Decode terminates at end-of-data or file boundary.

## Findings

| Finding | Severity | Status |
|---------|----------|--------|
| Crafted dimension overflow | Low | MITIGATED — Python arbitrary precision |
| Malformed op-code loop | Low | MITIGATED — bounds checked |
| Large file DoS | Low | MITIGATED — 64 MiB guard |
| No timeout | Informational | ACCEPTED |

## Recommendation

GATE8_SECURITY_REVIEW: READY_FOR_HUMAN_APPROVAL
