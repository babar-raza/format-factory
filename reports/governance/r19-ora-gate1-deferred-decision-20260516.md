# R19 ORA Gate 1 Deferred Decision
Sprint: FORMAT-FACTORY-R19-HIGH-THROUGHPUT-ACQUISITION-TRAIN-001
Date: 2026-05-16
Gate: 14 (R19) — ORA Final Delegated Decision

## Decision

**DEFERRED_BORDERLINE**

## Scoring Summary

| Field | Value |
|-------|-------|
| Format | OpenRaster Image (.ora) |
| Score | 6.8/10 |
| Accept threshold | 7.0 |
| Band | Borderline |
| Decision | DEFERRED |

## Rationale

1. Score 6.8 is below the 7.0 automatic-accept threshold
2. No new evidence has emerged since R18 that would change the score:
   - Community demand: Still limited to Krita/MyPaint ecosystem
   - Spec body: Still informal (freedesktop.org community spec, not OASIS/IETF)
   - Aspose NOT_SUPPORTED: Confirmed (potential differentiation but niche market)
3. R19 execution prompt explicitly states: "Default should be DEFER_ORA if still borderline"
4. This is an agent-actionable decision per Gate 2 normalization (r19-delegated-decision-normalization)

## Score Breakdown (R18)

| Criterion | Score | Notes |
|-----------|-------|-------|
| Technical clarity | Medium | ZIP+PNG+XML structure documented |
| Spec formality | Low | Informal community spec |
| Community demand | Medium-Low | Krita/MyPaint only |
| Legal basis | Medium | Category 2 (permissive community) |
| Aspose differentiation | High | NOT_SUPPORTED = differentiation |
| Market opportunity | Low | Niche imaging segment |
| Overall | 6.8/10 | Borderline — below 7.0 threshold |

## What DEFER Means

- ORA remains in acquisition backlog
- Gate 1 status: `deferred_borderline`
- No further gates executed
- Can be re-evaluated if:
  - ORA score improves (e.g., new formal spec body, wider adoption)
  - Explicit Babar Raza instruction to override DEFER
  - Market evidence changes (e.g., major software adopting ORA)

## What DEFER Does NOT Mean

- DEFER is not BLOCKED — ORA can be re-scored in a future sprint
- DEFER is not permanent — it reflects current scoring, not a categorical rejection
- DEFER does not change `commercial_product_ready` (remains false, gate 1 not passed)

## Alternatives Considered

| Option | Assessment |
|--------|-----------|
| ACCEPT_6.8_OVERRIDE | REJECTED — sprint prompt is explicit: default DEFER if borderline |
| REQUEST_MORE_EVIDENCE | REJECTED — no actionable evidence source identified |
| BLOCK_PERMANENTLY | REJECTED — score may improve; BLOCK is too strong |
| DEFER | ACCEPTED — correct per scoring rules and sprint prompt |

## Registry Updates

- ora.gates.gate_1.status: scored_pending_human_approval → deferred_borderline

GATE_14_ORA_DECISION: DEFERRED_BORDERLINE (score 6.8 < 7.0 threshold)
