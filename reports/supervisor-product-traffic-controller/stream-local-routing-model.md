# Stream-Local Routing Model

## Sprint
`FORMAT-FACTORY-SUPERVISOR-PRODUCT-TRAFFIC-CONTROLLER-INTEGRATION-001`

## Authority Model

Each stream has local authority over its own routing packet. The Supervisor reviews all streams
and produces product-specific guidance. Stream local routing packets are written to:
`reports/supervisor-streams/{stream}/routing-packet.json`

## Routing Packet Status

| Stream | Status | Decision | Breadth | Overhead | Flag |
|--------|--------|----------|---------|---------|------|
| Mainstream | PRESENT | CONTINUE_WITH_LIMITATIONS | 2 | 0 | PARTIAL_FEW_FAMILIES |
| Skills | PRESENT | CONTINUE | 0 | 2 | SKILLS_MISSING_PACKET |
| Acceleration | PRESENT | CONTINUE | 1 | 1 | None |
| Supervisor | PRESENT | CONTINUE_WITH_LIMITATIONS | 0 | 3 | External gates only |

## Routing Rules

1. **Mainstream CLEAN_PASS**: breadth ≥ 3, source_diffs ≥ 3, governed_transcripts ≥ 3, raw_logs ≥ 3, capability_matrix_deltas ≥ 3, repair < product
2. **PARTIAL_FEW_FAMILIES**: breadth < 3 → route to gap-filling sprint targeting 3+ families
3. **SKILLS_MISSING_PACKET**: Skills machinery_overhead ≥ 2 AND not consumed by Mainstream → flag; Mainstream must declare consumption next sprint
4. **Supervisor overhead=3**: Expected when building infrastructure; wiring sprint resolves this
5. **External gate gaps**: Cannot be unblocked autonomously; escalate to human authority

## Cross-Stream Consumption Rules

- Skills governed transcripts must be PRODUCED by Skills AND CONSUMED by Mainstream to count
- Acceleration AI outputs must be marked `ai_draft` AND explicitly consumed by Mainstream
- Neither consumption currently satisfied → next Mainstream sprint must address both

## Stream Fallback Policy

When Skills/Acceleration report directories are absent:
- Fallback to local coordinator authority
- No cross-stream packet consumption can be claimed
- Routing packets are generated from replay data only
- Flag: FALLBACK_LOCAL_COORDINATOR
