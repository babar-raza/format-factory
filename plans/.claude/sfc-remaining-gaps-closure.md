# SFC Remaining Gaps Closure Plan

**mission_id:** SFC-REMAINING-GAPS-2026-07-17

## Context

The SFC production hardening plan (`plans/.claude/vivid-noodling-pancake.md`) shipped
5 gaps (A-E), verified via pilot rerun (334/334 tests, before/after evidence), and was
TERMINAL_CLOSED. That verification surfaced 3 remaining items, explicitly scoped out of
that plan at the time:

1. `EP-007-EXCEPTION-SCAN-UNSCOPED-GAP` — the pre-commit exception-bypass check scans
   the entire `.local/exceptions/` directory for ANY matching file, unscoped to the
   actual commit/mission — a stale, unrelated exception file has silently bypassed the
   skill-guard on every commit made this session.
2. `DIRECT-GENERATOR-GAP` — ~25 (policy estimate, now corrected: **125** per a fresh
   scan) `tools/*.py` scripts write product source/registries directly with no skill
   resolution.
3. Evidence-gated promotion of Gap C (`skill_resolution`) / Gap E
   (`sprint_closeout_governance`) advisory checks to `enforcing`.

User explicitly selected this scope (not the general product-deepening ledger) via
clarifying question. Single controller: this interactive session, direct execution +
the SFC audit/harden/execute/verify loop already used all session. No competing
headless supervisor invoked (One-Mechanism Lock, AGENTS.md §AH1).

## Taskcard Status Summary

| TC-ID | Status |
|-------|--------|
| TC-RG-001 | CLOSED |
| TC-RG-002 | CLOSED |
| TC-RG-003 | CLOSED |

(Updated as work is actually implemented, verified, and evidenced — never
marked CLOSED in advance. See Execution Log below.)

## Execution Log

### TC-RG-001 — EP-007-EXCEPTION-SCAN-UNSCOPED-GAP (CLOSED)

Root cause: `.hooks/pre-commit-skill-guard`'s `check_exception_record()` did a
naive substring scan (`"pre_commit_bypass" in content`) across every file in
`.local/exceptions/`, with no expiry and no relevance check to the files
actually being committed. A single stale exception
(`fiop-full-001-src-healing.yaml`, from mission `FIOP-FULL-001`, already
`MISSION_COMPLETE` since 2026-07-12) silently bypassed the skill-guard for
every commit made all session — confirmed live: `"[skill-guard] Exception
record found — bypassing guards"` printed on every one of this session's ~9
governance commits.

Fix: `check_exception_record(staged)` now requires every valid exception to
declare an unexpired `expires` and a non-empty `paths` list, rejects forbidden
reasons, and only grants a bypass when the UNION of all valid exceptions'
`paths` covers every staged file (all-or-nothing, fail closed on partial
coverage). Retrofitted the stale exception with its true original scope
(3 specific files) and an expiry the day after its authorizing mission
completed — it now correctly reads as EXPIRED rather than a silent perpetual
bypass.

Evidence: `tests/governance/test_precommit_exception_scoping.py` (12 tests:
no-dir, empty-staged, missing-expires, missing-paths, expired, forbidden-
reason, valid-exact-match, valid-no-match, partial-coverage-fails,
multi-exception-union, the REAL retrofitted file now inert, malformed-YAML
non-fatal). Full `tests/governance/` suite: 84/84 pass (including these 12 new
tests), 0 failures — no regression.

Committed: `5e60e223`.

### TC-RG-002 — DIRECT-GENERATOR-GAP (CLOSED)

Root cause: `scan_ungoverned_generators()` matched a write call ANYWHERE in a
file against a mutation-target string (`src/python/`, `registry/`,
`.supervisor/`, `oracle/`) ANYWHERE ELSE in the same file, with no relation
between the two. The policy doc's own stale estimate ("~25") was corrected
first: a fresh run found **125** flagged files, not 25 — the estimate itself
had drifted from reality.

Fix (detector): `_write_call_targets_mutation_path()` now requires the
mutation-target string within a bounded line window (8 before / 2 after)
around the specific write-call line, not anywhere in the file. A stricter
"must be on actual path-join syntax" gate was tried and reverted after it
produced a false NEGATIVE on the most serious confirmed true positive
(`bounded_repair_engine.py`'s only nearby evidence is an f-string error
message, not path-join code — this codebase's `Path(...) / "seg"` idiom
rarely produces a contiguous matchable substring in real path-construction
code at all). Windowing alone cut the real-repo signal from 125 to 5
candidates, verified by direct rerun against the live repo.

Manual triage of all 5 (see `docs/governance/skill-only-policy.yaml`'s
`DIRECT-GENERATOR-GAP` entry for full detail, and
`tests/governance/test_direct_generator_gap_triage.py`):
  - `tools/supervisor/bounded_repair_engine.py` — CONFIRMED real gap. Writes
    directly to `src/` with no skill resolution; two of its repair actions
    (`MISSING_ATTRIBUTE`, `NAME_ERROR`) write a literal `# TODO: implement`
    stub into product source — a direct EP-1 Zero-Stub Enforcement conflict.
    Confirmed dead code first (`ast`-based import scan: no importer anywhere
    under `tools/` outside its own test file) — marked
    deprecated-pending-redesign in its own module docstring (remediation
    option (b)) rather than governance-wrapped, since wrapping would
    legitimize code that must not run as-is without a redesign of its
    stub-write behavior (out of this task's scope — no behavior change made,
    zero risk to its 8 passing unit tests).
  - `tools/supervisor/build_context_pack.py` — CONFIRMED real gap. GOVERNED
    (remediation option (a)): added `.supervisor/context-pack.yaml` + its
    report to `tools/governance/hot-governance-files/output-manifest.yaml`,
    and added the script's path pattern to `gate.py`'s `GENERATOR_PATTERNS` —
    exactly the SFC-GAP-B precedent, reusing the same mechanism, no new
    primitive.
  - `tools/supervisor/supervisor_loop.py` — its `.supervisor/state/
    current-run.json` write is already declared under the pre-existing
    `tools/supervisor/autonomous-cycle-output-manifest.yaml`; `gate.py`
    doesn't yet route it through `guard-run` enforcement. Backlogged, not
    governed this pass — single-writer ephemeral heartbeat file, not a
    shared multi-writer canonical policy document like the hot-files set;
    lower collision risk than the other two.
  - `tools/review/architecture_audit.py`, `tools/oracle/self_test_oracle_harness.py`
    — reclassified FALSE POSITIVE on manual read even after windowing: both
    write only to `reports/`/self-test scratch dirs; the nearby match was a
    docstring or f-string error message describing what the tool *reads*
    (`src/python/{fmt}/`), not its actual write target.

Evidence: `tests/governance/test_scan_ungoverned_generators_proximity.py` (6
tests: windowed match/no-match unit tests + fixture-based scan tests + a
real-repo regression pin asserting the signal stays small), 6/6 pass.
`tests/governance/test_direct_generator_gap_triage.py` (4 tests: dead-code
confirmation for `bounded_repair_engine.py`, its docstring documents the EP-1
conflict, `build_context_pack.py` governed via the hot-files manifest +
gate.py pattern, `supervisor_loop.py`'s write already declared elsewhere),
4/4 pass. `tests/supervisor/test_hotfile_generator_guard.py` extended (2 new
outputs + 1 new parametrized pattern case), 9/9 pass. Full
`tests/governance/` suite: 149/150 pass — the 1 failure
(`test_control_validator_not_failing`, a stale command-hash HIGH finding for
`.claude/commands/reconcile-contract-capabilities.md`) is confirmed
pre-existing, unrelated concurrent-agent work (live `STALE` lease owned by
`agent-claude-code-20260717T060141-e225cd`, a different active session
working on an unrelated format-contract-layer feature) — not touched, out of
this mission's scope. Core coordination suite
(`test_coordination_guards.py`, `test_coordination_foundation.py`,
`test_coordination_registry_leases.py`, `test_coordination_preflight_gate.py`):
89/89 pass — no regression from the `gate.py` pattern addition.

`docs/governance/skill-only-policy.yaml`'s `DIRECT-GENERATOR-GAP` entry
updated with the full corrected count, fix description, and per-candidate
disposition — no longer stale.

Committed: `491d2857`.

### TC-RG-003 — Evidence-gated enforcing-promotion evaluation (CLOSED)

Ran `python -m tools.supervisor.coordination advisory-report --check <id>`
(Gap C's C3 observe-only analyzer) against the real accumulated
`advisory-log.jsonl` for both checks Gap C/E shipped in `advisory` mode:

- `skill_resolution`: 70 real events over ~16.7 hours
  (2026-07-16T20:33:25Z -> 2026-07-17T13:14:16Z), 3 distinct agents, 11
  distinct paths, **100% would-block rate**, tier breakdown 100%
  `SKILL_EXISTS_BUT_NO_MANIFEST` — **zero `MANIFEST_COVERING` events have
  ever been recorded**. Confirmed via `check-mode get` the check is still
  correctly `advisory` (not accidentally already promoted).
- `sprint_closeout_governance`: **0 events** — no headless sprint has run
  through `cmd_run_sprint`'s manifest-gated path since Gap E shipped.

**Disposition: BOTH REMAIN ADVISORY. No promotion.** This is the honest
reading of the evidence, not a placeholder deferral:
- `sprint_closeout_governance` has no traffic at all — there is nothing to
  evaluate yet, full stop.
- `skill_resolution`'s 100% would-block rate with zero observed
  `MANIFEST_COVERING` events is not "the check is working and catching real
  gaps" — it's a sign that manifest creation isn't part of anyone's actual
  interactive workflow yet (including this session's — none of TC-RG-001/
  002's edits went through `manifest.create_manifest()` first either).
  Promoting to `enforcing` today would not validate the check; it would
  block essentially every Edit/Write on a skill-governed path across the
  entire live agent population (44-53 registered agents this session, only
  3 of which have even triggered the check once) — exactly the "oscillation
  /governance-defeat" risk the plan's Gap C design flagged for premature
  *automatic rollback*, and it applies equally to premature promotion: a
  100%-block check with zero passing examples proves adoption is absent,
  not that the check is calibrated.
- Per the plan's own C4 design ("minimum sample size *and* minimum elapsed
  time, not just one or the other"): the elapsed-time leg is arguably
  approaching a first checkpoint, but the *adoption* leg (do agents ever
  actually satisfy `MANIFEST_COVERING`?) has not been observed even once.
  Time alone was never meant to be sufficient.

**Follow-on (explicitly not performed here, correctly out of TC-RG-003's
scope — "run the analyzer and make a disposition," not "build manifest-
creation integration into the standard Edit/Write flow")**: before
promotion can be responsibly reconsidered, there needs to be a burn-in
period where `MANIFEST_COVERING` events actually start appearing — which
requires manifest creation to be wired into the normal interactive workflow
(or at minimum into a governed skill population large enough to generate
real passing examples), not just the sprint/generator paths Gap C/E
instrumented. That integration is a distinct, larger task and is not
started here; recorded as a named follow-up rather than silently dropped.
No `set_check_mode` call was made — remaining on the default `advisory` is
itself the deliberate, evidence-based decision (no state mutation to make
when the evidence says "not yet").
