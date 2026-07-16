# Independent Verification — Skills-First Control

**Verifier:** independent agent (separate context; did not rely on the implementer's
summary). **Method:** ran every tool itself, read the code, and attempted bypasses.

## What the verifier independently reproduced

**Tools run (exit codes captured without a masking pipe):**
- `validate_skills_first_control.py --json` → `PASS_WITH_WARNINGS` (CRITICAL 0, HIGH 0,
  MEDIUM 1, INFO 6), **exit 0**.
- `audit --warn-high` → `verdict=PASS skills=185/188 commands=188 CRITICAL=0 HIGH=0`,
  **exit 0**.
- Test suite → **36 passed**, exit 0. Confirmed the adversarial file contains ≥6
  genuine fail-closed assertions (not smoke tests).

**Bypass attempts (all correctly blocked):**
- Manifest naming an unregistered skill → `exit 2` BLOCKED.
- Closeout of an out-of-scope change + no evidence → `CLOSE_BLOCKED` exit 1.
- Closeout of in-scope change + evidence → `CLOSE_OK` exit 0.
- Expired / broad / forbidden-reason exceptions → all rejected by `validate_exception`.
- Empty allowed_paths and bogus agent_type → blocked. Only valid exceptions enter the
  covered set; invalid ones are surfaced as violations, never silent passes.

**Healing & policy independently confirmed:**
- `fix-exception-hierarchy` and `wire-analytics-module` now in BOTH registries; both
  `.md` on disk.
- New `skills-first-audit` skill + command + `skills_first_control` route all present.
- Policy is v2.1; EP-007 = `IMPLEMENTED_AND_INSTALLED`; EP-010/011/012/013 present;
  manifest schema referenced; `known_gaps` includes EP-010-GAP, RUNLOOP-SKIPPERMS-GAP,
  DIRECT-GENERATOR-GAP.

**Honesty check:** Part IV of the consolidated audit and the pilot records openly
disclose the open gaps (tool-layer gate coordination-only; product write DENY-listed;
live loop not run). Nothing hidden.

## Verdict

> **VERDICT: ACCEPT_WITH_EXTERNAL_BLOCKERS**

Named external blockers (all documented as tracked `known_gaps` with compensating
controls EP-007/012/013):
1. `src/` write permission is DENY-listed in `.claude/settings.json` — blocks the
   product pilot's *actual* mutation (operator authorization required to write `src/`).
2. Headless `run-loop` manifest/closeout wiring deferred (RUNLOOP-SKIPPERMS-GAP) — the
   live autonomous loop was not run; enforcement is contract-proven, not exercised
   end-to-end.
3. EP-010 PreToolUse tool-layer skill gate remains coordination-only (deferred pending
   a staged advisory→enforcing rollout on shared live infrastructure).

The verifier found the controls real and fail-closed under its own attacks, the
healing and reconciliation genuine, and the gaps honestly disclosed (a cover-up would
have been REJECT-worthy; this was not).
