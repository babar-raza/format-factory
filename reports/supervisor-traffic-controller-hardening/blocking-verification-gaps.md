# Blocking Verification Gaps — Hardening IV

## Gaps That Require Verification (must address in this sprint)

| Gap | Lane | Required Fix |
|---|---|---|
| Skills packet present but `check_cross_stream_consumption.py` may still emit SKILLS_MISSING_PACKET | Lane C | Verify and fix the consumption checker to recognize the current Skills packet |
| Acceleration packets present but consumption status unknown | Lane C | Verify Acceleration packets parse correctly; classify as CONSUMABLE or PARTIAL |
| Routing determinism unproven — never run twice against same inputs | Lane B | Run generator twice; compare semantic hash |
| Mainstream routing handoff is generic — not product-specific with 3 families confirmed | Lane D | Regenerate handoff with FODS+FODT+Netpbm and Skills/Acceleration status |
| Continuation states 3 new states untested under realistic failure fixtures | Lane E | Run 10 fixture scenarios with expected outcomes |
| External-tool detection never proven read-only | Lane F | Prove no .vscode/mcp.json mutation; no tool invocation |

## Key Defect to Diagnose

**Skills packet detection**: The prior sprint's `check_cross_stream_consumption.py` reads replay results from a JSON file to determine Skills breadth. But it doesn't currently read `reports/skills-product-first/mainstream-consumption-packet.json` directly. This means even though the Skills packet now exists on disk, the consumption checker won't find it unless the replay results are updated.

**Resolution**: Update `check_cross_stream_consumption.py` to also look for Skills and Acceleration packets in known filesystem locations, not only in replay results. This is a routing correctness defect.

## Non-Blocking Gaps (acknowledge but do not block on)

- Mainstream `breadth = 2` (needs 3) — addressed via handoff direction, not blocking
- No governed transcripts from Skills yet — acknowledged in handoff; not a routing blocker
- Acceleration ai_draft not yet produced — acknowledged; Acceleration classified as CONSUMABLE_PARTIAL
