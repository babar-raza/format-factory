---
visibility: generated
generated_by: codex
---

# R90 Risk Register

| Risk | Severity | Control |
|---|---|---|
| Prior supervisor outputs are dirty | medium | Preserve and classify before integration |
| R89 source edits predate governed ledger | high | Audit and backfill as `BACKFILLED_PRE_GOVERNANCE` |
| Canonical next sprint is weaker than latest worker prompt | high | Harden generator and rerun autonomous-cycle |
| Product source edit occurs before governed path exists | high | Keep `src/` read-only until registry, commands, and ledger validation are installed |
| Evidence repair consumes sprint | medium | Repair only validator defects that block truthful autonomous continuation |
