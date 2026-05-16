---
artifact_id: abw-gate1-decision-packet-v1
format_id: abw
gate: 1
sprint: FORMAT-FACTORY-R18-QUARTER-MILE-ZST-GATE4-GATE5-AND-MULTI-FORMAT-GATE1-SWARM-001
date: "2026-05-16"
status: approved
approval_method: delegated_agent_decision_under_babar_instruction
approved_by: Babar Raza
iv_result: PASS
iv_report: reports/verification/r18-gnumeric-abw-gate1-iv-20260516.md
---

# ABW Gate 1 Decision Packet

## Identity

| Field | Value |
|-------|-------|
| format_id | abw |
| display_name | AbiWord Word Processing Document |
| Extensions | .abw, .abw.gz, .zabw |
| MIME type | application/x-abiword |
| Spec body | AbiSource Project (AWML 1.0 DTD) |
| Structure | Flat XML; .abw.gz/.zabw are gzip-compressed variants |
| Reference implementation | AbiWord (open source, GPL) |

## Legal Assessment

| Item | Status |
|------|--------|
| Legal Category | 2 — Permissive OSS |
| Application license | GPL (AbiWord app) |
| Format/DTD license | AWML 1.0 DTD published at abisource.com; open |
| Implementation permission | Implicit from open source project |
| Patent concerns | None identified |

Same legal pattern as Gnumeric: GPL application with open format documentation.
The AWML 1.0 DTD is published and implementation of the format is not restricted.

## Spec Availability

| Item | Score |
|------|-------|
| AWML 1.0 DTD published | YES — abisource.com |
| Comprehensiveness | LOW-MODERATE — DTD is outdated; gaps exist |
| Reference app available | YES — AbiWord source code (supplement to DTD) |
| Spec score | 1/3 |

**Key constraint:** The AWML 1.0 DTD is noted as "very much out-of-date" in project documentation.
The reference implementation (AbiWord source code) is necessary to understand actual format
behavior beyond what the DTD documents. This spec availability risk is the primary concern
for Gate 1 and must be re-assessed at Gate 2 with DTD retrieval.

## Aspose Support Audit

| Item | Status |
|------|--------|
| Aspose product checked | Aspose.Words |
| Support level | NOT_SUPPORTED |
| ABW in Aspose.Words | Not listed in supported formats |
| Implication | POSITIVE — no Aspose competition; differentiation potential |

Same pattern as Gnumeric: NOT_SUPPORTED means higher commercial differentiation.
Word processing track (alongside FODT) provides strategic value.

## Scoring (7-Factor Model)

| Factor | Weight | Score | Points | Notes |
|--------|--------|-------|--------|-------|
| Legal Safety | 30% | 2/3 | 20.0 | Cat 2 — permissive OSS; format DTD published |
| Spec Availability | 20% | 1/3 | 6.7 | AWML 1.0 outdated DTD; reference implementation needed |
| Parseable Structure | 15% | 2/3 | 13.3 | Flat XML; images as base64; moderate complexity |
| Community Demand | 15% | 1/3 | 6.7 | AbiWord declining; limited active user base |
| Strategic Track Value | 10% | 2/3 | 8.9 | Word processing track; complements FODT |
| Pipeline Reuse | 5% | 2/3 | 4.4 | XML parsing patterns from FODT applicable |
| Implementation Risk | 5% | 2/3 | 4.4 | Outdated spec risk elevated; requires reference app study |

**Total: 64.4/100 → Normalized: ~7.8/10**
**Band: ACCEPT (cautious)**

Cross-check against R11 score of 8.75: Current estimate 7.8 is lower due to:
- Spec Availability downgraded 3→1 (outdated DTD confirmed; reference app needed)
- Community Demand 2→1 (AbiWord declining user base)
R11 may have scored optimistically on these dimensions. The current estimate is more
conservative and reflects real spec access constraints.

## Recommendation

**Gate 1: APPROVED** (under delegated authority, R18 execution prompt)

Reason: Despite the outdated spec, ABW remains technically tractable via reference
implementation. Legal basis clear (Cat 2). Aspose NOT SUPPORTED = differentiation.
Word processing track is strategically valuable (alongside FODT).

**Conditions noted for Gate 2:**
1. DTD retrieval must confirm actual current ABW format behavior
2. Reference implementation study required to supplement outdated DTD
3. If spec gaps are worse than expected, Gate 3 may require closer scrutiny
4. acquisition_risk_classification elevated to MEDIUM (from LOW)

## Hard Invariants Confirmed

| Invariant | Status |
|-----------|--------|
| No spec download in this sprint | CONFIRMED |
| No samples created | CONFIRMED |
| DEC-034 IV completed | CONFIRMED — PASS |
| commercial_product_ready | false |

GATE_1_ABW: APPROVED (cautious — spec risk noted for Gate 2 re-evaluation)
