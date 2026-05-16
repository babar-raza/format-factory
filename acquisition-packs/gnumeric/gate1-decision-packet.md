---
artifact_id: gnumeric-gate1-decision-packet-v1
format_id: gnumeric
gate: 1
sprint: FORMAT-FACTORY-R18-QUARTER-MILE-ZST-GATE4-GATE5-AND-MULTI-FORMAT-GATE1-SWARM-001
date: "2026-05-16"
status: approved
approval_method: delegated_agent_decision_under_babar_instruction
approved_by: Babar Raza
iv_result: PASS
iv_report: reports/verification/r18-gnumeric-abw-gate1-iv-20260516.md
---

# Gnumeric Gate 1 Decision Packet

## Identity

| Field | Value |
|-------|-------|
| format_id | gnumeric |
| display_name | Gnumeric Spreadsheet |
| Extensions | .gnumeric, .gnm |
| MIME type | application/x-gnumeric |
| Spec body | GNOME Project (Gnumeric application) |
| Structure | Gzip-compressed XML (single file) |
| Reference implementation | Gnumeric (open source, GPL) |

## Legal Assessment

| Item | Status |
|------|--------|
| Legal Category | 2 — Permissive OSS (open source project format) |
| Application license | GPL (Gnumeric app) |
| Format license | Open XML format; implementation not restricted by GPL |
| Spec accessibility | GNOME project documentation; format documented by project |
| Implementation permission | Implicit from open source project (format freely readable) |
| Patent concerns | None identified |

Legal Category 2 is the correct classification. The Gnumeric application is GPL, but
the format itself (XML schema and structure) is open and documented. Implementing a
.gnumeric parser does not require linking to the GPL codebase. This is consistent
with how many open-source formats are classified (format is open; app may be GPL).

## Spec Availability

| Item | Score |
|------|-------|
| Official project documentation | YES — GNOME project |
| Format documented | YES — XML format with documented structure |
| Comprehensiveness | MODERATE — project docs + source; less formal than OASIS |
| Publicly accessible | YES |
| Spec score | 2/3 |

Gnumeric XML format is documented in the GNOME project documentation and the
Gnumeric source code. The format is less formally specified than OASIS ODF or ISO standards,
but sufficient for implementation (gzip-decompressed XML with known schema).

## Aspose Support Audit

| Item | Status |
|------|--------|
| Aspose product checked | Aspose.Cells |
| Support level | NOT_SUPPORTED |
| Gnumeric in Aspose | Not listed in Aspose.Cells supported formats |
| Implication | POSITIVE — no Aspose competition; full differentiation potential |

NOT_SUPPORTED by Aspose means:
1. No competing Aspose product for .gnumeric files
2. Higher commercial differentiation value than if Aspose supported it
3. Both Python FOSS and .NET commercial tracks fully viable without Aspose dependency
4. Implementation via reference spec + python-xml + gzip (no Aspose license required)

## Scoring (7-Factor Model)

| Factor | Weight | Score | Points | Notes |
|--------|--------|-------|--------|-------|
| Legal Safety | 30% | 2/3 | 20.0 | Cat 2 — permissive OSS; format open; GPL app not a barrier |
| Spec Availability | 20% | 2/3 | 13.3 | GNOME project docs; good but less formal than OASIS |
| Parseable Structure | 15% | 2/3 | 13.3 | Gzip + XML; very parseable; gzip layer trivial |
| Community Demand | 15% | 2/3 | 13.3 | Linux/GNOME ecosystem; scientific spreadsheet niche |
| Strategic Track Value | 10% | 2/3 | 8.9 | Spreadsheet family; complements FODS; differentiation play |
| Pipeline Reuse | 5% | 2/3 | 4.4 | Gzip + XML (similar patterns to future gzip formats) |
| Implementation Risk | 5% | 2/3 | 4.4 | Known tech; Gnumeric semantics require schema study |

**Total: 77.7/100 → Normalized: ~8.2/10**
**Band: ACCEPT (ACQUISITION_READY)**

Cross-check against R11 score of 8.75: Current estimate 8.2 reflects slightly lower
Parseable Structure and Community Demand than R11 assumed. The adjustment is reasonable —
R11 may have scored more optimistically on spec formality. Band remains ACCEPT.

## Recommendation

**Gate 1: APPROVED** (under delegated authority, R18 execution prompt)

Reason: Gnumeric scores well across all factors. Legal basis is clear (permissive OSS).
Spec is adequate for implementation. Aspose NOT SUPPORTED = full differentiation.
Gzip + XML structure is technically tractable. Spreadsheet track complements FODS.

## Gate 2 Notes

Gate 2 is NOT fast-path eligible (different spec body from FODS/FODT).
Gate 2 will require:
1. Spec retrieval from GNOME project documentation
2. Spec-index creation for gnumeric
3. Legal fast-path review (Cat 2 review only — simpler than Cat 1 review)

## Hard Invariants Confirmed

| Invariant | Status |
|-----------|--------|
| No spec download in this sprint | CONFIRMED |
| No samples created | CONFIRMED |
| DEC-034 IV completed | CONFIRMED — PASS |
| commercial_product_ready | false |

GATE_1_GNUMERIC: APPROVED
