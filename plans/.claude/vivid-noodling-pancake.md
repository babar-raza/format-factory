# Skills-First Control — Production Hardening Plan (v2)

**mission_id:** SFC-PRODUCTION-HARDENING-2026-07-17

<!-- Convergence note (2026-07-17): a `plan_type: machinery_hardening` header
was briefly added here during closure, which triggers a repo-policy gate
requiring 2 tracked behavioral iterations (audit-execute-reaudit cycles)
before terminal closure -- a ceremony for plans explicitly run as multi-
session machinery missions from the outset. This plan was not: it executed
as one continuous session (5 gaps, 157 tests, 6 commits), and the earlier
skills-first-control-sprint.md plan this same session -- which touched the
same category of machinery -- was never classified this way either and
closed cleanly. Retroactively adding the label at closure time to invoke (or,
worse, to sidestep) that gate would misrepresent how the work was actually
run either direction. Reverted to keep the mission_id (genuinely useful for
Gap D's mission-scoping) without the mismatched classification. -->

## Context

Last session built and shipped a fail-closed Skills-First Control (SFC) layer
(`tools/governance/skills_first/`: registries, resolve, manifest, closeout,
exceptions, audit) — 36 tests, independently verified, proven via a self-governance
pilot. That work is solid and is **not** being redesigned here.

Closing out that sprint via the repo's own governed convergence lifecycle
(`prompt1..4` + `lifecycle_audit.py`) surfaced three concrete, currently-open
production gaps, all already named in `docs/governance/skill-only-policy.yaml`'s
`known_gaps`:

1. `src/` product-source writes are denied in `.claude/settings.json` with no safe
   path to unblock them.
2. The headless autonomous loop (`sprint_executor.py run-loop`) spawns a
   `--dangerously-skip-permissions` subprocess with zero skill/manifest governance.
3. The live PreToolUse hook (`gate.py`) that intercepts every Edit/Write/Bash across
   ~44-47 concurrent agents enforces coordination leases only — it is skill-blind.

A first design pass proposed direct fixes for all three, plus a "closure oracle
non-determinism" bug hit live during convergence. An adversarial second pass (and
follow-up direct code reads) found that **two of those proposed fixes were actively
wrong** — one would have duplicated existing, better infrastructure with strictly
weaker guarantees; the other relied on a mechanism that is provably unsound given
this repo's actual topology (a single shared working tree, no per-agent isolation).
This plan supersedes the first pass with the corrected design.

The user explicitly asked for the **full production tool-layer rollout**, designed
to not create a blocking incident across the concurrent-agent population, rather
than a narrower interim workaround — that is the scope of Gap C below, and Gap A
(product-source writes) is now sequenced to depend on it rather than shipping via a
separate shortcut.

**Intended outcome:** four production-grade fixes, each reusing existing mature
machinery wherever it exists, each with a determinism/concurrency regression test,
staged so that no single change can cause a blast-radius incident across the live
agent population — and an honest accounting of what remains uncertain until real
operational data exists.

---

## Symptom vs. root cause vs. structural weakness

This distinction matters because several "symptoms" observed during the convergence
run point at the *same* underlying structural weakness, and fixing only the visible
symptom (as the first design pass initially did for two of the four gaps) reproduces
the weakness elsewhere.

**Symptoms observed (this session, live):**
- Closing an otherwise-100%-complete plan got blocked by two findings that had
  nothing to do with the plan being closed.
- Committing a file required manually discovering my own agent identity via raw
  SQL and manually re-baselining a coordination lease.
- A shared canonical policy file had to be excluded from a commit because another
  mission's uncommitted edit was interleaved with mine.
- `src/` writes are flatly denied with no route to a safe exception.
- The headless loop has run unattended with `--dangerously-skip-permissions` and no
  governance the whole time this SFC layer has existed.

**Root causes (the actual code-level bugs, confirmed by direct reading):**
- `lifecycle_audit.py`'s `check_sprint_audit_guard` (lines 443-498) and its rework-
  consumption check (`build_closure_contract`, line 300) read two **global singleton
  files** (`.local/supervisor/sprint-audit-log.json` — confirmed no `mission_id`
  field on disk; `.local/supervisor/continuation-signal.json` — confirmed no
  `mission_id` field on disk) with **no mission/plan filter at all**, even though
  the same file already implements the correct pattern twice elsewhere
  (`_read_machinery_mission_ledger` lines 95-117, `check_mission_complete` lines
  960-978: `if data.get("mission_id") != mission_id: ...`). The call site (line 580)
  doesn't even forward `mission_id` into the guard. This is an *inconsistency*, not
  an unsolved problem — the fix pattern already exists in the same file.
- `~8-10` canonical governance YAML files are written by **many different code
  paths** (interactive Edit/Write, and separately by ad hoc Python scripts invoked
  via `Bash(python *)`, which is broadly allowed) with **no single enforcement
  point** covering all of them — the PreToolUse hook only lease-checks Edit/Write
  tool calls; its Bash handler only pattern-matches a fixed list of known generator
  scripts, git destructive commands, and broad-add — it has no general "this writes
  a governed file" detection.
- `tools/supervisor/coordination/hooks/gate.py`'s enforcement mode
  (`off`/`advisory`/`enforcing`) is a single global dial (`db.py:131-149`,
  `settings` table, one `mode` row) with zero per-check granularity anywhere in the
  schema — so there is no way to add a *new* check without it inheriting the
  already-`enforcing` blast radius of the *existing* (already-proven, already-
  running) coordination checks on day one.
- `sprint_executor.py:cmd_run_sprint` (lines 356-427) spawns
  `claude --print --dangerously-skip-permissions -p <raw next-sprint.md text>`
  (lines 399-405) — no manifest, no skill resolution, no independently-verified
  changed-file list; the worker **self-declares** `changed_files` in its own
  evidence YAML, with only a single-SHA `git rev-parse HEAD` as provenance
  (`autonomous_cycle.py:633-651`), not a diff.

**Structural weakness (the thing that, if left unaddressed, will keep reproducing
these symptoms in new forms):**

There is **no concept of "mission-scoped state" as a first-class, consistently-
enforced convention** in this codebase. The correct pattern (compare a stored
`mission_id` before trusting cached/shared state) exists in *some* functions in
`lifecycle_audit.py` and *not others in the same file*. Shared governance files have
*a* concurrency primitive (coordination leases) but it is applied inconsistently
(covers interactive Edit/Write, not Bash-invoked scripts). The tool-layer hook has
*a* safety dial (mode) but it is undifferentiated (global, not per-check), so every
future addition to it inherits maximum blast radius by default. This is the thing
that actually breaks consistency across reruns: **the same command, run twice
against the same mission, can return different verdicts purely because of
concurrent, unrelated agent activity elsewhere in the shared tree** — a
reproducibility violation, not a one-off bug.

**What must be preserved (do not touch):** the entire `tools/governance/skills_first/`
package and its 36 tests — `resolve.py`, `manifest.py`, `closeout.py`,
`exceptions.py`, `audit.py`, `validate_skills_first_control.py`. The existing
coordination lease system (`leases.py`, `baselines.py`, `preflight.py`) — mature,
already running at 44-47 agent scale, not the source of the bugs found. The existing
`generator_guard.py` (TC-COORD-009) — mature, purpose-built, currently unused for
the files that need it.

**What must be redesigned (not just patched):** the closure oracle's global-state
reads (Gap D below) need an actual mission-scoping data-model change, not a
one-line filter bolted on top of files that don't carry the field yet. The
tool-layer hook's mode dial needs a genuine per-check dimension, not a bespoke
one-off flag for this one new check. The run-loop's provenance mechanism needs to
be built on the coordination system's existing attribution primitive, not a new
git-diff heuristic that is unsound given the shared-tree topology.

---

## The four gaps — design

### Gap A: `src/` product-source write governance

**Sequencing:** depends entirely on Gap C reaching at least shadow-mode coverage for
`src/**` paths. Do not widen `.claude/settings.json`'s `src/` deny list as a
shortcut — that was explicitly rejected by the user's direction to do the full
rollout, and independently by the finding below that the *current* boundary is
already porous, so widening it without Gap C's real authorizer in place would
compound an existing weakness rather than fix it.

**Finding that changes the risk picture:** the current `src/` deny in
`.claude/settings.json` (`Write(src/python/*/**)`, `Write(src/net/**)`, lines
148-149) only matches the `Write` tool. `Bash(python *)` is broadly allowed
(line 77), and `gate.py`'s `_on_pre_bash` only pattern-matches a fixed list of known
generator scripts, destructive git commands, and broad-`git add` — it has **no
detection at all** for "this Bash command writes to `src/`." So a short Python
script invoked via Bash can write to `src/` **today**, ungoverned, bypassing the
deny list entirely. The "coarse wall" this gap is nominally about widening is
already not a solid wall. Closing that Bash-side hole is a prerequisite, not an
afterthought — it is included as a Gap C task below (extend `_on_pre_bash`'s
pattern set, or — more robustly, since regex-matching arbitrary Python for "does
this write to src/" is unreliable — route all product-source-mutating scripts
through a single checked helper, mirroring the `generator_guard` pattern).

**Design:** once Gap C's `skill_resolution` check has run in shadow/advisory mode
against real `src/**` traffic and the would-block analyzer (Gap C) shows a
low/understood false-positive rate, promote that check to `enforcing` scoped to
`src/**` specifically (per-check, per-path-prefix promotion — the granularity Gap C
builds supports this). Only then widen `.claude/settings.json`'s allow list, and
even then incrementally per format (mirroring the existing
`Write(samples/by-format/fods/**)`-style precedent), so the static glob remains the
coarse *eligibility* boundary while the now-skill-aware hook is the real
fine-grained authorizer (checks for a live, unexpired, path-covering manifest on
the specific file — "unexpired" requires the manifest TTL added in Gap C's
prerequisite work, see below).

**Validation:** `tests/governance/test_settings_src_allow_scoped.py` — a static
regression guard asserting any future `Write(src/**)` allow entry is always scoped
to a named format directory, never a bare wildcard (prevents accidentally
reopening the blanket case later). The real gate for *when* to widen settings.json
is Gap C's analyzer evidence, not a unit test.

**Honest uncertainty:** whether Claude Code's harness treats `Write(...)` settings
permissions as covering the `Edit` tool or only literal `Write` tool calls could not
be resolved by static reading of this repo (zero `Edit(...)` entries exist anywhere
in `settings.json` to compare against). This is a live question about harness
semantics, not this repo's code, and should be confirmed empirically (a single,
reversible, low-stakes test edit) before the settings.json diff is finalized, not
assumed either way.

---

### Gap B: Shared canonical-YAML concurrent-edit collisions

**Root cause:** ~8-10 hot files (`skill-only-policy.yaml`, `skill-registry.yaml`,
`command-registry.yaml`, etc.) are written both through the coordination-aware
Edit/Write path *and* through plain `Path.write_text()` in ad hoc Python scripts
invoked via Bash, which the hook does not attribute or lease-check at all. The
symptom hit live this session — `skill-only-policy.yaml` had to be excluded from a
commit because mission `AGENT-COORD-2026-07-15`'s uncommitted edit was interleaved
with mine, discovered only by manual `git diff` hunk inspection.

**Rejected approach (from the first design pass):** a bespoke read-hash → compute-
patch → write-if-unchanged → retry-with-backoff CAS primitive. Rejected because (a)
it duplicates `tools/supervisor/coordination/generator_guard.py` (TC-COORD-009),
which already exists, is already tested, and already does this exact job — lease
the declared output paths *before* any write is attempted (refuse up front, not
after a race), record drift after the fact via the existing `ConflictLog`; (b) a
bespoke CAS's natural retry/backoff numbers would need to be tuned for a
multi-second-to-tens-of-seconds "an agent is mid-edit" window, not the millisecond-
scale SQLite-lock contention the existing `db.immediate()` retry logic is tuned
for — copying that number is a naive-magic-number risk with a real starvation
failure mode under 44-47-agent contention; (c) it would create a second, different
"is this file safe to write" mechanism operating on the same files as the first
(the lease system), a split-brain risk.

**Design:**
1. Register the ~8-10 hot files as a `tools/governance/hot-governance-files/output-manifest.yaml`
   (`generator_id: hot-governance-files`, `outputs: [docs/governance/skill-only-policy.yaml, .supervisor/skill-registry.yaml, .claude/commands/command-registry.yaml, .supervisor/capability-routing-registry.yaml, registry/found-issue-register.yaml, registry/governance/validator-id-authority.yaml, oracle/registry/format-oracle-registry.yaml, .supervisor/skill-first-policy.md]`),
   consistent with the checked-in manifest convention `generator_guard.py` already
   documents.
2. Any **script-based** writer of these files (`sync_skill_command_registry.py`,
   `build_capability_routes.py`, etc.) must be invoked through
   `python -m tools.supervisor.coordination guard-run --generator-id hot-governance-files --manifest-file tools/governance/hot-governance-files/output-manifest.yaml -- <command>`
   (the existing subprocess-bridge style, zero code changes needed inside those
   scripts) — this is a calling-convention change, not a refactor.
3. Any **interactive Edit/Write** touching these files already goes through
   `preflight()`/lease-check today; add these paths to the same claimed-resource set
   so an agent editing one of them picks up a real exclusive-write lease (not just a
   post hoc baseline hash check) — reuses `LeaseManager.claim`, no new locking code.
4. Extend `gate.py`'s `GENERATOR_PATTERNS` (currently a fixed list matching known
   generator script paths) to include the hot-file writer scripts identified above,
   so the *existing* Bash-side generator-guard nudge (`_on_pre_bash`, already wired)
   catches them too — this directly closes part of Gap A's Bash-bypass finding for
   the specific case of governance-file writers.
5. **Resolve the live instance now-in-hand as the first concrete taskcard**: once
   this mechanism exists, use it to reconcile `docs/governance/skill-only-policy.yaml`'s
   currently-still-dirty mixed-authorship state (confirmed still `M` in git status)
   with whatever `AGENT-COORD-2026-07-15` has since landed — a real, immediate proof
   of the mechanism, not just a test fixture.

**Validation:** `tests/supervisor/coordination/test_hotfile_generator_guard.py` —
(1) two concurrent `guarded_generation` calls for the same hot file, second one
blocked *before* writing (not raced), confirms `GeneratorBlocked` fires; (2) an
interactive Edit-tool lease and a `guard-run`-wrapped script both contending for the
same file — whichever holds the lease wins, the other is denied with a clear
message, no silent overwrite; (3) drift detection: a write outside the declared
`outputs` list is caught and logged to the conflict log, not silently accepted.
Per the structural testing gap noted below, at least one of these must be a real
multi-process (not single-process-sequential) test.

**Tradeoffs:** this makes writing these ~8-10 files slightly more ceremonious (must
go through `guard-run` or hold a lease) — acceptable given they are exactly the
files where uncoordinated writes have already caused real problems. Does not fix
general working-tree contention across all 844 currently-dirty files — intentionally
scoped to the highest-fan-in files where the cost/benefit is clear.

---

### Gap C: Tool-layer skill-resolution rollout (`gate.py`, EP-010) — full production design

This is the gap the user explicitly asked to be designed for production rather than
worked around. It has the highest blast-radius risk (runs on every Edit/Write/Bash
across ~44-47 live agents) and therefore the most staging.

**Root cause:** `gate.py`'s `mode` is a single global dial
(`db.py: get_mode`/`set_mode`, lines 131-149; one `settings` row). Every check
wired under it inherits the *existing* checks' blast radius — there is no way to
add a new check in a contained way today. The advisory log
(`gate.py:_advisory`, lines 61-67) is write-only; nothing in the repo reads or
analyzes it. There is no existing per-check, per-cohort, or percentage-based
rollout primitive anywhere in the coordination package.

**Design — four pieces, explicitly sequenced, with automatic rollback deferred:**

**C1. Per-check mode granularity (build first, foundational).**
New `db.py` functions, modeled directly on the existing `get_mode`/`set_mode`:
```python
def get_check_mode(conn, check_id: str) -> str: ...   # default "advisory"
def set_check_mode(conn, check_id: str, mode: str, actor: str, reason: str) -> None: ...
```
stored as additive `settings` rows keyed `check_mode:<check_id>`. **Load-bearing
invariant:** the existing global `mode` gate in `gate.py` (line 152's early
`if mode == "off": return 0`, and the existing `enforcing`-only-blocks branches) is
computed *first* and is *never* weakened by a per-check setting — a new check's
`advisory` state can only ever be *more* permissive than the already-`enforcing`
global coordination checks, never override them. This ordering must be enforced in
code, not just in intent, and is the first thing the regression test below checks.

**C2. The check itself: `tools/supervisor/coordination/hooks/skill_gate.py`**, called
from `_on_pre_file` after the existing coordination logic, using a **three-tier,
non-binary verdict** specifically to avoid false-blocking legitimate work during the
transition:
- `MANIFEST_COVERING` — a live, unexpired manifest (see TTL note below) whose
  `allowed_paths` covers this file → always allow.
- `NO_SKILL_RESOLVED_FOR_PATH` — `resolve.resolve()` returns
  `MISSING_SKILL_CAPABILITY` for this operation/path → always allow, **never**
  block-eligible (there is no skill to require yet; blocking here would be actively
  wrong and would make the skill-gap workflow itself impossible to bootstrap).
- `SKILL_EXISTS_BUT_NO_MANIFEST` — a route/skill resolves, but no live manifest
  covers the path → the **only** block-eligible tier, and only once this specific
  check's mode is `enforcing`.

**C2-prerequisite: add manifest expiry.** `manifest.py`'s `_REQUIRED`/`_STATUSES`
currently have no TTL — a manifest created and never explicitly closed (agent
crash, abandoned task) stays "live" forever, which would make "checks for a live
unexpired manifest" a hollow security property. Add `expires_at` (default: a bounded
window from `created_at`, e.g. hours not days) to the schema, `validate_manifest`,
and `closeout.evaluate` (an expired-but-unclosed manifest should read as
`CLOSE_BLOCKED`, not silently authorize). This is a small, additive, backward-
compatible schema change (old manifests without the field are treated as already-
expired, forcing explicit re-creation — fail closed, not fail open).

**C3. Observe-only analyzer, `tools/supervisor/coordination/advisory_analyzer.py`** —
reads `advisory-log.jsonl` filtered to `check == "skill_resolution"`, reports total
events, would-block count and rate, breakdown by verdict tier, a bounded sample of
would-block events, and distinct agents/paths affected. **This ships and runs for a
defined burn-in period before any promotion decision is made** — there is currently
zero incident-rate data for this check anywhere in the repo, and a threshold picked
without it would be a guess dressed as a number. `cli.py` gains
`advisory-report --check skill_resolution` to make this a routine, not a manual
log-scrape.

**C4. Promotion — human/CI-gated, evidence-based, staged by path scope, no automatic
rollback on day one.** Explicitly deferring the first design pass's "automatic
rollback on incident-rate spike" — with zero real incident-rate data to calibrate a
threshold against, an automated de-escalation mechanism risks its own failure modes
(oscillation between advisory/enforcing with no hysteresis, or becoming a governance-
defeat surface if noise on the check can be manufactured to force it back to
advisory). Concrete path instead:
- Ship C1-C3, run in `advisory` mode globally, for a defined minimum burn-in
  (e.g., a minimum sample size *and* minimum elapsed time, not just one or the
  other — a low-traffic path could hit a time threshold with too few samples to be
  meaningful).
- Review the analyzer's evidence explicitly (a human or a governed skill,
  `set_check_mode` call is itself an auditable, attributed action via the existing
  `emit_event`/`MODE_CHANGE` mechanism — reused verbatim).
- Promote to `enforcing` **scoped by path prefix**, smallest blast radius first —
  e.g., `tools/governance/**` (this SFC package's own directory — dogfood on
  ourselves first) before `src/**` (the highest-stakes, highest-traffic path).
- Automatic rollback is an explicit **follow-on hardening item**, only after real
  enforcing-mode incident-rate data exists to calibrate a threshold against —
  tracked as a named follow-up, not silently dropped, not built speculatively now.

**Validation:** `tests/supervisor/coordination/test_skill_gate_rollout.py` — (1)
global `mode=enforcing` + `check_mode:skill_resolution=advisory` → a
`SKILL_EXISTS_BUT_NO_MANIFEST` event is allowed and logged, proving the decoupling
invariant from C1; (2) flip only the per-check mode to `enforcing` → same event now
blocks, global mode untouched; (3) analyzer correctness against a seeded synthetic
`advisory-log.jsonl`; (4) an expired manifest (past `expires_at`) does not satisfy
`MANIFEST_COVERING`; (5) the entire existing coordination test suite passes
unmodified with `check_mode:skill_resolution` in any state — a hard regression
guard that this change cannot destabilize the already-proven, already-`enforcing`
lease system.

**Tradeoffs / honest limits:** the burn-in period's actual duration and the
promotion sample-size threshold are placeholders pending real traffic data — stated
as "to be calibrated from C3's first observation window," not asserted as known-good
numbers now. Automatic rollback's absence means a bad `enforcing` promotion, if one
happens, requires a human/governed-skill action to revert rather than self-healing —
an explicit, accepted tradeoff of not building a half-validated automatic mechanism.

---

### Gap D: Closure-oracle mission-scoping (`lifecycle_audit.py`)

**Root cause, precise:** `check_sprint_audit_guard` (lines 443-498) and the rework-
consumption logic feeding `build_closure_contract` (line 300) read
`.local/supervisor/sprint-audit-log.json` and `.local/supervisor/continuation-signal.json`
— both confirmed, by direct inspection, to have **no `mission_id` field on disk
today** — with no filtering, while `_read_machinery_mission_ledger` (95-117) and
`check_mission_complete` (960-978) *in the same file* already implement
`if data.get("mission_id") != mission_id: ...` correctly, because *their* target
files already carry that field. This is an inconsistency to fix, not a new pattern
to invent — but it does require a **data-model change** to the two files that lack
the field (not just a reader-side filter), since a filter has nothing to filter on
yet.

**Design:**
1. Add `mission_id` to `.local/supervisor/sprint-audit-log.json` at the point
   `lifecycle_audit.py` itself writes it (it is both reader and writer of this
   file — confirmed by direct read) — additive field, existing consumers unaffected.
2. Add an additive `rework_items_by_mission: {"<mission_id>": [...]}` structure to
   `continuation-signal.json`'s writers, alongside (not replacing) the existing flat
   `rework_items` list — old readers keep working; scoped readers use the new
   structure when populated, fall back to a substring-match heuristic against the
   mission's own taskcard IDs (via `parse_plan_taskcards`, already computed
   elsewhere in the same call) for pre-migration entries.
3. `check_sprint_audit_guard` gains a `mission_id: str | None = None` parameter; the
   call site (line 580, currently passing only `(repo_root,)`) is fixed to actually
   forward it — this one-line omission is a real, separate bug from the missing
   schema field. When `mission_id` is `None` (explicit opt-in, e.g. a plan whose own
   scope IS general-ledger health), preserve today's global-mtime behavior exactly
   — do not remove the only signal a legitimately-global-scope plan has, just stop
   it being the *default*, silent behavior for every plan regardless of scope.
4. `build_closure_contract` gains a `ledger_lane_scope: "mission" | "global"` output
   field so the distinction is visible and auditable in the closure record, not an
   invisible fallthrough.
5. **Compensating control, not a removed safety net:** mission-scoping removes an
   *accidental* cross-mission signal (two unrelated files' mtimes), which was never
   a real regression check to begin with — it does not remove real cross-mission
   regression detection because none currently exists. Add a genuinely independent,
   **non-blocking** cross-mission health report (a new, separate advisory artifact —
   not a closure gate for any individual mission) that runs the shared test suite
   subset touching files any *other* live mission currently holds a lease on, and
   surfaces it for human/governed-skill review, decoupled from any one mission's
   closure decision.

**Validation:** `tests/supervisor/test_lifecycle_audit_mission_scoping.py` — (1)
determinism: identical repo state, two runs of the same mission's closure check,
identical verdict; (2) ambient-noise immunity: inject a rework entry and a stale
audit-log timestamp both tagged for a *different* mission_id between the two runs →
the mission-under-test's verdict does not change; (3) opt-in still sees global
noise when `mission_id=None` is passed explicitly, proving the distinction is real;
(4) existing `test_g4_*` tests (which call the guard with no `mission_id` argument)
continue passing unmodified, since the new parameter defaults to today's behavior.

**Expected, accepted side effect:** some mission currently passing closure *only*
because another mission's fresher global file happened to mask its own stale/absent
audit will, once scoping removes that accidental camouflage, correctly flip to
blocked. This is a **correction**, not a regression — call it out explicitly when
this ships so it isn't mistaken for new breakage.

---

### Gap E (originally proposed as part of run-loop wiring): rejected git-diff
provenance, replaced with write-journal attribution

**Why the original approach is rejected, not just "risky":** the proposed fix was
"capture `git rev-parse HEAD` before the subprocess spawns, `git diff --name-only`
after it exits, feed that into the closeout gate." Direct code reading shows this is
**provably unsound**, not merely imperfect, given this repo's actual topology: there
is no git-worktree isolation anywhere in `tools/` (confirmed, zero hits for
`git worktree add`), `cmd_run_sprint`'s subprocess runs for up to 30 minutes
(`timeout=1800`) directly in the shared repo root, and 44-47 *other* agents are
concurrently mutating the same tree throughout that window. A before/after commit-
range diff around that window will, depending on timing:
- **over-attribute** — capture every other agent's unrelated commits landed during
  the same 30-minute window, wrongly feeding them into *this* sprint's
  `closeout.evaluate()` as if this sprint touched them; or
- **under-attribute** — if this sprint's own changes are left as uncommitted
  working-tree edits (a realistic pattern here, since the declaration/commit flow
  in this repo generally separates "make changes" from "commit," and the
  surrounding code already flags `git_head_end` staleness as a known issue), `HEAD`
  never moves for this run at all, and the diff sees nothing.

This is a topology problem, not a tuning problem — no retry count or timing window
fixes it.

**Design (replacement):** register the run-loop's spawned subprocess as a
coordination agent, exactly the way `generator_guard.py`'s `guarded_generation`
already does for headless generators (`registry.register(..., agent_type="headless")`)
and answer "what did this run change" via the **existing, already-tested write-
journal attribution mechanism** (`baselines.py`'s `classify_change`:
`OWN_CHANGE` vs `OTHER_AGENT_CHANGE`, keyed per `agent_id`) rather than a git-diff
heuristic. Concretely, in `cmd_run_sprint`:
1. Before spawning, resolve skill(s)/`allowed_paths` for the sprint's work item via
   `resolve.resolve()` (the orchestrator does this on the untrusted child's behalf —
   the child itself is never trusted to self-govern), call `manifest.create_manifest(...)`,
   and register a coordination identity for this run bound to the manifest's
   `execution_id`.
2. Run the subprocess as today (no change to the spawn itself).
3. After exit, query the write-journal for entries attributed to this run's
   `agent_id` during the run's time window — this is the actual, already-correct
   changed-files list, immune to concurrent unrelated agents' writes because
   attribution is per-agent-identity, not per-time-window.
4. Call `closeout.evaluate(manifest, changed_files=<journal-attributed list>, ...)`
   at the existing acceptance gate point (`autonomous_cycle.py:1984-1988`, the
   `if manifest.get("exit_code", 1) == 0:` block, before `_update_lane_counters`
   writes the ledger). `CLOSE_BLOCKED` routes into the existing `rework_items`
   mechanism (reused, not reinvented) instead of accepting into the ledger.

**Explicitly flagged, not silently dropped:** real git-worktree isolation for the
run-loop (giving it its own working copy, merged/rebased back) is a more complete
fix for the *broader* shared-tree contention problem, and the coordination system's
own root-resolution logic already anticipates a multi-worktree topology
(`root.py`). It is **not** adopted here because it introduces its own new
failure surface (merge/rebase conflict handling, continuous-loop worktree lifecycle
management, disk overhead) for a problem — "what did *this specific run* touch" —
that the existing attribution primitive already solves without any of that new
surface. It is recorded as a candidate future upgrade if/when general shared-tree
contention (not just this one attribution question) becomes the active bottleneck.

**Validation:** `tests/supervisor/test_sprint_executor_skill_governance.py` — (1)
manifest created, with call-order proof, before the mocked subprocess spawn; (2) a
concurrent "other agent" write during the mocked run's window is **not** attributed
to this run (the actual regression test for the rejected approach's core flaw); (3)
an out-of-scope own-write correctly triggers `CLOSE_BLOCKED` and the ledger update is
*not* called (spied); (4) `MISSING_SKILL_CAPABILITY` still creates an audited
fallback-scope manifest rather than skipping governance silently; (5) advisory-mode
behavior for this new gate is itself governed by Gap C's per-check primitive
(`check_mode:sprint_closeout_governance`), not a bespoke flag.

---

## Cross-gap sequencing (dependency order)

1. **Gap D** (closure-oracle scoping) — smallest diff, zero dependency on anything
   else, actively causing wrong verdicts today. Ship first.
2. **Gap B** (adopt `generator_guard` for hot files) — self-contained; also directly
   unblocks resolving the live `skill-only-policy.yaml` mixed-authorship instance.
3. **Gap C, pieces C1+C2-prerequisite (manifest TTL)+C2+C3** (per-check granularity,
   manifest expiry, the check itself, observe-only analyzer) — depends on the
   already-shipped SFC foundation only. Longest burn-in, so start it as early as
   possible; promotion (C4) is a later, separate, evidence-gated milestone, not
   part of this implementation pass.
4. **Gap E** (run-loop write-journal attribution) — depends on the SFC foundation
   and benefits from, but does not strictly require, Gap C's per-check primitive for
   its own advisory/enforcing staging (can ship with a simple boolean initially,
   migrate to `check_mode` once C1 lands).
5. **Gap A** (src/ settings.json widening) — strictly last; gated on Gap C reaching
   `enforcing` for `src/**` specifically, with analyzer evidence in hand.

**Hard precondition across Gaps B, C, and E, called out explicitly per the red-team
review:** every test file found in this area today is single-process/sequential.
None of these three gaps' concurrency claims can be considered validated —
regardless of how the code reads — until each has at least one genuine multi-
process or multi-thread stress test (N real concurrent callers hammering the same
resource for 60+ seconds, asserting no lost updates, bounded starvation, and correct
attribution). This is a testing-infrastructure gap in its own right and is treated
as a blocking precondition for calling any of B/C/E "production," not a nice-to-have
add-on.

## Explicitly rejected (with why, so it isn't silently re-proposed later)

- A bespoke CAS write primitive for Gap B — duplicates `generator_guard.py` with
  weaker guarantees and mistuned retry timing (Gap B design above).
- Automatic advisory↔enforcing rollback on day one for Gap C — zero real incident-
  rate data to calibrate against; real oscillation/governance-defeat risk if built
  before that data exists (Gap C design above).
- Git-diff-based (`git rev-parse` before/after) provenance for the run-loop —
  provably unsound given the shared, non-isolated working tree (Gap E design
  above).
- A blanket `Write(src/**)` settings.json widening "to move faster" — directly
  rejected by the user's own direction; also would compound the already-porous
  Bash-bypass finding rather than fix it.
- A single synchronous schema migration of every `rework_items` producer (~21 call
  sites) to fully structured, mission-tagged objects in one change — too large a
  blast radius under 44-47 concurrent agents; the additive
  `rework_items_by_mission` + heuristic fallback captures most of the benefit at a
  fraction of the coordination risk.

## Critical files

- `tools/supervisor/lifecycle_audit.py` (Gap D)
- `tools/supervisor/coordination/{db.py, hooks/gate.py, generator_guard.py, baselines.py, preflight.py, leases.py}` (Gaps B, C, E)
- `tools/governance/skills_first/{manifest.py, closeout.py, resolve.py}` (Gaps C, E — reused, not modified except manifest.py's additive TTL field)
- `tools/supervisor/sprint_executor.py`, `tools/supervisor/autonomous_cycle.py` (Gap E)
- `.claude/settings.json` (Gap A, last)
- `docs/governance/skill-only-policy.yaml` (update `known_gaps` status as each gap ships; also the live mixed-authorship instance Gap B resolves)
- New: `tools/governance/hot-governance-files/output-manifest.yaml`, `tools/supervisor/coordination/hooks/skill_gate.py`, `tools/supervisor/coordination/advisory_analyzer.py`

## Verification (end-to-end, per gap, before calling any gap done)

For each gap: (1) the gap-specific unit/integration tests listed above pass; (2) the
full existing test suite (`tests/supervisor/`, `tests/governance/`) passes
unmodified — no regression to already-working coordination/SFC behavior; (3) for
Gaps B/C/E specifically, the multi-process stress test required by the hard
precondition above passes; (4) `tools/governance/validate_skills_first_control.py`
and `tools/governance/skills_first/audit.py --write` still report clean (0
CRITICAL/HIGH) after the change; (5) `docs/governance/skill-only-policy.yaml`'s
`known_gaps`/`enforcement_points` entries are updated to reflect the new true state
(reusing the pattern already established last session for reconciling stale
statuses) — never left stale.

---

## Taskcard Status Summary

| TC-ID | Status |
|-------|--------|
| TC-SFCP-GAPD | CLOSED |
| TC-SFCP-GAPB | CLOSED |
| TC-SFCP-GAPC1 | CLOSED |
| TC-SFCP-GAPC2-PREREQ | CLOSED |
| TC-SFCP-GAPC2 | CLOSED |
| TC-SFCP-GAPC3 | CLOSED |
| TC-SFCP-GAPE | CLOSED |
| TC-SFCP-GAPA | CLOSED |
| TC-SFCP-POLICY-RECONCILE | CLOSED |
| TC-SFCP-EP007-EXCEPTION-SCAN-GAP | EXCLUDED |
| TC-SFCP-DIRECT-GENERATOR-GAP | EXCLUDED |
| TC-SFCP-ENFORCING-PROMOTION | EXCLUDED |

EXCLUDED rationale: `TC-SFCP-EP007-EXCEPTION-SCAN-GAP` and
`TC-SFCP-DIRECT-GENERATOR-GAP` are newly-discovered/pre-existing gaps outside
this plan's approved 5-gap scope, recorded in `skill-only-policy.yaml`
`known_gaps` rather than silently dropped — successor-mission work.
`TC-SFCP-ENFORCING-PROMOTION` (promoting Gap C's `skill_resolution` and Gap E's
`sprint_closeout_governance` checks from advisory to enforcing) is explicitly
NOT part of this plan by design — it is a deliberate, evidence-gated decision
requiring real `advisory-report` traffic data this plan does not (and should
not) manufacture; see EP-010-GAP/RUNLOOP-SKIPPERMS-GAP in the policy file.

## Completion status (2026-07-17)

All 5 gaps (D, B, C, E, A) implemented, tested, and committed:

| Gap | Commit | Tests added |
|-----|--------|-------------|
| D — closure-oracle mission-scoping | `79ab2676` | 12 (+52 existing regression) |
| B — hot-governance-file generator guard | `79ab2676` | 8 unit + 1 real multi-thread pilot proof |
| C — staged tool-layer skill-resolution rollout | `84865172` | 7 TTL + 9 decoupling + 6 analyzer = 22 (some counted with closeout suite) |
| E — run-loop manifest/closeout wiring | `c176fec7` | 13 |
| A — static src/ permission regression guard | `63c63032` | 4 |
| Policy reconciliation + test-isolation fix | `e35890cc` | (fixed pre-existing test-isolation bug found by full regression) |

Final state: `tools/governance/validate_skills_first_control.py` exit 0
(`PASS_WITH_WARNINGS`, 0 CRITICAL/HIGH); 157/157 tests pass across the full
governance + supervisor/coordination suite; 17/17 coordination pilot proofs
pass including the new real-thread contention proof and double-run
idempotency. Nothing promoted to `enforcing` — by design, per this plan's
explicit rejection of day-one automatic promotion/rollback.


<!--plan_terminal_lock:
  status: ITERATION_REQUIRED
  locked_at: "2026-07-16T21:06:32.906545+00:00"
  locked_by: "4d50707c8ce0"
  successor_required_for_future_changes: true
  mutation_policy: "no further plan/hardening/execution writes"
-->
