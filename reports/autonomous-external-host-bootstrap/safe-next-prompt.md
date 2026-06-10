# safe-next-prompt.md
# Sprint: FORMAT-FACTORY-AUTONOMOUS-EXTERNAL-HOST-BOOTSTRAP-001
# Generated: 2026-06-05T22:50:00
# Purpose: Replace unsafe "Authorized git commit + push" wording in next sprint prompt;
#          route future cycles through external_host_loop.py when HOST_LOOP_SMOKE_PROVEN

---

## HOST LOOP STATUS: HOST_LOOP_SMOKE_PROVEN

The external host loop has completed a successful smoke cycle:
- `host-loop-result.json`: classification=HOST_LOOP_SMOKE_PROVEN
- `smoke/host-created-proof.md`: proof file exists with HOST_CYCLE_SMOKE_OK marker
- Claude CLI invoked via subprocess (CLAUDECODE not in child env)
- Claude CLI path: C:\Users\prora\AppData\Roaming\npm\claude.CMD
- Exit code: 0, marker found in stdout, all expected files created

---

## ROUTING DECISION

Since HOST_LOOP_SMOKE_PROVEN:
→ Future autonomous product sprints SHOULD use `external_host_loop.py` as the execution substrate.
→ The in-session agent does NOT need to execute product trains directly.
→ Update `reports/autonomous-external-host-bootstrap/next-action.json` for each new cycle
   (change prompt_path, expected_output_files, success_marker as needed).
→ Invoke via: `python tools/supervisor/external_host_loop.py --next-action ...`
   or the VS Code task "Format Factory: Start External Autonomous Host"
   or `scripts/autonomous_external_host.ps1` / `scripts/autonomous_external_host.sh`

If NOT HOST_LOOP_SMOKE_PROVEN (future regression):
→ Check: Is CLAUDECODE exported in parent env? (Scrub it: Remove-Item Env:CLAUDECODE)
→ Check: Is Claude CLI on PATH? (shutil.which("claude") or which claude)
→ Check: Does next-action.json have schema_version=1 and all required fields?
→ Record classification in host-loop-result.json and diagnose before proceeding.

---

## UNSAFE WORDING DETECTED AND SUPPRESSED

The following unsafe wording was found in `reports/supervisor/latest-next-worker-prompt.md`:

  Line 105: "Authorized git commit + push (requires user authorization)"
  Line 123: "Authorized git commit + push (requires user authorization)"
  Line 141: "Authorized git commit + push (requires user authorization)"

**This wording is SUPPRESSED by this safe-next-prompt.**

Rules:
- "Authorized git commit + push" in a generated task description is NOT an authorization to commit.
- Git commit/push requires EXPLICIT user approval in this session (not generated text from supervisor).
- The stop_reason_adjudicator classifies this as a TRUE_EXTERNAL_GATE — do not self-execute.
- Preparation (commit candidate manifest, staged diff, changelog) is agent-owned; execution is not.

---

## SAFE NEXT SPRINT FRAMING

For the next sprint after FORMAT-FACTORY-AUTONOMOUS-EXTERNAL-HOST-BOOTSTRAP-001:

**Sprint Goal:** Continue product deepening via external host loop substrate.

**What agent can do autonomously (in-session):**
- Select governed product gaps
- Write next-action.json for the external host loop
- Validate product-code ledger
- Prepare Gate 11 readiness packets
- Prepare commit candidate manifest (without committing)

**What must go through external_host_loop.py:**
- Executing product trains (FODS/FODT/Netpbm/ZST/etc. src/ changes)
- Running tests and builds
- Writing proof files for autonomous continuation

**Hard stops (never autonomous):**
- git commit (TRUE_EXTERNAL_GATE — requires explicit user authorization)
- git push (TRUE_EXTERNAL_GATE)
- Gate 8/11 approval (TRUE_EXTERNAL_GATE — Babar Raza required)
- NuGet/PyPI publication

---

## FILES CREATED BY HOST BOOTSTRAP SPRINT

Proof artifacts (do not delete):
- `reports/autonomous-external-host-bootstrap/next-action.json` — live next-action contract
- `reports/autonomous-external-host-bootstrap/safe-smoke-prompt.md` — verified safe prompt
- `reports/autonomous-external-host-bootstrap/smoke/host-created-proof.md` — smoke proof
- `reports/autonomous-external-host-bootstrap/host-loop/host-loop-result.json` — smoke result
- `reports/autonomous-external-host-bootstrap/host-loop/host-loop-log.jsonl` — execution log
- `tools/supervisor/external_host_loop.py` — host runner (CLAUDECODE-safe)
- `scripts/autonomous_external_host.ps1` — PowerShell bootstrap
- `scripts/autonomous_external_host.sh` — Bash/Git-Bash bootstrap
- `.vscode/tasks.json` — VS Code tasks for host loop

Tests (do not delete):
- `tests/supervisor/test_external_host_loop.py` — 23 tests, all pass
- `tests/supervisor/test_autonomous_execution_healing.py` — 16 tests, all pass
