---
version: "1.0"
last-updated: "2026-07-14"
phase-available: "all"
gate-required: "Supervisor approval"
skill_type: ATOMIC_SKILL
idempotency: "Same target directory tree + same query (callers_of/callees_of/paths_between/complexity_hotspots/attack_surface/preanalysis) produce the same graph result for an unchanged source tree; the one-time package install is idempotent (a no-op if trailmark is already installed at the required version)"
loc_budget: "0 lines of executable code (prompt-driven workflow only; no bundled script — invokes the installed trailmark package's own CLI/API)"
test_path: "N/A (prompt-spec skill, no bundled script) — verification is the real `uv pip install trailmark` (or pip fallback) run recorded under TC-EXT-025-03/06, plus the manual scan proof"
external_skill_origin: true
external_skill_source: trailofbits/skills
external_skill_commit: cfe5d7b1619e47fb5b38b7e2561dad7e5f1e89af
external_skill_license: CC-BY-SA-4.0
risk_level: MEDIUM
created-by: TC-EXT-025-03
product_track: governance
---

# /trailmark

Builds a multi-language source-code graph (call graphs, attack-surface
mapping, blast-radius / impact analysis, taint propagation, complexity
hotspots, entry-point enumeration) over a target directory tree, via the
`trailmark` PyPI package's programmatic query API. Unlike the purely
prompt-driven reviewer skills imported earlier in this family (`sharp-edges`,
`audit-context-building`), this skill requires a one-time external package
install — that is why its `risk_level` is `MEDIUM`, not `LOW`.

## Attribution

<!--
This skill's one-time-install workflow and its programmatic query API
surface (`trailmark.query.api.QueryEngine.from_directory(...)`,
`.callers_of()`, `.callees_of()`, `.paths_between()`,
`.complexity_hotspots()`, `.attack_surface()`, `.preanalysis()`) are adapted
from the `trailmark` skill in `trailofbits/skills`, commit
`cfe5d7b1619e47fb5b38b7e2561dad7e5f1e89af`. Author, per the upstream skill's
own conventions: Trail of Bits. Licensed CC-BY-SA-4.0
(https://creativecommons.org/licenses/by-sa/4.0/).

CC-BY-SA-4.0 share-alike notice: this file is itself a derivative work of
the cited upstream skill's documented workflow and API surface (prose
adaptation only — the `trailmark` PyPI package itself is a separate,
independently-licensed third-party dependency this skill installs and calls;
no upstream *skill* code is vendored). Per the license's ShareAlike term,
this derivative file (`.claude/commands/trailmark.md`) is distributed under
the same CC-BY-SA-4.0 terms as the original. Any further redistribution of
this specific file must preserve this attribution notice and the
CC-BY-SA-4.0 license grant. This share-alike obligation applies only to this
file's adapted workflow/API text — it does not relicense any other file in
this repository, all of which remain under this repository's own license
terms, and it does not relicense the separately-licensed `trailmark` PyPI
package.
-->

This skill adapts the one-time-setup pattern and the query API surface from
Trail of Bits' `trailmark` skill (`trailofbits/skills`, CC-BY-SA-4.0), commit
`cfe5d7b1619e47fb5b38b7e2561dad7e5f1e89af`. The install-then-query workflow
and the named query methods are carried over near-verbatim from the upstream
skill; the FF-specific primary-target scope
(`tools/supervisor/` + `tools/governance/`) and the fallback install path
(`.venv/Scripts/pip install trailmark` when `uv` is unavailable) are original
to this repository. Cleared by `/skill-scanner` per TC-EXT-012's mandatory
gating rule.

## Purpose

FF's only existing blast-radius mechanism today is
`/found-issue-ownership` Step 4 — and it is **reactive, manual, and
single-pattern-grep**: it runs only *after* a bug has already been found, and
it searches for one specific pattern at a time rather than mapping the
codebase's actual call graph. `trailmark` is genuinely distinct: it is
**proactive and codebase-wide** — a real call-graph / attack-surface /
blast-radius index that can be queried *before* a bug is found, to answer
"what actually calls this function" or "what is reachable from this
entrypoint" with a structural answer instead of a grep guess. This skill's
primary target is FF's own `tools/supervisor/` and `tools/governance/` —
the same high-privilege autonomous-execution codebase named as the gap in
`audit-context-building`'s Purpose section, here mapped structurally rather
than function-by-function.

## Why `risk_level: MEDIUM`, not `LOW` or `HIGH` (reconciled explicitly)

Installing a new third-party PyPI package is a real, if narrow,
supply-chain-adjacent action — hence not `LOW` like the pure prompt-spec
reviewers. But per this plan's own §7.1 reconciliation (item 4,
`plans/.claude/yes-my-earlier-answer-humming-waffle.md`): *"installing a new
dev/security tool (`uv pip install trailmark`) does not hit any of the three
named `TRUE_EXTERNAL_GATE`s (it is not a git push, not Gate 11, not package
publication) and is routine agent-executable dependency-addition. Reclassified
MEDIUM, no human needed."* This skill therefore proceeds on `Supervisor
approval` alone, not a per-instance human stop.

## One-Time Setup (verbatim-adapted, with an FF-specific fallback)

1. Check whether `uv` is available: `uv --version`.
2. **If `uv` is available:** `uv pip install trailmark`. Confirm via
   `uv run trailmark --version` (or `python -c "import trailmark"`).
3. **If `uv` is not available** (FF-specific fallback, not in upstream):
   `.venv/Scripts/pip install trailmark` (Windows) or
   `.venv/bin/pip install trailmark` (POSIX). Confirm via
   `python -c "import trailmark"`. Record this deviation explicitly in
   evidence — it is a documented fallback, not a silent substitution.
4. **Upstream's own rule, preserved verbatim:** "If `uv run trailmark` fails,
   install: `uv pip install trailmark`. DO NOT fall back to manual
   analysis." — i.e., a failed invocation is a signal to (re-)install the
   package, not a license to abandon the structural query in favor of ad hoc
   grepping.
5. This is a **one-time** setup step per environment — subsequent invocations
   skip straight to the Query Workflow below once `import trailmark` (or
   `uv run trailmark --version`) succeeds.

## Query Workflow

1. **Build the graph** — `trailmark.query.api.QueryEngine.from_directory(<target dir>)`,
   scoped to `tools/supervisor/` and/or `tools/governance/` for this
   repository's specific gap (see Purpose above).
2. **Run the query** relevant to the question being asked:
   - `.callers_of(<symbol>)` — what calls this function/method.
   - `.callees_of(<symbol>)` — what this function/method calls.
   - `.paths_between(<a>, <b>)` — is there a call path from `a` to `b`, and
     what is it (the structural blast-radius question).
   - `.complexity_hotspots()` — which functions/modules are
     complexity-concentrated (candidates for careful review).
   - `.attack_surface()` — enumerate reachable entry points.
   - `.preanalysis()` — a preliminary structural summary before a deeper,
     targeted query.
3. **Record the result** — the query, its parameters, and its structural
   output (caller/callee list, path, hotspot ranking, entry-point list) —
   inline in the invoking taskcard's evidence.
4. **Never propose a fix or assign severity from this skill directly** — a
   structural finding (e.g. an unexpectedly large blast radius from a
   `tools/governance/` entrypoint) is routed to `/found-issue-ownership` or
   to `sharp-edges` / `agent-owasp-compliance` / `audit-context-building` for
   disposition, matching this skill's Trail-of-Bits siblings' own
   analysis-only posture.

## Allowed Paths

- Bash — **narrowly**, for exactly two action classes:
  1. The one-time setup commands above (`uv --version`,
     `uv pip install trailmark` / `.venv/Scripts/pip install trailmark`,
     `uv run trailmark --version` / `python -c "import trailmark"`).
  2. Invoking the installed `trailmark` package's query API
     (`trailmark.query.api.QueryEngine` and its query methods) against a
     read-only target directory tree — this never mutates the target.
- Read, Grep, Glob — `tools/supervisor/**`, `tools/governance/**` (primary
  query target, read only)
- `.local/evidences/**`, `reports/` — query-result evidence output (write)

## Forbidden Paths

- **No mutation of the query target.** `tools/supervisor/**` and
  `tools/governance/**` are read by the graph-building step; this skill never
  writes to them.
- `src/**` (outside the one-time package install into the environment) —
  never mutated by this skill's query workflow.
- `pyproject.toml` — **intentionally not touched.** `trailmark` is an ad hoc
  analysis-tool install into the current environment, not a declared runtime
  or dev dependency of any shipped FF package (unlike `hypothesis`, which
  `property-based-testing.md` adds to `[project.optional-dependencies].dev`
  because Hypothesis-authored tests ship in `tests/**`). No test or product
  code depends on `trailmark` being importable, so it is not declared as a
  project dependency.
- `.supervisor/skill-registry.yaml`, `.supervisor/policies.yaml`,
  `registry/found-issue-register.yaml` — never written directly; findings
  route through `/found-issue-ownership`.
- Any `git push`, Gate 11 action, or package-publication credential use —
  none of this skill's steps touch a named `TRUE_EXTERNAL_GATE`.

## Constraints

- The one-time install is the only step with an external network effect (a
  PyPI package fetch); every subsequent query is a local, read-only
  structural analysis with no network call.
- No fix proposal, PoC generation, or severity assignment — this skill
  produces structural facts (caller/callee graphs, paths, hotspots, attack
  surface), not a disposition.
- If the install fails for a reason other than `uv` being absent (e.g.
  network unavailable, package removed from PyPI), do not silently fall back
  to manual grep-based analysis — record the failure honestly and treat it
  as a blocked query, per upstream's own "DO NOT fall back to manual
  analysis" rule.

## Idempotency Contract

Given an unchanged target source tree and the same query (same method, same
arguments), `trailmark`'s query API returns the same structural result — no
randomness. The one-time install step is idempotent: re-running
`uv pip install trailmark` (or the pip fallback) against an
already-satisfied environment is a no-op.

## Governance Note

Per TC-EXT-012 (external-skill-import plan) and TC-EXT-025 (this import),
this skill was cleared by `/skill-scanner` before registration. Its
CC-BY-SA-4.0 share-alike attribution is recorded above in both prose and an
HTML comment, per TC-EXT-001-02's precedent. Its `risk_level: MEDIUM` and
`gate-required: "Supervisor approval"` reflect the one-time external package
install reconciled against CLAUDE.md's Supreme Directive per this plan's
§7.1 item 4 — the install does not hit any named `TRUE_EXTERNAL_GATE` and
is routine agent-executable dependency-addition, requiring Supervisor
approval rather than a per-instance human stop.
