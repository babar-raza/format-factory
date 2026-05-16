---
artifact_id: ora-gate1-scoring-packet-v1
format_id: ora
gate: 1
sprint: FORMAT-FACTORY-R18-QUARTER-MILE-ZST-GATE4-GATE5-AND-MULTI-FORMAT-GATE1-SWARM-001
date: "2026-05-16"
status: scored_pending_human_approval
approved_by: null
---

# ORA Gate 1 Scoring Packet

## Status: PENDING HUMAN REVIEW

ORA scored ~6.8 (Borderline). This format is NOT auto-approved.
Borderline scores require human review before Gate 1 approval.
This packet provides the scoring evidence for human decision.

## Identity

| Field | Value |
|-------|-------|
| format_id | ora |
| display_name | OpenRaster Image |
| Extension | .ora |
| MIME type | image/openraster |
| Spec body | freedesktop.org (community) |
| Spec version | OpenRaster 0.0.3 (informal) |
| Structure | ZIP container: stack.xml + PNG image tiles + thumbnail |
| Reference implementations | Krita, MyPaint, GIMP |

## Legal Assessment

| Item | Status |
|------|--------|
| Legal Category | 2 — Permissive community spec |
| Spec accessibility | freedesktop.org, openly published |
| Royalty claims | None (community standard) |
| Patent concerns | None identified |
| Explicit RF designation | Not found — community practice implies open |

Category 2 is conservative. The format has no royalty claims and is implemented by
multiple open source applications (Krita, GIMP, MyPaint) without restriction.
No explicit patent grant exists, but no patent assertions have been documented.

## Spec Availability

| Item | Score |
|------|-------|
| OpenRaster 0.0.3 spec | YES — freedesktop.org |
| Comprehensiveness | MODERATE — community spec, not formal standards body |
| Gaps | Some; reference implementations supplement the spec |
| Spec score | 2/3 |

## Aspose Support Audit

| Item | Status |
|------|--------|
| Aspose product checked | Aspose.Imaging |
| Support level | NOT_SUPPORTED |
| ORA in Aspose.Imaging | Not listed in supported formats |

NOT_SUPPORTED means differentiation potential. However, with a niche format and
limited user base, this advantage is less compelling than for Gnumeric or ABW.

## Scoring (7-Factor Model)

| Factor | Weight | Score | Points | Notes |
|--------|--------|-------|--------|-------|
| Legal Safety | 30% | 2/3 | 20.0 | Cat 2 — permissive community spec |
| Spec Availability | 20% | 2/3 | 13.3 | Community spec with some gaps |
| Parseable Structure | 15% | 2/3 | 13.3 | ZIP + PNG + XML; technically tractable |
| Community Demand | 15% | 1/3 | 6.7 | Krita/MyPaint only; very niche |
| Strategic Track Value | 10% | 1/3 | 4.4 | Image/raster format; limited pipeline reuse |
| Pipeline Reuse | 5% | 1/3 | 2.2 | ZIP handling; PNG; XML; mostly new domain |
| Implementation Risk | 5% | 2/3 | 4.4 | Manageable tech; tile handling new |

**Total: 64.3/100 → Normalized: ~6.8/10**
**Band: BORDERLINE — Human review required**

## Analysis

ORA's score of 6.8 reflects:
- Strong legal (Cat 2) and parseable structure (ZIP + XML + PNG)
- Weak Community Demand (1/3): only used in digital painting apps (Krita, MyPaint)
- Weak Strategic Track Value (1/3): imaging format with limited business pipeline reuse
- Limited Pipeline Reuse (1/3): no existing ORA patterns in current pipeline

The format is technically viable but commercially marginal. The question for human
decision is whether the imaging track expansion justifies the investment, given that:
1. Aspose doesn't support it (differentiation potential exists)
2. User base is narrow (Krita/MyPaint digital painters only)
3. The format competes with TIFF, PSD, XCF in the professional painting space

## Recommendation for Human Decision

**Options:**
1. **Approve Gate 1 with conditions** — proceed if imaging track is strategically desired
2. **Defer** — keep in backlog until FODP/FODG/Gnumeric/ABW are through gates 2-3
3. **Reject** — score too low; limited commercial return

This decision is NOT made by the agent. Human review required.

## No DEC-034 IV Required for Scored-But-Not-Approved State

DEC-034 IV is required before Gate 1 APPROVAL. Since ORA is not approved,
IV is deferred to the sprint where human approval is requested.
When the human approves, the approving sprint's agent must perform DEC-034 IV.

STATUS: SCORED_PENDING_HUMAN_APPROVAL
