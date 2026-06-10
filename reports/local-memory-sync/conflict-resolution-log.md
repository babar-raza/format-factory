# Conflict Resolution Log
# Sprint: FORMAT-FACTORY-LOCAL-MEMORY-GOVERNANCE-SYNC-20260604-001

## Conflicts Found and Resolved

### Conflict 1: Stream State Table (master plan §43.7 vs. memory section 6)

**Old position (master plan §43.7, 2026-06-03):**
| Skills | R112 | Strong milestone. Next: full live cycle, stream convergence, MCP readiness. |
| Supervisor | R109 | Useful, not fully autonomous. Next: ledger, sample outputs, replay closure. |

**New position (memory, 2026-06-04):**
- Supervisor: bundle 69 accepted, 53 tests, routing packets built, needs hardening IV
- Skills: bundle 70 accepted, 72 tests, FODS CSV packet built, needs hardening IV

**Resolution:** Added Section 44.6 with updated stream state table. Section 43.7 preserved as historical (labeled 2026-06-03). No contradiction — timeline is clear.

### Conflict 2: Mainstream Status

**Old implied:** Mainstream may run after R113 breadth sprint.

**New position (memory section 8):** Mainstream DEFERRED until Supervisor + Skills + Acceleration each have independent hardening proof.

**Resolution:** Section 44.4 states hardening sequence explicitly. Mainstream state file updated to DEFERRED. Section 43.7 preserved as historical context.

### Conflict 3: Supervisor Closeout Command Style

**Old style (some prompts):** `python tools/supervisor/supervisor_loop.py ...` or `run-on-latest --bundle`

**New required style (memory section 11):** `python tools/supervisor/autonomous_cycle.py --declaration <path>`

**Resolution:** Section 44.7 declares declaration-driven closeout as mandatory. Stale-claim report notes old style as superseded. New prompt templates use new style.

### Conflict 4: Evidence Handling

**Old pattern (some sprint prompts):** Evidence repair as main sprint goal.

**New position (memory section 9):** Evidence repair justified only when blocking proof. Forward progress priority.

**Resolution:** docs/governance/evidence-handling-principles.md created. Stale-claim report notes old pattern as superseded.

## No Other Conflicts Found
The prior local-memory-sync sprint (2026-06-04, FORMAT-FACTORY-LOCAL-MEMORY-PRODUCT-FIRST-AI-EXTERNAL-TOOLS-SYNC-001) is consistent with the new memory payload. No rollback needed.
