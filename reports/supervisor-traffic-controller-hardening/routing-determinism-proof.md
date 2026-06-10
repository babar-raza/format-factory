# Routing Determinism Proof — Hardening IV

## Method

Ran `generate_stream_routing_packet.py` twice with identical inputs and compared semantic output (timestamps stripped).

## Inputs
- Replay: `[{"stream":"mainstream","product_velocity_score":{"product_breadth_score":2,"machinery_overhead_score":0},...}]`
- Gaps: `reports/supervisor-streams/mainstream/routing-packet.json`

## Comparison

| Output File | Run 1 | Run 2 | Match |
|---|---|---|---|
| `stream_decision.json` | `CONTINUE_WITH_LIMITATIONS` | `CONTINUE_WITH_LIMITATIONS` | MATCH |
| `product_velocity_score.json` | breadth=2, overhead=0 | breadth=2, overhead=0 | MATCH |
| `false_pass_false_stop_assessment.json` | false_pass=False | false_pass=False | MATCH |

**DETERMINISTIC: True**

## Semantic Hash Method

Fields excluded from comparison: `generated_at`, `timestamp`
Fields included: all routing decisions, classification, breadth scores, selected gaps

## Ordering Stability

Selected product gaps are sorted by `priority_score` (descending) then `gap_id` (alphabetical) for tie-breaking. This ensures deterministic ordering regardless of filesystem iteration order.

## Crash Safety

Tested with empty gaps input → `CONTINUE_WITH_LIMITATIONS` decision returned, no crash.
Missing replay fields default to safe values (0 breadth, 0 overhead).

## Verdict

**ROUTING_IS_DETERMINISTIC** — same input always produces same routing decision and selected families.
