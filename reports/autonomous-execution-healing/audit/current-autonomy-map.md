# Autonomy Map — Sprint 5 Audit

## Sprint: FORMAT-FACTORY-AUTONOMOUS-EXECUTION-HEALING-AND-HOST-LOOP-PROOF-001
## Audited: 2026-06-05

---

## 1. Continuation Signal State

**File:** `.local/supervisor/continuation-signal.json`

```json
{
  "autonomous_continue": false,
  "iteration": 12,
  "max_iterations": 12,
  "stop_reason": "max_iterations_reached",
  "safe_lanes_available": false,
  "hard_stops_detected": ["max_iterations_reached"],
  "continuation_state": "NO_MAX_ITERATIONS"
}
```

**Classification:** `STOPPED_MAX_ITERATIONS` — autonomous continuation halted at 12/12.

---

## 2. Claude CLI Detection

**Path:** `shutil.which("claude")` → found at system PATH
**Version:** `2.1.62 (Claude Code)`
**Invocable:** YES from external terminal; NO from within Claude Code session

---

## 3. Live Noop Invocation Result

**Command:** `claude --print -p "Respond with exactly: HOST_RUNNER_NOOP_OK..."`
**Exit code:** non-zero (error)
**Output:**
```
Error: Claude Code cannot be launched inside another Claude Code session.
Nested sessions share runtime resources and will crash all active sessions.
To bypass this check, unset the CLAUDECODE environment variable.
```

**Classification:** `HOST_RUNNER_LIVE_INVOCATION_BLOCKED_BY_CLAUDECODE`
**Honest classification:** CLAUDECODE env var is set by the parent Claude Code session; all subprocesses inherit it; nested invocation is blocked by the CLI itself.

---

## 4. Prompt Generator Defect

**File:** `reports/supervisor/latest-next-worker-prompt.md` (lines 184-190)
**Bad paths:** `src/python/netpbm/`, `tests/python/netpbm/`
**Root cause:** Prompt generator references a non-existent `netpbm` Python package directory.
  Python Netpbm is split into three separate packages: `pbm`, `pgm`, `ppm` under `src/python/`.
**Status:** Validator test `tests/supervisor/test_r3_prompt_path_validator.py` correctly detects this (2 failures).

---

## 5. Max Iterations Rollover Gap

**Policy:** `.supervisor/policies.yaml` — `max_iterations: 12`
**Current state:** `iteration=12, max_iterations=12` → `autonomous_continue=false`
**Gap:** No rollover mechanism exists. When iteration reaches max, pipeline fully stops.
  New sprints require manual Babar intervention to reset the counter.
**Proposed fix:** Implement governed rollover in `autonomous_cycle.py` — when iteration reaches max
  and work remains, write `RUNTIME_CONTINUATION_REQUIRED` packet with reset instructions,
  but do NOT reset iteration automatically (requires human authorization).

---

## 6. Session-Resume vs Continuation-Signal Contradiction (CLAIM-003)

**session-resume.md says:** `Autonomous continue: True`
**continuation-signal.json says:** `autonomous_continue: false`
**Root cause:** `session-resume.md` was written at end of R3 sprint (iter=11) when
  continuation was still possible. The continuation-signal was updated to `false` after
  the autonomous_cycle.py run completed iteration 12.
**Verdict:** RESOLVED — session-resume is stale; continuation-signal is authoritative.

---

## 7. Wiring Instructions for External Terminal

To prove live invocation outside of this Claude Code session:

```bash
# From an external terminal (not inside Claude Code):
cd "C:/Users/prora/OneDrive/Documents/GitHub/format-factory"
unset CLAUDECODE
claude --print -p "Respond with exactly: HOST_RUNNER_NOOP_OK. Do not modify files. Do not run commands."
# Expected output: HOST_RUNNER_NOOP_OK
```

Or use the full autonomous runner:
```bash
unset CLAUDECODE
python tools/supervisor/autonomous_host_runner.py --live \
  --report-dir reports/host-autonomy-runner \
  --repo-root .
```

---

## 8. Summary Classification

| Component | Status |
|-----------|--------|
| Claude CLI available | YES (v2.1.62) |
| Live invocation from inside Claude Code | BLOCKED (CLAUDECODE env var) |
| Live invocation from external terminal | EXPECTED PASS (unblock by unsetting CLAUDECODE) |
| max_iterations rollover | NOT IMPLEMENTED (requires human reset) |
| Prompt generator bad paths | DEFECT (src/python/netpbm doesn't exist) |
| Continuation-signal vs session-resume | RESOLVED (signal is authoritative) |
| Overall autonomy level | H3 (packet-only inside session; H4 pending external proof) |
