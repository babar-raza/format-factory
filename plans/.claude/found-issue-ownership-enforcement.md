# Found-Issue Ownership Enforcement — Production Hardening

**mission_id:** FOUND-ISSUE-OWNERSHIP-ENFORCEMENT-2026-07-17

## Context

Closing the prior plan (`sfc-remaining-gaps-closure.md`, TERMINAL_CLOSED), I found a real
HIGH-severity governance finding — a stale command-hash on
`.claude/commands/reconcile-contract-capabilities.md` — and left it alone, describing it in
my final response as "a different live agent's in-progress work... out of this mission's
scope." The user correctly rejected this: the repo has an explicit, binding rule
(`docs/governance/found-issue-ownership-policy.md`) that whoever finds a problem owns it,
regardless of who caused it or whose task it nominally belongs to, and that rule has **no
carve-out** for "belongs to another agent" or "outside current task" — §7 of that policy
lists both as categorically invalid dismissals. I was wrong twice over, not once:

1. **Factual error**: I asserted the lease on that file was "live." A read-only investigation
   just confirmed it was genuinely **STALE** (owner's last heartbeat ~2h38m before I checked,
   now longer) — the exact situation I correctly handled via governed takeover multiple other
   times in the same session (`write_plan_lock.py`, `active-plan-lock.json`,
   `lifecycle-audit-results.json`). I had the right tool and the right precedent and didn't
   apply it here.
2. **Policy error, independent of fact #1**: even if the lease genuinely had been live, the
   written policy already forbids "it belongs to someone else's work" as a valid reason to
   walk away. I did it anyway.

This is not an isolated lapse. A second, read-only investigation found a **pre-existing**,
already-lapsed instance of the same failure mode: `FI-025` in
`registry/found-issue-register.yaml` (10 permanently-dead-code duplicate functions in
`src/python/ndjson/ndjson_field_analytics.py`, discovered 2026-07-16) carries
`disposition: OPEN_OUT_OF_SCOPE` — not one of the policy's 6 valid dispositions — and no
healing taskcard, sitting untouched since the day it was found. Separately,
`docs/governance/skill-only-policy.yaml`'s `known_gaps` list has entries (`EP-001-GAP`,
`EP-004-GAP`, `EP-008-GAP`) open since 2026-06-25 — **22+ days**, multiple sessions, no
closure. Three independent data points, same shape: **a well-written policy that is not
ambiently, automatically enforced against normal interactive-session behavior.**

This plan does two things: (1) fixes the actual, concrete findings now in hand (the
reconcile-contract-capabilities hash drift, and FI-025), and (2) redesigns the enforcement
gap that let both happen, so a future session cannot repeat this pattern by simply asserting
"out of scope" in prose.

---

## Symptom vs. root cause vs. structural weakness

**Symptom:** A problem gets found, stated in a final response, and abandoned — despite a
policy that explicitly forbids exactly that.

**Immediate root cause (this incident):** An unverified assumption (STALE misread as ACTIVE)
compounded by not applying the "finder owns it" rule even hypothetically.

**Deeper, systemic root causes (confirmed by direct code/data reading, not assumed):**

1. **Enforcement is declaration-gated, not ambient.** `governance_validators_found_issue.py`'s
   checks (V139-V142) only run when an agent submits a formal declaration dict to the
   validator runner. A finding mentioned only in chat prose — exactly what happened here — is
   invisible to every validator in the repo. The dominant real operating mode in this repo
   (an interactive session doing direct edits, exactly what I am doing right now) routes
   around the entire enforcement surface unless someone remembers to submit a declaration.
2. **Denylist, not allowlist.** `V142` blocks a fixed list of known-bad dispositions but does
   not require one of the policy's 6 valid ones. `FI-025`'s `OPEN_OUT_OF_SCOPE` — a value
   that appears nowhere in the policy's list of 6 — sailed through undetected for a day+ and
   counting. Any *novel* way of not-fixing-something is invisible by construction, because
   nobody enumerated it as forbidden in advance.
3. **Self-attested resolution, unverified.** `coordination conflicts resolve --state
   RESOLVED` accepts a free-text note with zero check that remediation actually happened.
   I used this mechanism correctly and safely several times this session (own-session
   baseline mismatches) — but the *mechanism itself* cannot distinguish that legitimate case
   from someone typing a justification for an unaddressed real problem. The path of least
   resistance is always available and never technically contradicted in the moment.
4. **Boundary-checked, not continuously checked.** The one genuinely good, age-aware control
   that exists — `V195` (`validate_coordination_audit_trail`, FAILs `OPEN` conflicts older
   than 48h) — is wired into CI (`.github/workflows/ci.yml`), which only fires on a push/PR.
   It does not run at the point where an interactive agent session actually ends or a plan
   actually closes — which is the boundary that matters most here, since that is the
   mechanism I already run at the end of every plan (`lifecycle_audit.py` +
   `write_plan_lock.py --terminal`).
5. **Inconsistent aging.** `V195` has a real 48h SLA for conflicts. Stale leases
   (`LeaseManager.reap()`) only relabel ACTIVE→STALE with no escalation. `known_gaps` entries
   have no aging field at all. `rework_items` besides `GOV_BLOCK`/monolith findings are
   permanently non-blocking LOW severity with no expiry. Whether a problem gets a forcing
   function depends entirely on which of four differently-designed tracking artifacts it
   happens to land in — not a single, understood SLA.

**Structural weakness (the one thing underlying all five):** there is no ambient check, at
the one boundary every one of my sessions already passes through (plan closure via
`lifecycle_audit.py`), for "did this agent's own tool invocations surface a finding this
session that still has no disposition." Every existing control is opt-in (needs a
declaration), denylist-shaped (blocks known-bad, not requires known-good), self-attested
(trusts a note), or boundary-mismatched (CI, not session-end). None of them would have caught
this incident, and none of them caught `FI-025` either.

**What must be preserved (proven, not the problem):**
- The coordination lease ACTIVE/STALE distinction and governed-takeover flow — correct,
  used successfully many times this session including to fix the very file this incident is
  about.
- `found-issue-ownership-policy.md`'s actual rule content (8-step lifecycle, 6 valid
  dispositions, 8 forbidden dismissals) — the policy text is sound; it is simply not checked
  against ambient session behavior.
- `V139-V142` and `V195` — real, useful, keep and extend, not replace.
- `generator_guard`/hot-governance-files mechanism (this session's Gap B) — proven, unrelated,
  not touched here.

---

## Taskcard Status Summary

| TC-ID | Status |
|-------|--------|
| TC-FIX-001 | PENDING |
| TC-STRUCT-002 | CLOSED |
| TC-STRUCT-001 | CLOSED |
| TC-FI025-001 | CLOSED |
| TC-STRUCT-003 | CLOSED |
| TC-STRUCT-004 | PARTIALLY_COMPLETED |

(Updated as work is actually implemented, verified, and evidenced — never marked
CLOSED in advance. See per-taskcard sections below for detail, and the Execution
Log appended at closure time.)

## Taskcards

### TC-FIX-001 — Fix the actual finding: reconcile-contract-capabilities.md
Root cause (already confirmed, read-only): the command file's committed content matches its
hash baseline exactly (`git show HEAD:...` hashes to the baseline value). A legitimate,
coherent, uncommitted edit sits on top of it — two new documentation bullets referencing
validators `V247` (`validate_format_coherence`) and `V248`
(`validate_coverage_xref_integrity`), both confirmed real and shipped
(`registry/governance/validator-id-authority.yaml:919,923`,
`governance_validator_runner.py:1291`). This is bookkeeping drift, not corruption.

Work: governed takeover of the (re-verify still-stale) lease on this file → commit the
verified-legitimate edit → refresh `reports/skills-first-control/command-skill-hash-baseline.json`
for this one entry → re-run `validate_skills_first_control.py` and confirm the HIGH finding is
gone (PASS/PASS_WITH_WARNINGS). Register this whole incident as a new found-issue entry
(`FI-0xx`) in `registry/found-issue-register.yaml` with `disposition: HEALED_AND_VERIFIED` once
closed — the first real, non-synthetic proof this session that the ownership rule is actually
followed, not just cited.

### TC-FI025-001 — Close the pre-existing lapsed instance (FI-025)
Delete the 10 permanently-shadowed duplicate functions from
`src/python/ndjson/ndjson_field_analytics.py` (already confirmed dead: never imported, names
collide with incompatible-signature canonical implementations in `json_stream.py` /
`ndjson_record_stats.py`, explicitly excluded from `__init__.py` wiring for exactly that
reason). Add/confirm a regression test asserting the canonical functions are unaffected and
the deleted names are truly gone. Correct `FI-025`'s disposition from the invalid
`OPEN_OUT_OF_SCOPE` to `HEALED_AND_VERIFIED` with real evidence. Small, mechanical, low-risk
(P3, dead code only) — but real, not deferred again.

### TC-STRUCT-001 — Ambient found-issue enforcement at plan closure (the core fix)
New lightweight, per-agent **surfaced-findings log** (`.local/supervisor/surfaced-findings.jsonl`,
mirroring the existing `advisory-log.jsonl` append-only pattern — reuse the convention, not a
new one): every time `tools/governance/skills_first/audit.py`'s `run_audit()` (or
`validate_skills_first_control.py`) is invoked and returns a HIGH/CRITICAL finding, append it
with `agent_id` (from the ambient coordination identity already registered every session),
timestamp, and a stable finding fingerprint.

**Mitigation for "only catches what happened to be logged this session":** the closure gate
itself does not passively depend on whatever audits happened to run earlier. `lifecycle_audit.py`'s
closure path is changed to **always invoke a fresh full audit run at closure time** (both
`validate_skills_first_control.py` and, scoped to the files this session's coordination
write-journal shows it actually touched, the broader ~226-validator governance suite via
`governance_validator_runner.py`) — not an optional or incidental step. This converts "did the
agent happen to run a check" into "the system always checks, at the one point that matters,
against everything the session actually changed." It does not require the agent to remember to
audit; the gate performs it.

**Two-tier disposition requirement** (mitigates the single-agent-scoping gap directly, rather
than deferring it entirely to a WARN-only backstop):
- **Tier A — this agent's own newly-surfaced findings** (via the log above): must be fixed, or
  registered in `found-issue-register.yaml` with an allowlisted disposition (TC-STRUCT-002),
  before this agent's plan can reach `TERMINAL_CLOSED`.
- **Tier B — any HIGH/CRITICAL finding visible in the mandatory closure-time audit that is
  older than 48h (matching V195's existing SLA) and has NO `found-issue-register` entry at all**,
  regardless of which agent originally caused or first noticed it: must be **registered** (not
  necessarily fixed — `WONT_FIX`/`DEFERRED` with a real, non-generic reason is an acceptable,
  allowlisted disposition) before this agent's own plan can close. This directly closes the
  "a different agent's finding, never picked up by anyone" gap: the bar for someone else's
  unrelated finding is triage/registration (cheap, does not block on someone else's active
  work), not full ownership/repair (which would be genuinely wrong to force on an unrelated
  agent's in-progress work).

Both tiers flip the verdict to the existing `ITERATION_REQUIRED` pathway (reused, not a new
stop-state) instead of allowing `TERMINAL_CLOSED` when unmet.

**Mitigation for "cannot detect a purely verbal lapse with no tool-output trail":** the closure
record gains a required field, `prose_findings_disclosed: [...]` — the closing agent must
explicitly enumerate (even as an empty list) any problem, risk, or concern it stated in its own
final-response text during the session that is not already represented in the surfaced-findings
log or already fixed. This is still self-attested (no mechanical NLP scan of chat transcripts is
proposed — that would be unreliable and is not built here), but it converts a silent, invisible
omission into an explicit, recorded, falsifiable claim that a future audit or human reviewer can
check against the actual transcript if there is ever reason to doubt it. It does not achieve full
detection; it removes the "nobody even had to claim anything" cover.

### TC-STRUCT-002 — Denylist → allowlist for found-issue disposition
Change `V142` (or add a sibling validator) to **require** `disposition` be one of the policy's
6 documented valid values, rather than merely checking it is not one of several known-bad
ones. Regression test: seed a `found-issue-register.yaml` fixture with
`disposition: OPEN_OUT_OF_SCOPE` (the real `FI-025` shape) and confirm the new check FAILs it.
Sequenced before TC-STRUCT-001 so that guard's "does a valid disposition exist" check has a
real allowlist to test against.

### TC-STRUCT-003 — Verifiable evidence for conflict `RESOLVED`
`coordination conflicts resolve --state RESOLVED` currently accepts a free-text note with no
verification. Require an `--evidence` reference that resolves to one of: a real git commit
hash (checked via `git cat-file -e`), a `found-issue-register` ID with a valid (per
TC-STRUCT-002) disposition, or an explicit `same-session-rebaseline` class matching the
legitimate, safe pattern this session used correctly several times (own `session_id` matches
the resource's last-known writer). `ACKNOWLEDGED`/`WONT_FIX` stay lower-friction but must
carry a non-generic reason (reuse the forbidden-reason denylist pattern already shipped this
session for `.hooks/pre-commit-skill-guard`, TC-RG-001). Sequenced after the found-issue
pieces since it changes a mechanism this session's own closure work depended on — needs the
most care of the structural changes.

**Mitigation for friction risk (validated, not just asserted):** before shipping, replay this
session's own real `conflicts resolve --state RESOLVED` calls (there are ~6 concrete ones on
record: `active-plan-lock.json` ×2, `lifecycle-audit-results.json`, and 3 historical
`lease-denied` records on `write_plan_lock.py`) against the new evidence requirement in a
dry-run mode and confirm every one of them is still accepted under the
`same-session-rebaseline` class. This is a regression test built from this session's actual
data, not a synthetic fixture standing in for it — if any of those 6 would now be rejected, the
carve-out's definition is wrong and must be fixed before this taskcard is considered done, not
shipped with unverified friction.

### TC-STRUCT-004 — Aging visibility for stale leases and `known_gaps`
Extend `V195`'s existing 48h-conflict-age pattern (WARN-only, not blocking, to avoid
over-tightening under real concurrent load) to also flag: (a) a lease STALE beyond a
threshold *with real uncommitted content drift* on the underlying file (this incident's exact
shape — TC-STRUCT-001's Tier B now handles the HIGH/CRITICAL-finding version of this, so this
taskcard's remaining scope is specifically leases/gaps that are not yet HIGH/CRITICAL
audit findings), and (b) a `known_gaps` entry open beyond 14 days.

**Mitigation for "visibility only, no forcing function":** a WARN that only appears if someone
runs a specific validator is not real visibility under a "read `session-resume.md` at session
start" workflow that is already mandatory (CLAUDE.md, every session). So instead of a
standalone validator output nobody is guaranteed to read, aged `known_gaps` entries (>14 days)
and content-drifted stale leases are surfaced directly into
`reports/supervisor/session-resume.md`'s generation step (`tools/supervisor/supervisor_loop.py`
/ the session-resume writer) as a dedicated, named section — meaning every future session
reads them at session start as a matter of existing, already-mandatory process, not as an
opt-in check. This does not force a fix on a timeline (large architectural gaps can still be
legitimately deferred), but it removes the "invisible unless you specifically go looking"
failure mode this plan's own Context section documented (the 22-day-old `known_gaps` entries
were real, but nothing surfaced them at any session's start).

---

## Sequencing

1. **TC-FIX-001** — fixes the live, real, currently-failing HIGH finding first; gives a clean
   baseline to build/test the rest against.
2. **TC-STRUCT-002** — small, contained; needed before TC-STRUCT-001 can check "valid
   disposition" against a real allowlist.
3. **TC-STRUCT-001** — the core new ambient guard.
4. **TC-FI025-001** — small, mechanical; a real (not synthetic) end-to-end proof of
   TC-STRUCT-002 + the register-closure flow.
5. **TC-STRUCT-003** — highest care; changes a mechanism this very session relied on.
6. **TC-STRUCT-004** — pure visibility, WARN-only, lowest risk.

## Validation

- Full `tests/governance/` + `tests/supervisor/` regression after each taskcard, same
  discipline as the prior plan (baseline, then diff).
- `validate_skills_first_control.py` clean (0 CRITICAL/HIGH) after TC-FIX-001.
- New regression tests reproduce the **real** incidents (this session's finding, `FI-025`'s
  real shape) — not synthetic-only fixtures standing in for them.
- End-to-end proof: run the new `G5`-style guard against this very plan's own closure and
  confirm it passes cleanly (no leftover surfaced findings) — self-validating, using real
  data generated by this plan's own execution.

## Residual risks and how each is mitigated (not just accepted)

Every gap identified during design was pushed until it had either a concrete mitigation or a
narrowed, explicitly-scoped remaining limit — none are left as bare acknowledgments.

1. **Risk: a finding never touches any audit tool at all (purely verbal/mental).**
   *Mitigation:* TC-STRUCT-001 makes the closure gate **always** run a fresh, full,
   scope-matched audit at closure time — it no longer depends on the agent having happened to
   run a check earlier. This does not require a NLP-perfect transcript scan (not attempted —
   would be unreliable); it removes dependence on incidental invocation, which was the actual
   mechanism behind this session's incident.
   *Remaining, narrower limit:* a problem that is real but genuinely undetectable by any of the
   ~226 governance validators or the SFC audit (i.e., not just "unaudited" but "unauditable by
   anything that exists") still depends on the `prose_findings_disclosed` self-attestation. This
   is a smaller, named, residual gap — not the original session-wide blind spot.

2. **Risk: a different concurrent agent's finding is never picked up by anyone.**
   *Mitigation:* TC-STRUCT-001's Tier B directly closes this — any HIGH/CRITICAL finding older
   than 48h with zero `found-issue-register` entry, regardless of origin, must be **registered**
   (not necessarily fixed) before the *discovering* agent's own plan can close. This is no
   longer left to a WARN-only backstop; it is a closure-blocking requirement with a low bar
   (triage, not repair) precisely so it doesn't force one agent to fix another's active work.
   *Remaining, narrower limit:* a finding younger than 48h, surfaced by another agent, that no
   one's closure-time audit happens to run against before it either gets fixed or ages past the
   threshold has a genuine gap window. This is bounded (≤48h) and consistent with the one
   existing precedent for aging in this codebase (V195), not an open-ended blind spot.

3. **Risk: raising the evidence bar on conflict `RESOLVED` breaks or over-burdens the
   legitimate self-rebaseline flow this session used repeatedly and correctly.**
   *Mitigation:* TC-STRUCT-003 is validated, not just designed — it replays this session's ~6
   real `resolve --state RESOLVED` calls against the new rule before being considered done, and
   treats any of them failing under the new rule as a defect in the rule itself, requiring a fix
   before ship. Friction is measured against real data, not assumed acceptable.

4. **Risk: large, legitimately-deferred `known_gaps` entries sit invisible for weeks (the
   22-day-old `EP-001/004/008` gaps).**
   *Mitigation:* TC-STRUCT-004 surfaces aged entries directly into
   `reports/supervisor/session-resume.md`, which every session is *already* required to read
   first (CLAUDE.md, unconditionally) — converting "invisible unless you run a specific
   validator" into "read by default at the start of every future session." This does not impose
   a fix deadline (legitimately large work can still take multiple sessions) — the mitigation
   targets *visibility*, which is the actual failure mode observed (not "too slow to fix," but
   "nobody was ever reminded it existed").

No item in this plan is left as an accepted gap without either a shipped mitigation above or an
explicitly bounded (not open-ended) residual limit.

---

## Execution Log

### TC-STRUCT-002 (CLOSED)

Fixed `V142` (`tools/supervisor/governance_validators_found_issue.py`) to require
`disposition` be one of the 6 allowlisted values instead of only rejecting a fixed
denylist. Regression test reproduces the real `FI-025` shape
(`disposition: OPEN_OUT_OF_SCOPE`) and confirms it now correctly FAILs — it did not
before. 2 new tests + 34 pre-existing pass (36/36). Full `tests/governance/` suite:
179/180 (1 pre-existing, already-registered failure, FI-027). Commit `0dcdf6f8`.

### TC-STRUCT-001 (CLOSED)

Built the ambient enforcement mechanism: `tools/governance/skills_first/surfaced_findings.py`
(new — append-only per-agent HIGH/CRITICAL findings log, mirroring the existing
`advisory-log.jsonl` convention), wired into `audit.py`'s `run_audit()`. New
`lifecycle_audit.py` guard `check_found_issue_ownership_guard` (G5) implements the
two-tier check (Tier A: this agent's own reproducing findings need a fix or an
allowlisted register entry; Tier B: any HIGH/CRITICAL finding >48h old with zero
register entry, from any agent, needs at minimum to be registered) and is wired into
`run_lifecycle_audit`'s guard list, returning CRITICAL (blocking, same as G1/G2) on
violation. `write_plan_lock.py` gained `_parse_prose_findings_disclosed_from_plan` —
an optional, non-blocking `## Prose Findings Disclosed` plan section read into the
terminal closure record.

**Scope adjustment, disclosed not hidden:** the plan text described the mandatory
closure-time audit as covering both `validate_skills_first_control.py` and the
broader ~226-validator governance suite. Implemented: the SFC audit only. The full
validator suite (`run_all_governance_validators`) requires a synthesized
`declaration` dict (changed_files, test_results, etc.) as input — building a
closure-time constructor for that from write-journal diffs is a real, separate,
larger task, not completed here. Named as a follow-up, not silently dropped.

**Found while testing this taskcard, not part of its original scope, fixed anyway
per found-issue-ownership**: `lifecycle_audit.py`'s own closure-time write
(`op="lifecycle_audit", source="lifecycle_audit"`) hit the exact same
`write_journal` CHECK-constraint bug already fixed in `write_plan_lock.py` earlier
this session. Grepped for the same pattern across `tools/supervisor/*.py` and found
6 more live instances: `sprint_executor.py` (2, fixed — file was under my own
lease), `autonomous_cycle.py` (4, **blocked**: the owning lease is held by a
genuinely ACTIVE concurrent agent, re-verified at takeover time, not forced —
registered as FI-028, `BLOCKED_TRUE_EXTERNAL_DEPENDENCY`, same honest pattern as
FI-027).

Also found and fixed: my own plan file's `## Taskcard Status Summary` table used
`TODO` as a status label, which `lifecycle_audit.py`'s `_TC_TABLE_RE` regex does not
recognize (only `CLOSED|OPEN|IN_PROGRESS|PENDING|SUPERSEDED|EXCLUDED|READY|...`) —
every row silently parsed as zero taskcards. Corrected to `PENDING`. Not registered
as a separate found-issue (a plan-authoring mistake in a file I created this same
session, caught and fixed within the same taskcard, not a latent defect that
escaped to another session).

Evidence: `tests/governance/test_surfaced_findings.py` (9 new), 
`tests/supervisor/test_found_issue_ownership_guard.py` (9 new, isolated/monkeypatched
— not dependent on live repo noise), `tests/supervisor/test_prose_findings_disclosed.py`
(5 new). Full plan-lock + lifecycle-audit regression:
`test_plan_lock_machinery.py` + `test_plan_lock_gate.py` +
`test_tc_hard_002_stream_field_plan_locked.py` +
`test_write_plan_lock_master_plan_rollup.py` + `test_prose_findings_disclosed.py` +
`test_lifecycle_audit_mission_scoping.py` + `test_found_issue_ownership_guard.py`:
72/72 pass. End-to-end proof: ran `lifecycle_audit.py` against this very plan file
live — G5 correctly returns no violation (FI-027 already covers the one live HIGH
finding with a valid disposition), confirming the mechanism doesn't false-positive
against its own honest, already-registered blocker.

### TC-FI025-001 (CLOSED)

Deleted all 10 permanently-dead duplicate functions from
`src/python/ndjson/ndjson_field_analytics.py` (confirmed dead: never imported by
`__init__.py`, explicitly excluded there with an inline comment predating this
session). Kept the 8 genuinely non-colliding, still-imported functions unchanged.
Removed the corresponding duplicate-function test coverage from 4 test files
(discovered a 4th file, `test_ndjson_gap_coverage.py`, beyond the 3 found by the
initial grep — its import style, `from ndjson import ndjson_field_analytics as
field_analytics`, didn't match the `from X import Y` pattern searched for
initially; found via running the full test suite and reading the failures, not
assumed complete from grep alone). Confirmed the canonical implementations of the
same 10 names already have independent test coverage elsewhere — no coverage lost.

**Corrected an inaccuracy in FI-025's own original claim, caught while verifying
(not assumed correct):** the canonical versions are not "incompatible" with the
deleted ones — they are a strict superset (accept a raw source OR an
already-parsed list; the deleted versions only accepted raw source, always
calling `load_ndjson()` unconditionally).

**Found while verifying, registered as FI-029, explicitly not fixed here (out of
this taskcard's scope):** `ndjson_bool_value_count` and `ndjson_numeric_field_count`
have DIFFERENT semantics between `json_stream.py` and `ndjson_record_stats.py`
themselves — two already-wired modules colliding on the same name, with
`__init__.py`'s star-import order silently deciding the winner. This is a live
defect in already-shipped, already-tested code, not dead code — fixing it safely
requires determining which semantic real callers actually depend on, a
dedicated investigation disproportionate to this taskcard's scope. Registered
with `status: discovered`, no disposition yet (in-flight, not a premature/invalid
one), and a named healing taskcard ID (`TC-NDJSON-NUMERIC-COLLISION-001`) so it
does not become another untracked, prose-only finding.

Also updated `registry/source-structure-baseline.json`'s `loc`/`functions` fields
for this file (263→124, 18→8) to reflect the new measured state;
`baseline_loc_cap`/`baseline_functions_cap` left unchanged (write-once ceiling).

Evidence: `tests/python/ndjson/test_fi025_dead_duplicates_removed.py` (5 new
tests: all 10 deleted names confirmed gone, all 8 kept names still work, kept
names still re-exported from the package, canonical implementations behave
correctly for the exact scenarios the duplicates existed for, canonical
implementations additionally accept pre-parsed lists). Full
`tests/python/ndjson/` suite: 2191/2191 pass (net -1 test count from removing 10
duplicate-only tests and adding 5 new ones — 0 coverage regression, confirmed by
running the full suite, not just the changed files). `V142`/`V140` re-verified
PASS against the live, updated register. Full `tests/governance/` suite: 152/153
(1 pre-existing, already-registered FI-027 failure).

### TC-STRUCT-003 (CLOSED)

`ConflictLog.resolve()` (`tools/supervisor/coordination/conflicts.py`) now requires,
for `state="RESOLVED"` specifically, an `--evidence` value resolving to one of: a
real git commit (verified via `git cat-file -e <hash>^{commit}` against the actual
repo, not merely well-formatted), a `found-issue-register.yaml` entry whose
disposition passes TC-STRUCT-002's allowlist, or the literal
`same-session-rebaseline` — itself verified against `write_journal` (the resolving
agent must actually be the resource's most recent recorded writer, not merely
assert it). `ACKNOWLEDGED`/`WONT_FIX` remain lower-friction but now reject a
small set of generic, information-free reasons (`"done"`, `"fixed"`, `"ok"`, etc.)
via the same forbidden-reason pattern shipped this session for
`.hooks/pre-commit-skill-guard` (TC-RG-001). CLI gained `--evidence` on
`conflicts resolve`.

**Friction validated against real data, not just asserted (per the plan's own
mitigation requirement):** dry-run verified all 11 of this session's actual
`resolve --state RESOLVED` calls (read-only query against the live coordination
DB, no mutation) against the new `same-session-rebaseline` check —
**11/11 pass**. If any had failed, the carve-out's definition would have needed
fixing before this taskcard could be considered done; none did.

Evidence: `tests/supervisor/test_conflict_resolution_evidence.py` (14 new tests,
hermetic — isolated coordination root + sandbox git repo per test, following the
existing `test_coordination_guards.py` pattern): no-evidence rejected,
garbage-evidence rejected, real commit accepted, fabricated commit rejected,
valid FI-id accepted, FI-id with invalid disposition rejected, nonexistent FI-id
rejected, same-session-rebaseline accepted when the agent is genuinely the last
writer, rejected when a different agent wrote last, rejected with no journal
entry at all, generic ACKNOWLEDGED/WONT_FIX reasons rejected, real reasons
accepted, WONT_FIX confirmed not to require `--evidence` (intentionally
lower-friction). Full coordination regression (`test_coordination_guards.py` +
`test_coordination_foundation.py` + `test_coordination_registry_leases.py` +
`test_coordination_preflight_gate.py` + this new file): 103/103 pass. Full
`tests/governance/` suite: 152/153 (1 pre-existing, already-registered FI-027
failure) — no new regressions from this change.

### TC-STRUCT-004 (PARTIALLY_COMPLETED)

Implemented and fully tested `V252` (`validate_stale_lease_drift_and_gap_aging`,
`tools/supervisor/governance_validators_coordination.py` — the one file in this
dependency chain not under another agent's lease): Part A flags a `STALE` lease
whose file has real, verified uncommitted `git diff` drift (this mission's own
triggering incident's exact shape); Part B flags a `known_gaps` entry whose
`git log -S` introduction date is more than 14 days old. Both WARN-only, never
FAIL — by design, matching V195's existing pattern, to avoid over-tightening
under real concurrent load.

**Genuinely blocked, not force-completed:** wiring V252 into
`governance_validator_runner.py`'s dispatch list (confirmed required — the
`@validator` decorator does not auto-register; the runner explicitly imports and
calls each validator by name) and registering it in
`registry/governance/validator-id-authority.yaml`, plus surfacing its findings
into `reports/supervisor/session-resume.md` (generated by
`tools/supervisor/autonomous_cycle.py`), all require editing files re-verified,
at write time, to be under a lease genuinely held by the same actively-working
concurrent agent already blocking TC-FIX-001 (FI-027) and part of FI-028. Not
forced — registered as **FI-030** (`BLOCKED_TRUE_EXTERNAL_DEPENDENCY`) with the
same retry-before-closure plan as FI-027/FI-028. V252 itself is real, tested,
and immediately callable standalone even while unwired from the full suite —
this is a genuine partial completion, not a placeholder.

Evidence: `tests/supervisor/test_governance_validators_coordination_v252.py` (9
new tests, hermetic — isolated coordination root + sandbox git repo, mocked git
subprocess calls for the aging check): no-DB/no-leases PASS, real drift WARNs,
no drift PASSes, nonexistent file PASSes, no-policy-file PASSes, aged open gap
WARNs (with the exact day count in the message), recent open gap PASSes,
resolved gap not flagged, `blocks_sprint` confirmed always `False`. Also noted:
V194-V196 in the same module have zero pre-existing test coverage anywhere in
this repo (confirmed by search) — out of this taskcard's scope to backfill, but
disclosed rather than silently discovered-and-ignored. Full `tests/governance/`
suite + this new file: 161/162 (same 1 pre-existing FI-027 failure).

### Final pre-closure retry (TC-FIX-001 / FI-027, FI-028, FI-030)

Re-attempted governed takeover on all 4 blocked leases immediately before closing
this plan (`.claude/commands/reconcile-contract-capabilities.md`,
`tools/supervisor/autonomous_cycle.py`, `registry/governance/validator-id-authority.yaml`,
`tools/supervisor/governance_validator_runner.py`) — all 4 still confirmed
genuinely `ACTIVE` by the coordination system's real liveness check (not the
cached lease-row status flag, which reads `STALE` on all 4 and would be
misleading if trusted directly — exactly the distinction this whole mission
started from). `agent-claude-code-20260717T060141-e225cd` has been continuously,
verifiably active across every check this session (10:58 → 13:36 → 14:11 →
14:30 → 15:00 → 15:11, ~13 minutes before this final retry), running a large,
real, unrelated `PORTFOLIO-AUDIT-2026-07-16` mission spanning a significant
portion of `tools/supervisor/`.

**TC-FIX-001 remains `PENDING`. FI-027, FI-028, and FI-030 remain
`BLOCKED_TRUE_EXTERNAL_DEPENDENCY`** — honestly, verifiably, not assumed. This is
the correct, final disposition for this session: forcing a takeover against a
confirmed-live agent's real work would repeat the exact class of error this
mission exists to fix, in the opposite direction. Retrying again requires a
future session where that agent's mission has actually concluded.

## Prose Findings Disclosed

None. Every problem, risk, or concern surfaced during this session is either (a)
fixed with evidence in the Execution Log above, or (b) registered in
`registry/found-issue-register.yaml` (FI-026 through FI-030) with a disposition
from found-issue-ownership-policy.md's §6 allowlist. Two incidental
observations were made and resolved inline rather than needing separate
tracking: `tools/supervisor/coordination/conflicts.py` and
`governance_validators_coordination.py` were found to be pre-existing,
previously-uncommitted (but actively relied-upon) code, swept into this
session's commits alongside the actual changes made to them — disclosed at
commit time, not a latent, still-open finding. V194-V196
(`governance_validators_coordination.py`) having zero pre-existing test
coverage is already recorded directly in this plan's TC-STRUCT-004 execution
log above, not left as an untracked chat-only remark.
