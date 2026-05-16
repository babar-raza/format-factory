---
artifact_id: fodg-gate1-decision-packet-v1
format_id: fodg
gate: 1
sprint: FORMAT-FACTORY-R18-QUARTER-MILE-ZST-GATE4-GATE5-AND-MULTI-FORMAT-GATE1-SWARM-001
date: "2026-05-16"
status: approved
approval_method: delegated_agent_decision_under_babar_instruction
approved_by: Babar Raza
iv_result: PASS
iv_report: reports/verification/r18-fodp-fodg-gate1-iv-20260516.md
---

# FODG Gate 1 Decision Packet

## Identity

| Field | Value |
|-------|-------|
| format_id | fodg |
| display_name | Flat OpenDocument Drawing |
| Extension | .fodg |
| MIME type | application/vnd.oasis.opendocument.graphics-flat-xml |
| Spec body | OASIS |
| Spec version | ODF 1.3 (Part 1: Drawing/Graphics Application) |
| Structure | Single-file flat XML (no ZIP container) |
| Relationship | Same spec family as FODS, FODT, FODP |

## Legal Assessment

| Item | Status |
|------|--------|
| Legal Category | 1 — OASIS Royalty-Free on Limited Terms |
| IPR Disclosures | None (same OASIS RF policy as FODS/FODT) |
| Patent grant | OASIS RF grants royalty-free implementation rights |
| Approved precedents | FODS Gate 1 (2026-05-04), FODT Gate 1 (both OASIS RF Cat 1) |

Legal basis is identical to FODS, FODT, and FODP which have already passed Gate 1.
No new legal analysis required; fast-path legal clearance applies.

## Spec Availability

| Item | Score |
|------|-------|
| Official published specification | YES — OASIS ODF 1.3 |
| Comprehensiveness | HIGH — same OASIS spec |
| Publicly accessible | YES |
| Already cached | YES — FODS/FODT Gate 2 cached ODF 1.3 |
| Spec score | 3/3 |

## Aspose Support Audit

| Item | Status |
|------|--------|
| Aspose product | Aspose.Imaging |
| Support level | LOAD_ONLY |
| Load | ODG (OpenDocument Graphics) load confirmed |
| Save | Save as FODG not confirmed (limited support) |
| Commercial note | LOAD_ONLY — reduces commercial differentiation vs FULL_ROUND_TRIP |

**LOAD_ONLY is not a Gate 1 blocker.** Gate 1 assesses legal safety, spec availability,
and preliminary viability. Aspose support level affects commercial track planning (Gate 11)
but does not disqualify the format. A Python FOSS track may still provide value via the
open reference implementation approach, independent of Aspose.

Note: The open source ODF ecosystem (LibreOffice, etc.) provides full round-trip support
for .fodg. Python track (python-odfpy or similar) may support round-trip independently
of Aspose. This is assessed at Gate 8+ for implementation.

## Scoring (7-Factor Model)

| Factor | Weight | Score | Points | Notes |
|--------|--------|-------|--------|-------|
| Legal Safety | 30% | 3/3 | 30.0 | OASIS RF Cat 1 — maximum legal clearance |
| Spec Availability | 20% | 3/3 | 20.0 | OASIS ODF 1.3 comprehensive spec |
| Parseable Structure | 15% | 2/3 | 13.3 | Flat XML — parseable; drawing semantics moderate |
| Community Demand | 15% | 1/3 | 6.7 | Specialized drawing/diagram domain; niche use |
| Strategic Track Value | 10% | 2/3 | 8.9 | ODF family completion; drawing track new |
| Pipeline Reuse | 5% | 3/3 | 5.0 | Full reuse: same OASIS spec as FODS/FODT |
| Implementation Risk | 5% | 2/3 | 4.4 | Known XML/ODF; drawing schema new domain |

**Total: 88.3/100 → Normalized: ~8.1/10**
**Band: ACCEPT (ACQUISITION_READY)**

Note: Score lower than FODP primarily due to Community Demand (1/3 vs 2/3) —
drawings are a more specialized use case than presentations.

## Recommendation

**Gate 1: APPROVED** (under delegated authority, R18 execution prompt)

Reason: FODG scores well on legal, spec, and pipeline reuse. Drawing format completes
the ODF Flat XML family (FODS + FODT + FODP + FODG). Community demand is limited but
not disqualifying. LOAD_ONLY Aspose support noted — Python track may achieve round-trip
independently. ODF family coherence is a strong strategic argument.

## Commercial Track Note

The LOAD_ONLY Aspose support is a risk factor for the .NET commercial track.
Options to be assessed at Gate 6+:
1. Python FOSS track: full round-trip via python-odfpy (not Aspose dependent)
2. .NET commercial track: investigate Aspose.Slides for drawing support, or conversion path
3. Human decision required at Gate 6 on commercial track strategy for FODG

## Gate 2 Fast-Path Authorization

FODG is eligible for Gate 2 fast-path (same OASIS ODF 1.3 legal/spec basis as FODS/FODT).
Gate 2 fast-path requires separate authorization.

## Hard Invariants Confirmed

| Invariant | Status |
|-----------|--------|
| No spec download in this sprint | CONFIRMED — spec already cached |
| No samples created | CONFIRMED — Gate 3 not authorized |
| DEC-034 IV completed | CONFIRMED — PASS (10/10) |
| commercial_product_ready | false (unchanged) |

GATE_1_FODG: APPROVED
