# Sample Supervisor Next-Sprint Prompt (R110 excerpt)

## Sprint Focus
CLOSE: Supervisor stream-local authority packaging defects — lane ledger, sample outputs, continuation semantics.

## Stream Authority
- Authoritative state: `reports/supervisor-streams/supervisor/`
- Global `reports/supervisor/` is convenience snapshot only (last-writer-wins)
- Stream-local continuation: `.local/supervisor/streams/supervisor/continuation-signal.json`

## Hard Quota
1. Lane ledger packaged and clears anti-skip
2. 5+ sample outputs packaged
3. Wrong-stream next-sprint classified as archived
4. Stream-local replay proven for all 4 streams
5. YES_WITH_LIMITATIONS semantics consistent

## Non-Negotiable Rules
1. No push without explicit user authorization
2. No commit without explicit user authorization
3. No gate self-approval
4. Format Factory authority is final
5. Stay within supervisor stream boundary
