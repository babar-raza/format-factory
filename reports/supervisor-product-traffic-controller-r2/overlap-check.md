# Overlap Check — Supervisor Product Traffic Controller R2

## Serialized (Shared) Files
The following files are written by only one lane:

| File | Owner Lane | Concurrent Writers |
|------|-----------|-------------------|
| tools/supervisor/generate_stream_routing_packet.py | F | none |
| tools/supervisor/check_cross_stream_consumption.py | G | none |
| reports/supervisor-streams/mainstream/routing-packet.json | F | none |
| reports/supervisor-streams/skills/routing-packet.json | F | none |
| reports/supervisor-streams/acceleration/routing-packet.json | F | none |
| reports/supervisor-streams/supervisor/routing-packet.json | F | none |
| .local/evidences/supervisor-product-traffic-controller-r2/evidence-declaration.yaml | COORD (closeout) | none |
| reports/supervisor/next-sprint.md | J (after IV) | none |

## Lane-Local Files (no conflicts)
All `reports/supervisor-product-traffic-controller-r2/` files are lane-local except the shared list above.

## Verdict
**OVERLAP_FREE** — No two lanes write the same file concurrently.
Serialized shared files are assigned to exactly one lane.
