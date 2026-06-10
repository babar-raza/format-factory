# Acceleration Gap Analysis — R99

## Current Acceleration Layer State

The acceleration layer exists as a set of loosely connected scripts in `tools/supervisor/`.
It lacks:

1. **Lane execution recording** — no `record_lane_execution.py` exists
2. **Sprint learning feedback loop** — `agent-learning-notes.md` is manual today
3. **Stream-aware gap selection** — `select_poc_gaps.py` selects all gaps at once, not per-stream
4. **Skill router integration with registry** — `choose_skill_or_handoff.py` uses hardcoded rules, not the skill registry
5. **Package/install proof automation** — `/package-install-proof` skill exists but no standalone tool
6. **Evidence packaging quick-path** — agents must remember multi-step materialization sequence

## Gaps to Close in This Sprint

| Gap ID | Description | Train |
|--------|-------------|-------|
| ACCEL-GAP-001 | No lane execution recorder | E |
| ACCEL-GAP-002 | Gap selector not stream-aware | C |
| ACCEL-GAP-003 | Skill router doesn't read skill registry | D |
| ACCEL-GAP-004 | No sprint learning generator tool | F |
| ACCEL-GAP-005 | No package/install proof tool | H |
| ACCEL-GAP-006 | Evidence materialization not streamlined | G |
| ACCEL-GAP-007 | Acceleration layer not documented as system | B |
| ACCEL-GAP-008 | Manual processes not inventoried | A |

## Out of Scope

- Product implementation (FODS/FODT/Netpbm features)
- Supervisor internals (autonomous_cycle.py core logic)
- Gate approvals
- Publication/push
