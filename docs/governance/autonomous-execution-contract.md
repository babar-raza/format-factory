# Autonomous Execution Contract
# Format Factory — Governance Document
# Version: 1.0
# Date: 2026-06-05
# Authority: Format Factory Project

## Purpose

This contract defines the exact acceptance criteria for "100% autonomous until POC."
Every component in the autonomous execution system must be tested against these criteria.

---

## A. Valid Terminal States

A sprint may only emit one of these terminal states:

| State | Meaning | Who approves continuation |
|---|---|---|
| POC_READY_CANDIDATE_AUTHORITY_VERIFIED_RELEASE_APPROVAL_PENDING | All commercial + FOSS targets pass proof-backed gate; Gate 11 approval required | Babar Raza |
| POC_READY_CANDIDATE_AUTHORITY_VERIFIED | POC ready; no release pending | Agent |
| TRUE_EXTERNAL_GATE | Commit/push/Gate8/Gate11 execution/NuGet/PyPI publication required | Human |
| UNSAFE_WORKSPACE | Critical unsafe repo state (uncommitted destructive changes, etc.) | Human |
| RUNTIME_LIMIT_WITH_CONTINUATION_PACKET | Hit iteration/time limit; continuation packet exists | Agent (next session) |
| HOST_INVOCATION_LAYER_MISSING_WITH_WIRING_INSTRUCTIONS | Host runner cannot invoke Claude CLI; exact missing config documented | Human (one-time setup) |

---

## B. Invalid Terminal States (must never cause a stop)

These states MUST NOT cause autonomous execution to stop:

1. ACCEPTED (supervisor verdict alone)
2. ACCEPTED_WITH_REWORK
3. ACCEPTED_WITH_LIMITATIONS
4. Evidence package built
5. Next sprint generated
6. Max iterations reached (checkpoint rollover instead)
7. Gate 11 PREPARATION needed (agent-owned, never terminal)
8. Commit/push PREPARATION needed (agent-owned, never terminal)
9. Proof materialization warning (repair + continue)
10. anti-skip false positive (fix + continue)
11. prompt-quality warning (non-blocking caveat)
12. Missing optional acceleration
13. Host-runner dry-run only (unless host invocation is truly unavailable)
14. MODE/Ruflo/Claude-flow unavailability (fallback to local coordinator)
15. Missing optional evidence (repair/continue, not invalid stop)

---

## C. Required Autonomous Loop

Every sprint must execute this loop:

```
1. inspect_state()
2. classification = classify_terminal_state(state)
3. if classification in VALID_TERMINAL_STATES:
       if classification == POC_READY_CANDIDATE_..._RELEASE_APPROVAL_PENDING:
           emit final state, stop (external gate required)
       elif classification == TRUE_EXTERNAL_GATE:
           emit exact action needed, stop (human required)
       elif classification == HOST_INVOCATION_LAYER_MISSING_...:
           emit wiring instructions, stop (one-time setup)
       else:
           CONTINUE
4. else:
       next_action = generate_next_action(state)
       validate_next_action(next_action)
       if host_runner_available:
           invoke_host_runner(next_action)
       else:
           execute_locally(next_action)
       update_train_state()
       build_evidence()
       GOTO 1
```

---

## D. Required Proof for POC

A format target passes the proof-backed gate when it has ALL of:

| Requirement | Description | Exemptions |
|---|---|---|
| source | At least 1 source file > 100 bytes in expected src/ dir | None |
| tests | At least 1 test file in expected tests/ dir | None |
| raw_logs | At least 1 .log file containing format-name string | None |
| examples | At least 1 file in examples/ dir | DIF (no examples required) |
| proof_record | Ledger entry + proof graph projection (or explicit accepted substitute) | None |
| no_ai_draft_only | ai_draft files cannot be sole proof | None |

FOSS minimum: 3 of N FOSS targets must pass all checks.

Proof record requirements (Option B — Ledger-backed projection):
- Product code change ledger is canonical operational record
- A deterministic proof graph projection MUST be generated from the ledger
- "Ledger only" without projection is NOT accepted for POC gate
- Projection must be present at: reports/autonomous-system-audit/projected-proof-graph/

---

## E. Host Invocation Requirements

The autonomous host runner must:

1. Detect Claude CLI via shutil.which("claude") + explicit candidate paths
2. Perform dry-run with safe prompt (no modification, no commands)
3. Perform live no-op invocation if allowed by policy and CLI available
4. Refuse any prompt containing hard-stop keywords
5. Write host-runner-state.json with classification
6. If CLI unavailable: classify HOST_INVOCATION_LAYER_MISSING_WITH_WIRING_INSTRUCTIONS

Hard-stop keywords (must refuse):
- git push
- git commit
- gate 11 approval
- gate 8 approval
- publish
- commercial_product_ready: true
- mcp activation

Live no-op safe prompt:
"Respond with exactly: HOST_RUNNER_NOOP_OK. Do not modify files. Do not run commands."

---

## F. Adoption Compliance Requirements

For non-exempt source-changing work items:
- transcript required (or explicit fallback_transcript + reason)
- skill_id OR fallback_skill_id required
- lane ledger entry required
- source diff or changed files required
- test file or raw log required

Compliance result must classify as one of:
- PASS
- PASS_WITH_EXEMPTIONS (all non-exempt items have explicit exemption_reason)
- FAIL_MISSING_TRANSCRIPTS (non-exempt items without transcript, no exemption)
- FAIL_MISSING_SKILL_IDS (non-exempt items without skill_id, no exemption)
- FAIL_MISSING_LEDGER (src-editing items without ledger entry)

Compliance CANNOT be true when:
- non_exempt_items > 0 AND items_with_transcript = 0 AND items_with_skill_id = 0
- Unless every non-exempt item has explicit exemption_reason

---

## G. Anti-Skip Discovery Requirements

Anti-skip must discover raw logs from:
- evidence_root/ directly
- evidence_root/raw-logs/
- reports/<run_id>/raw-logs/ (R100 fix)
- sprint-evidence/reports/<run_id>/raw-logs/
- changed-files/reports/<run_id>/raw-logs/
- declaration.evidence_artifacts with type in (raw_log, raw-log, log, test_log)
- evidence-manifest.yaml with type in (raw_log, log)

Evidence quality score must NOT be 0 when:
- Raw logs exist
- Tests are referenced
- Proof audit exists
- Package has materialized artifacts
- ACCEPTED_WITH_LIMITATIONS items have declared evidence paths

---

## H. Components Using This Contract

All of the following must be testable against this contract:

- tools/supervisor/validate_adoption_compliance.py
- tools/supervisor/anti_skip_checker.py
- tools/supervisor/proof_backed_poc_gate.py
- tools/supervisor/autonomous_host_runner.py
- tools/supervisor/autonomous_train_executor.py
- tools/supervisor/stop_reason_adjudicator.py
- tools/supervisor/generate_next_worker_prompt.py
- tools/supervisor/simulate_autonomous_loop.py
