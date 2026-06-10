# Cross-Stream Adoption Enforcement (Skills R105 Train F)

## Purpose
Make Mainstream, Supervisor, and Acceleration consume Skills enforcement in the next cycle.

## R104 Enforcement Packages — Status

| Package | Created R104 | R105 Update |
|---------|-------------|-------------|
| mainstream-enforcement.yaml | Yes | No change needed — rules are correct |
| supervisor-enforcement.yaml | Yes | Updated: transcript grading matrix now tested (13 tests) |
| acceleration-enforcement.yaml | Yes | No change needed — rules are correct |

## R105 Advancement: Tested Enforcement Rules

R104 produced enforcement packages but no tests validated the rules. R105 adds:

1. **Transcript grade mapping tests (13):** Prove that valid/invalid/missing transcripts map to correct grades
2. **Command validation integration:** 23/23 commands pass, orphan count reduced
3. **Registry consistency:** 19 active, 2 draft, 1 newly registered orphan

## Adoption Checklists (per-stream)

See `adoption-checklists/` for stream-specific checklists.

## Next Prompt Fragments

Each stream's next prompt should include the adoption requirement:
- Mainstream: "All product source changes require skill_id + transcript + ledger"
- Supervisor: "When skill_id present in work item, validate transcript"
- Acceleration: "Route gaps through governed skills, not ad-hoc execution"

## Train F Decision: ACCEPT_WITH_CAVEATS
Enforcement packages exist from R104 and are now backed by tests. Full pipeline integration (auto-enforcement in grading) deferred to R106.
