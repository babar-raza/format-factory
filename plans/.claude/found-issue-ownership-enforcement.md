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
