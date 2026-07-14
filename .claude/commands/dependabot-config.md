---
version: "1.0"
last-updated: "2026-07-14"
phase-available: "all"
gate-required: "Supervisor approval + SCM-POLICY-CHECK-001 (see 'SCM-POLICY-CHECK-001 Precondition' below) — gates ONLY the eventual act of writing/editing `.github/dependabot.yml` (or opening a PR that does so); drafting the ecosystem table, the config block, and the PR-comment-command reference requires no additional gate beyond ordinary Supervisor review"
skill_type: ATOMIC_SKILL
idempotency: "Same confirmed ecosystem set (pip, nuget, github-actions) + same upstream ecosystem-detection table produce the same drafted `.github/dependabot.yml` block; this skill file itself makes no network call and mutates no target — it is a config-authoring reference only"
loc_budget: "0 lines of executable code (prompt-driven config-authoring guide only; no bundled script)"
test_path: "N/A (prompt-spec skill, no executable code) — verification is the manual scan proof recorded under TC-EXT-027-03 and the confirmed-absence check that `.github/dependabot.yml` was not created by this import"
external_skill_origin: true
external_skill_source: github/awesome-copilot
external_skill_commit: e353a8cfb8124d44905fc73214d873cea4a0ba3b
external_skill_license: MIT
risk_level: MEDIUM
created-by: TC-EXT-027-01
product_track: governance
---

# /dependabot-config

Config-authoring guide for GitHub Dependabot (`.github/dependabot.yml`):
ecosystem detection, the minimal per-ecosystem config block, the
`directories`/`directory` distinction, grouping/labels/scheduling options,
and the PR-comment command surface. Format Factory has **zero
dependency-update automation today** — no `.github/dependabot.yml` exists in
this repository. This skill provides the authoring reference for that gap;
it does not, by itself, create or edit the config file (see "Scope of This
Import" below).

## Attribution

<!--
This skill's ecosystem-detection table, the `directories`(plural,glob)
vs `directory`(singular) distinction, the minimal-config-block shape, and
the PR-comment command reference are adapted from the `dependabot` skill in
`github/awesome-copilot`, commit
`e353a8cfb8124d44905fc73214d873cea4a0ba3b`. Licensed MIT. The upstream
table's ~23 recognized ecosystem values and its "prefer uv when uv.lock is
present, otherwise pip" / "pnpm and yarn both use the npm ecosystem value"
rules are carried over near-verbatim; the FF-specific confirmed-ecosystem
list (pip, nuget, github-actions — see below), the explicit
non-auto-apply scope boundary, and the SCM-POLICY-CHECK-001 gate wiring are
original to this repository.
-->

Adapted from the `dependabot` skill in `github/awesome-copilot` (MIT),
commit `e353a8cfb8124d44905fc73214d873cea4a0ba3b`. The ecosystem-detection
table and PR-comment-command reference are carried over near-verbatim from
upstream; the FF-specific confirmed ecosystem set, the explicit
non-auto-apply scope boundary (this import drafts and registers the skill
only — it never creates `.github/dependabot.yml`), and the
SCM-POLICY-CHECK-001 gate wiring are original to this repository. Cleared
by `/skill-scanner` per TC-EXT-012's mandatory gating rule (TC-EXT-027-03).

## Scope of This Import (TC-EXT-027) — read before anything else

This skill file is a **config-authoring reference**. Importing it
(TC-EXT-027) means drafting this guide and registering it — it does
**not** mean `.github/dependabot.yml` gets created or edited as a side
effect of the import. Actually creating or editing
`.github/dependabot.yml` in this repository is a **separate, deliberate,
later action** with its own review, its own taskcard, and its own
SCM-POLICY-CHECK-001 confirmation (see below) — never an automatic
consequence of this skill existing or being registered.

## Purpose

FF has no automated dependency-update mechanism for any of its confirmed
ecosystems (Python, .NET, GitHub Actions) — updates today are entirely
manual. This skill documents *how* a `.github/dependabot.yml` would be
authored correctly for this repository's real dependency surface, so that
the eventual (separate) decision to enable Dependabot starts from a
correct, FF-specific config draft rather than a generic template.

## FF's Real Confirmed Ecosystems (verified this session, not assumed)

| Ecosystem value | Evidence in this repo | Notes |
|---|---|---|
| `pip` | `pyproject.toml` (`[project.optional-dependencies].dev`: pytest, ruff, bandit, hypothesis, lxml, zstandard, etc.); **no `uv.lock` found anywhere in the repository** | Upstream's own rule is "prefer `uv` when `uv.lock` is present, otherwise `pip`" — FF has no `uv.lock`, so the correct value is `pip`, not `uv`. Do not default to `uv` without re-checking for `uv.lock` first. |
| `nuget` | `src/net/**/*.csproj` (e.g. `src/net/csv/FormatFactory.Csv.csproj`, `src/net/fods/FormatFactory.Fods.csproj`, `src/net/fodt/...`, `src/net/html/...`, `src/net/markdown/...` — `Microsoft.NET.Sdk` projects) | Each `src/net/<format>/` directory is its own project; a real config needs one `directories`-style entry (or one `directory` entry per project, or a shared glob) — see below. |
| `github-actions` | `.github/workflows/ci.yml`, `.github/workflows/release-dotnet.yml`, `.github/workflows/release-python.yml` (pinned actions: `actions/checkout@v4`, `actions/setup-python@v5`, `actions/setup-dotnet@v4`, `actions/upload-artifact@v4`) | Ecosystem root directory is always `/` (workflow files are discovered automatically; there is no separate "workflow location" to point at). |

`dotnet-sdk` (a distinct ecosystem value in the upstream table, for the
`global.json`-pinned SDK version rather than NuGet packages) does **not**
apply — this repository has no `global.json`. `gomod`, `cargo`, `maven`,
`gradle`, `docker` do not apply — no `go.mod`/`Cargo.toml`/`pom.xml`/
`build.gradle`/`Dockerfile` exists in this repository as of this session.
Re-verify this table if any of those files are introduced later; do not
carry these three ecosystems forward without re-checking.

## Ecosystem-Detection Table (upstream reference, general form)

Adapted near-verbatim from `github/awesome-copilot`'s `dependabot` skill —
this is the general detection logic; the row above is FF's own confirmed
subset applied to it.

| Signal file(s) present | `package-ecosystem` value | Note |
|---|---|---|
| `uv.lock` | `uv` | Prefer `uv` over `pip` whenever `uv.lock` exists |
| `requirements.txt` / `pyproject.toml` (no `uv.lock`) | `pip` | FF's actual case — no `uv.lock` present |
| `package.json` + `package-lock.json` | `npm` | |
| `package.json` + `pnpm-lock.yaml` | `npm` | **pnpm uses the `npm` ecosystem value** — there is no separate `pnpm` value |
| `package.json` + `yarn.lock` | `npm` | **yarn also uses the `npm` ecosystem value** — same rule |
| `.github/workflows/*.yml` (any) | `github-actions` | FF's actual case |
| `*.csproj` / `*.sln` / `packages.config` | `nuget` | FF's actual case |
| `global.json` | `dotnet-sdk` | Does not apply to FF (no `global.json`) |
| `go.mod` | `gomod` | Does not apply to FF |
| `Cargo.toml` | `cargo` | Does not apply to FF |
| `pom.xml` | `maven` | Does not apply to FF |
| `build.gradle` / `build.gradle.kts` | `gradle` | Does not apply to FF |
| `Dockerfile` | `docker` | Does not apply to FF |
| (~23 recognized values total upstream; only the rows above are FF-relevant today) | | |

## `directories` (plural, glob) vs `directory` (singular)

- `directory: "/src/net/csv"` — a single, exact path. Use when exactly one
  project/manifest location needs updates for an ecosystem.
- `directories: ["/src/net/*"]` — a glob covering multiple sibling project
  directories in one entry. **This is the correct shape for FF's `nuget`
  ecosystem** — `src/net/csv/`, `src/net/fods/`, `src/net/fodt/`,
  `src/net/html/`, `src/net/markdown/`, and any other `src/net/<format>/`
  project directory, all in a single `directories` glob entry rather than
  one `directory` entry per format (which would require editing the config
  every time a new `.NET` format project is added).
- `pip` and `github-actions` in FF's case each have a single natural root
  (`/` for the umbrella `pyproject.toml`; `/` for `.github/workflows/`), so
  `directory: "/"` is sufficient for those two ecosystems — `directories`
  is not needed there.

## Minimal Config Block Per Confirmed Ecosystem (draft reference only)

This is what a correct, minimal `updates:` entry looks like for each of
FF's three confirmed ecosystems. **This is a drafted reference block for
future use — it is not written to any file by this skill or by TC-EXT-027.**

```yaml
# Reference draft only — NOT applied to .github/dependabot.yml by this skill.
version: 2
updates:
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"
  - package-ecosystem: "nuget"
    directories:
      - "/src/net/*"
    schedule:
      interval: "weekly"
  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "weekly"
```

## Grouping / Labels / Scheduling Options (reference)

- **Grouping**: a `groups:` block under an ecosystem entry can combine
  multiple dependency updates into a single PR (e.g. group all
  `actions/*` updates together, or all patch-level NuGet bumps together) —
  reduces PR volume at the cost of a coarser-grained review unit.
- **Labels**: `labels: ["dependencies", "<ecosystem>"]` — attaches labels
  to generated PRs for triage; FF would map this to its own existing label
  taxonomy if and when this is actually applied.
- **Scheduling**: `schedule.interval` (`daily` / `weekly` / `monthly`),
  optionally `schedule.day` and `schedule.time` with a `timezone` — weekly
  is the conservative default for a repository without existing
  dependency-update automation, to avoid a sudden high-volume PR influx on
  first enablement.
- **`open-pull-requests-limit`**: caps concurrent open Dependabot PRs per
  ecosystem entry — worth setting explicitly on first enablement rather
  than relying on the (much higher) default, again to avoid PR-volume
  shock.

## PR-Comment Commands (verbatim reference, with the 2026-01 deprecation noted)

| Command | Effect |
|---|---|
| `@dependabot rebase` | Rebase the PR against the target branch |
| `@dependabot recreate` | Recreate the PR from scratch (discard manual edits to the PR branch) |
| `@dependabot ignore this dependency` | Stop future updates for this dependency across all ecosystems |
| `@dependabot ignore this major/minor version` | Stop future updates for this specific major/minor version line only |

**`@dependabot merge`, `@dependabot close`, and `@dependabot reopen` are
deprecated as of January 2026** — use `gh pr merge`, `gh pr close`, and
`gh pr reopen` instead. Do not document or rely on the deprecated
merge/close/reopen comment commands in any future FF automation built on
top of this reference; route those actions through `gh pr` directly, same
as this plan's other `gh`-based skills (`gh-fix-ci`, `gh-address-comments`).

## AI-Agent Integration (reference only, read-only surface)

- **GitHub MCP Server's `dependabot` toolset** — queries the GitHub
  Advisory Database for known vulnerabilities. This is a **read-only
  lookup**, not a mutation; per this plan's §7.1 reconciliation, read-only
  Advisory-Database queries are part of why this skill's `risk_level` is
  reclassified `MEDIUM` rather than `HIGH` (the CI-config *edit* is the
  only mutating action, and it is separately gated below — the Advisory
  Database query itself never writes anything).
- **Dependabot CLI** — can diff a repository's dependency graph locally
  (what would change if Dependabot ran) without opening any PR or writing
  any file. Also read-only.
- Neither integration is wired into any FF tool as of this import — this
  section documents the reference surface for a future, separately
  reviewed integration, not a current FF capability.

## SCM-POLICY-CHECK-001 Precondition (gates only the eventual write to `.github/dependabot.yml`)

This precondition applies **only** to the eventual, separate action of
actually creating/editing `.github/dependabot.yml` (or opening a PR that
does so) — it does not gate anything in this skill file itself, since this
skill performs no write of its own. Quoted verbatim from the plan's §7.2
(`plans/.claude/yes-my-earlier-answer-humming-waffle.md`):

```yaml
precondition_id: SCM-POLICY-CHECK-001
statement: >
  Before TC-EXT-016, TC-EXT-021, TC-EXT-027, or TC-EXT-028 post any PR comment, edit
  .github/dependabot.yml, push a branch, or open a PR, the executing agent must confirm
  that Format Factory's existing SCM Agent sprint/user policy (AGENTS.md §AG4, CLAUDE.md
  Human-Free Autonomy Doctrine) currently authorizes these action classes. This is a
  policy-state read, not a request for a human to approve this specific plan or taskcard.
if_policy_already_authorizes: proceed autonomously, no further human involvement at any stage
if_policy_does_not_yet_authorize: classify as EXTERNAL_BLOCKER (per CLAUDE.md's existing
  named pattern, e.g. EXTERNAL_BLOCKER: git_push_credentials_unavailable) rather than
  silently stopping or silently proceeding — this is Format Factory's own existing
  classification discipline, not a new gate invented by this plan.
```

**Applied to this skill specifically:** before any future, separate task
actually writes `.github/dependabot.yml` using the draft blocks above:

1. Read AGENTS.md §AG4 and CLAUDE.md's "SCM Agent" doctrine for the
   current standing policy text.
2. Confirm no narrower policy override restricts CI-config edits
   specifically beyond the general commit/push policy.
3. If both checks pass: proceed with the write, record the policy
   citation in the invoking taskcard's evidence.
4. If either check fails or is ambiguous: do not write the file. Emit
   `EXTERNAL_BLOCKER: dependabot_config_write_not_authorized`, record it,
   and continue with the next safe work item.

**Why a policy-state check rather than a per-invocation human stop:**
identical reasoning to `/receiving-code-review` and `/gh-address-comments`
— AGENTS.md §AG4 governs commit/push as SCM Agent action classes; the
plan's §7.1 reconciliation extends that same shape of policy-based
authorization to this CI-config edit rather than inventing a new
per-instance gate. CI-config edits are within the Supreme-Directive
SCM-Agent authority (§7.1 item 1) — not a fresh per-instance human gate.

## Allowed Paths

- Read — `pyproject.toml`, `src/net/**/*.csproj`, `.github/workflows/*.yml`
  (ecosystem-detection recon, as performed for this import)
- `.local/evidences/**`, `reports/` — reference-draft evidence output
  (write)
- This skill itself never writes `.github/dependabot.yml` — see Forbidden
  Paths below. A write to that path belongs exclusively to a future,
  separate, SCM-POLICY-CHECK-001-gated taskcard, which would carry its own
  Allowed Paths grant at that time; it is not part of this skill's own
  permission surface.

## Forbidden Paths

- `.github/dependabot.yml` — **never written by this skill, under any
  invocation.** Not created or edited by TC-EXT-027 or by merely having
  this skill file exist/registered. Confirmed absent before and after this
  import. A future, separate, SCM-POLICY-CHECK-001-gated taskcard would
  need its own explicit Allowed Paths grant to write this file — this
  skill file's own permission surface never includes it.
- `src/**` — this skill never touches product source
- `.supervisor/skill-registry.yaml`, `registry/format-registry.yaml` —
  this skill does not alter governance or gate authority beyond its own
  registration entry
- Any `gh api` PR-comment-posting call — out of scope for this skill;
  routed through `/receiving-code-review` or `/gh-address-comments`
  instead

## Stop Conditions

- Stop before drafting an ecosystem row for any ecosystem not evidenced by
  an actual file in this repository (no speculative ecosystem entries).
- Stop before treating `uv` as FF's Python ecosystem value unless a
  `uv.lock` is found in the repository at the time of the check — re-run
  the `uv.lock` search rather than reusing a stale prior finding.
- Stop before any write to `.github/dependabot.yml` until
  SCM-POLICY-CHECK-001 is confirmed for the current session — classify
  `EXTERNAL_BLOCKER: dependabot_config_write_not_authorized` and continue
  with other safe work instead of blocking the session.
- Per this plan's §7.1 reconciliation: the CI-config edit this skill
  documents is within Supreme-Directive SCM-Agent authority (item 1), and
  the Advisory-Database queries this skill references are read-only
  lookups (not mutations) — this is why `risk_level: MEDIUM` applies
  rather than the upstream-implied `HIGH`, and why Supervisor approval
  plus the one-time policy check is sufficient, not a per-instance human
  stop.

## Idempotency Contract

Given the same confirmed ecosystem set (pip, nuget, github-actions) and
the same upstream ecosystem-detection table, re-running this skill's
drafting workflow produces the same config-block draft. This skill file
makes no network call and performs no write of its own — the only
non-idempotent, externally-visible action it documents (the eventual
`.github/dependabot.yml` write) belongs to a separate, later, gated task,
not to this import.

## Output Format

```
## Dependabot Config Draft: <repository>

### Confirmed Ecosystems
- <ecosystem>: <evidence file(s)>

### Drafted updates: block
<yaml block, per ecosystem above>

### Grouping/labels/scheduling chosen (if any)
- <ecosystem>: <groups / labels / schedule.interval chosen, with rationale>

### Applied to .github/dependabot.yml?
NO — this is a reference draft only (per TC-EXT-027 scope boundary).
Applying it is a separate, deliberate action gated by SCM-POLICY-CHECK-001.
```

## Governance Note

Imported under TC-EXT-027 of the external-skill-adoption plan
(`plans/.claude/yes-my-earlier-answer-humming-waffle.md` §7.3), adapted
from `github/awesome-copilot`'s `dependabot` skill (MIT), commit
`e353a8cfb8124d44905fc73214d873cea4a0ba3b`. Cleared by `/skill-scanner`
before registration (TC-EXT-027-03). Its `risk_level: MEDIUM` reflects
this plan's §7.1 reconciliation: the CI-config edit this skill documents
is within Supreme-Directive SCM-Agent authority (not a fresh per-instance
human gate), and the Advisory-Database queries it references are
read-only lookups — reclassified `MEDIUM`, not `HIGH`. This import itself
(TC-EXT-027) drafts and registers the skill only; `.github/dependabot.yml`
was not created or modified as part of this taskcard, and its actual
creation remains a separate, deliberate, later action requiring its own
review.
