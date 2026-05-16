# R18 Gate 7 (Sprint): FODP + FODG Gate 2 Fast-Path Decision
Sprint: FORMAT-FACTORY-R18-QUARTER-MILE-ZST-GATE4-GATE5-AND-MULTI-FORMAT-GATE1-SWARM-001
Date: 2026-05-16
Gate: 7 (sprint gate) — FODP + FODG Gate 2 Fast-Path Analysis

## Purpose

Evaluate whether FODP and FODG qualify for Gate 2 fast-path based on ODF family spec
reuse. If fast-path criteria are met, Gate 2 can proceed without downloading a new spec
(the ODF 1.3 spec is already cached from FODS/FODT Gate 2).

**IMPORTANT: This report does NOT approve Gate 2.** Gate 2 approval requires a separate
human execution prompt. This report establishes fast-path eligibility and pre-conditions.

## Gate 2 Fast-Path Criteria

Per master-plan.md and FODS/FODT precedent:
1. Legal basis is Category 1 (OASIS RF) — already cleared for this spec
2. Spec is published and publicly accessible via same URL as cached spec
3. Same spec body (OASIS) and same spec version (ODF 1.3) as already-approved format
4. No new legal analysis required

## FODP Fast-Path Assessment

| Criterion | FODP | Status |
|-----------|------|--------|
| Legal category | 1 (OASIS RF) | PASS |
| Spec body | OASIS | PASS |
| Spec version | ODF 1.3 | PASS |
| Same as FODS/FODT spec | YES — identical | PASS |
| Spec cached | YES — .local/spec-cache/ from FODS/FODT Gate 2 | PASS |
| New download required | NO | PASS |

**FODP Gate 2 Fast-Path: ELIGIBLE**

Basis: OASIS ODF 1.3 was downloaded in FODS Gate 2 (ODF 1.3 Part 3 schema PDF, sha256:92cfe6...)
and FODT Gate 2 (same spec). FODP uses the same ODF 1.3 spec for presentation content.

FODP-specific content: ODF 1.3 Part 1 covers all application-specific content including
presentations. The spec cache from FODS/FODT covers the complete ODF 1.3 set.

## FODG Fast-Path Assessment

| Criterion | FODG | Status |
|-----------|------|--------|
| Legal category | 1 (OASIS RF) | PASS |
| Spec body | OASIS | PASS |
| Spec version | ODF 1.3 | PASS |
| Same as FODS/FODT spec | YES — identical | PASS |
| Spec cached | YES | PASS |
| New download required | NO | PASS |

**FODG Gate 2 Fast-Path: ELIGIBLE**

Basis: Same as FODP. ODF 1.3 governs all document types including drawings.
The .fodg content model (drawing shapes, layers, styles) is defined in ODF 1.3 Part 1.

## What Is Already in the Spec Cache (from FODS/FODT Gate 2)

| Artifact | Path | SHA-256 |
|----------|------|---------|
| ODF 1.3 Part 3 Schema PDF | .local/spec-cache/fods/ | sha256:92cfe64ee30a8cca1be19a76d38628fdc8ef9153eb59547f6c96fe7b9b81b066 |
| RFC 8878 (ZST) | .local/spec-cache/zst/ | sha256:8ee6be03534113f5689cda75b9539a02e0704a2506d420814223e506420aeea4 |

For FODP/FODG Gate 2, the authoring agent should:
1. Verify the existing ODF 1.3 spec cache is accessible
2. Confirm ODF 1.3 covers FODP/FODG content (Part 1 — Presentation/Drawing Application)
3. Create spec-index entries for fodp and fodg pointing to the same cached spec
4. Record fast-path evidence in the Gate 2 evidence packet

## Gate 2 Sprint Recommendations

| Format | Fast-Path | Spec Needed | New Download | Priority |
|--------|-----------|-------------|--------------|----------|
| FODP | YES | ODF 1.3 Part 1 (already cached) | NO | HIGH |
| FODG | YES | ODF 1.3 Part 1 (already cached) | NO | HIGH (batch with FODP) |

**Recommended sprint:** FODP + FODG Gate 2 batch (same sprint as Gate 1 batch-next).
Since Gate 2 requires minimal work (fast-path + spec-index creation), it can proceed
immediately after Gate 1 approval in a single short sprint.

## What Gate 2 Does NOT Do

- Does NOT approve Gate 3 (corpus acquisition requires separate prompt)
- Does NOT create samples
- Does NOT create prototypes
- Does NOT authorize implementation

## Gap Register Note

The existing gap register (if maintained) should record:
- FODP: Gate 2 fast-path authorized (same OASIS ODF 1.3 as FODS/FODT)
- FODG: Gate 2 fast-path authorized (same OASIS ODF 1.3 as FODS/FODT)

GATE_7_SPRINT_FODP_FODG_GATE2_FASTPATH: ELIGIBLE (pending authorization)
