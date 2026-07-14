---
version: "1.0"
last-updated: "2026-07-14"
phase-available: "all"
gate-required: "Supervisor approval + SCM-POLICY-CHECK-001 (see 'SCM-POLICY-CHECK-001 Precondition' below) — gates ONLY Steps 5-8 (create release branch, write CHANGELOG.md, commit+push the branch, open the PR via `gh pr create`); Steps 1-4 are read-only recon and require no additional gate beyond ordinary Supervisor review; Step 9 (tag + actual publish) is never executed by this skill at all, gated or otherwise"
activation_gate: "SCM Agent policy authorization (CLAUDE.md's existing push doctrine) — see plan §7.1 item 2"
skill_type: ATOMIC_SKILL
idempotency: "Same repo state at HEAD + same PREV_TAG produce the same code-diff/commit-log analysis, the same reconciled SemVer recommendation, and the same drafted CHANGELOG.md entry; the branch-create/commit/push/gh pr create calls are the only steps with an external side effect and are gated by SCM-POLICY-CHECK-001 plus the upstream skill's own Step 4/Step 6 user-confirmation checkpoints, rather than executed unconditionally"
loc_budget: "0 lines of executable code (prompt-driven 9-step workflow + SemVer precedence table + error-handling table only; no bundled script)"
test_path: "N/A (prompt-spec skill, no executable code) — verification is the manual scan proof recorded under TC-EXT-028-03"
external_skill_origin: true
external_skill_source: github/awesome-copilot
external_skill_commit: e353a8cfb8124d44905fc73214d873cea4a0ba3b
external_skill_license: MIT
risk_level: HIGH
created-by: TC-EXT-028-01
product_track: infrastructure
---

# /github-release

Prepare a release packet for a per-format Format Factory package: determine
the next SemVer version from real evidence (code diff, reconciled against
commit log), draft a `CHANGELOG.md` entry, and open a PR carrying a release
branch — stopping short of ever cutting the actual tag or publishing the
package. This is the **fourth** `risk_level: HIGH` skill in the
`SCM-POLICY-CHECK-001` family (after `/receiving-code-review` TC-EXT-016,
`/gh-address-comments` TC-EXT-021, and the dependabot config-authoring skill
TC-EXT-027) and the only one of the four whose gated action is a **direct
`git push`** — the exact, pre-existing, named `TRUE_EXTERNAL_GATE` in
CLAUDE.md's Supreme Directive, not a new exception this skill invents.

## Requires

`gh` CLI (authenticated) and `git`. Both are assumed present in the executing
environment; their absence is a named error condition (see Error Handling
table below), not a silent failure.

## Attribution

This skill adapts the 9-step release workflow — read-only recon (Steps 1-4),
the code-diff-primary/commit-log-secondary reconciliation rule with its
`gh tag`-not-`gh release list` rationale, the SemVer precedence table, the
gated mutation sequence (Steps 5-8), the mandatory `--body-file` rule for
`gh pr create`, the explicit Step 9 manual hand-off, and the error-handling
table — from `github/awesome-copilot`'s `github-release` skill (MIT), commit
`e353a8cfb8124d44905fc73214d873cea4a0ba3b`. These sections are carried over
verbatim-adapted from the upstream skill (fetched directly from
`github/awesome-copilot` at that commit for this import). The FF-specific
`PUBLIC_PATH` re-scoping (per-format path required, no repo-root default —
see "FF Adaptation: PUBLIC_PATH" below), the SCM-POLICY-CHECK-001 gate around
Steps 5-8, and the explicit Forbidden Paths boundary at Step 9 are original
to this repository. License: MIT — attribution preserved per license terms;
no upstream code is executed, only its documented workflow is adapted into
prose. Cleared by `/skill-scanner` per TC-EXT-012's mandatory gating rule
(TC-EXT-028-03).

## Purpose

Cutting a release correctly requires (a) an honest SemVer determination
grounded in what the code actually changed, not just what commit messages
claim, and (b) a hard boundary between "prepare the release packet" (an
agent-safe, evidence-gated activity) and "publish the release" (an
irreversible, credential-gated, human-owned activity). This skill owns
exactly the first half. It never creates a tag and never runs a package
publish command — that boundary is load-bearing, not incidental, and is
enforced by this file's own Forbidden Paths section below.

## When to Use

- A per-format FF package (`src/python/<format>/` or `src/net/<format>/`) has
  accumulated commits since its last version tag and a release packet is
  needed.
- Before running any manual `git tag` / publish command — this skill's
  output (version recommendation + CHANGELOG entry + open PR) is the input
  to that manual step, never a replacement for it.

## FF Adaptation: `PUBLIC_PATH`

Upstream's workflow implicitly scopes its diff/changelog analysis to a
single-package repository (default: repo root). Format Factory ships
multiple independent packages per "release" — each format has its own
Python package under `src/python/<format>/` and, where applicable, its own
.NET package under `src/net/<format>/` — so a repo-root-scoped diff would
blend unrelated formats' changes into one SemVer determination. This skill
therefore **requires** a `PUBLIC_PATH` argument naming exactly one such
directory; there is no bare repo-root default:

```
PUBLIC_PATH: src/python/<format>/   (or)   src/net/<format>/
```

Step 2 (tag discovery) and Step 3 (diff/commit-log analysis) below are both
scoped to this path. A version tag not specific to `PUBLIC_PATH` (e.g. a
repo-wide tag with no per-format tagging convention yet) is treated as
`EXTERNAL_BLOCKER: no_per_format_tag_convention` and reported rather than
guessed at — this skill does not invent a per-format tagging scheme on the
user's behalf.

## Steps (the real 9-step workflow, verbatim-adapted)

### Steps 1-4 — read-only recon (no additional gate beyond Supervisor review)

1. **Checkout + pull main.** `git checkout main && git pull` — establish a
   clean, up-to-date base before any analysis.
2. **Get the latest version tag.** `git tag --sort=-version:refname`, scoped
   to `PUBLIC_PATH`'s tagging convention — **not** `gh release list`. Upstream's
   own rationale, carried verbatim: repos can have tags without a
   corresponding GitHub Release object, so `gh release list` can miss the
   true latest version; reading tags directly is the authoritative source.
   The first matching tag in the sorted output is `PREV_TAG`.
3. **Analyze changes since `PREV_TAG`.** Two signals, in this precedence
   order when they conflict:
   - **Code diff (primary signal)** — `git diff PREV_TAG..HEAD -- PUBLIC_PATH`,
     excluding `tests/**`, `docs/**`, and lockfiles. This is what actually
     shipped.
   - **Commit log (secondary signal)** — `git log PREV_TAG..HEAD --oneline`
     for conventional-commit prefixes (`feat:`, `fix:`, `BREAKING CHANGE:`,
     etc.). This is what the author *claimed* changed.
   - **Reconciliation rule (verbatim example preserved):** when the two
     signals disagree, the code diff wins. Upstream's own example: a commit
     message reads `fix: typo`, but the actual diff removes a public method
     — the commit log says PATCH, the diff shows a breaking removal. The
     diff wins: this is classified **MAJOR**, not PATCH. Never trust a commit
     message's self-classification over the diff's actual content.
4. **Determine the next SemVer version.** Apply the precedence table below
   (highest-precedence match wins when multiple categories are present in
   the same change set), then **present the recommendation with its
   rationale and WAIT for user confirmation** before proceeding to Step 5.
   This is a hard checkpoint, not an advisory suggestion — see Stop
   Conditions.

   | Change category (from Step 3's reconciled analysis) | SemVer bump |
   |---|---|
   | Any breaking change (removed/renamed public API, changed public signature, removed public export) | **MAJOR** |
   | New export/public API added, no breaking change | **MINOR** |
   | Bugfix, performance improvement, security patch, docs-only, chore-only | **PATCH** |

   Precedence: MAJOR > MINOR > PATCH — the highest-precedence category
   present in the change set determines the bump, even if lower-precedence
   changes are also present in the same diff.

### Steps 5-8 — gated mutation (SCM-POLICY-CHECK-001 applies to this block)

5. **Create the release branch** (e.g. `release/vX.Y.Z`) from the confirmed
   base.
6. **Update `CHANGELOG.md`** in Keep a Changelog format (`## [X.Y.Z] -
   YYYY-MM-DD` section, `Added`/`Changed`/`Fixed`/`Removed` subsections
   populated from Step 3's reconciled analysis). **Get confirmation before
   writing** — upstream's own second hard checkpoint, preserved verbatim:
   the drafted entry is presented for confirmation before the file is
   touched, exactly as Step 4's version recommendation is confirmed before
   Step 5 begins.
7. **Commit and push the release branch.** Ordinary `git commit` +
   `git push` of the release branch (never `main` directly) — gated by
   SCM-POLICY-CHECK-001 below.
8. **Open a PR via `gh pr create --body-file`.** The PR body is **never**
   passed inline via `--body` — upstream's own rationale, preserved
   verbatim: inline multi-line/special-character content through `--body`
   is subject to shell-escaping failures; writing the body to a temp file
   and passing `--body-file` avoids that failure class entirely. The PR
   body is the CHANGELOG entry drafted in Step 6.

### Step 9 — explicit manual hand-off (never automated by this skill)

9. **Hand off tag + actual publish to the user.** This skill's output ends
   at the opened PR from Step 8. Creating the version tag (`git tag`) and
   running the actual package-publish command (`twine upload`,
   `dotnet nuget push`, `gh release create`, or equivalent) are explicitly
   left to the user — upstream's own design, not a restriction this
   repository added. See Forbidden Paths below: this is enforced, not
   merely documented.

## Error Handling (verbatim-adapted)

| Condition | Disposition |
|---|---|
| `gh auth` failure (not authenticated) | **Stop.** Do not proceed past Step 1; report the auth failure verbatim. |
| Dirty working tree (uncommitted changes present at Step 1) | **Warn + ask.** Do not silently stash or discard; ask whether to commit, stash, or abort. |
| No commits since `PREV_TAG` scoped to `PUBLIC_PATH` | **Nothing to release.** Report this plainly and stop — not an error, just no work to do. |
| Tag exists locally but not on the remote | **Warn + ask.** Ambiguous state (local-only tag could mean an unpushed prior release or a stale local artifact) — ask before treating either tag state as authoritative. |
| Push fails because the target branch is protected | **Report verbatim** the exact `git push` failure output and suggest checking branch protection rules — do not retry with an escalated-privilege workaround. |

## SCM-POLICY-CHECK-001 Precondition (gates Steps 5-8 ONLY)

This precondition applies **only** to Steps 5-8 — create branch, write
`CHANGELOG.md`, commit+push, open PR. It does not gate Steps 1-4
(read-only recon), and it can never be used to authorize Step 9 (tag +
publish), which this skill does not execute under any policy state — see
Forbidden Paths.

Quoted verbatim from the plan's §7.2
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

**Why this is not a new exception (plan §7.1 item 2, cited explicitly):**
this skill's gated action — `git push` in Step 7 — hits the named `git push`
`TRUE_EXTERNAL_GATE` in CLAUDE.md's Supreme Directive directly. That is not
a gap this skill papers over: the plan's §7.1 item 2 reconciliation
determined that this skill's *own upstream design* — Steps 1-4 read-only
recon, an explicit user-confirmation checkpoint before Step 5 (the version
number) and before Step 6 (the CHANGELOG content), and Step 9 explicitly
deferring the actual tag/publish to the user — **already matches** Format
Factory's own pre-existing model for this exact class of action: *"SCM
Agent executes when credentials + policy authorize; agent prepares the
release packet, human does the final publish"* (CLAUDE.md, Hard Stops
section; Human-Free Autonomy Doctrine, "Push tasks"). Importing this skill
therefore does not create a new exception to the Supreme Directive — it
imports a workflow whose shape was independently designed, upstream, to fit
the identical prepare/publish split FF already enforces. The one standing
precondition (a policy-state read, not a per-invocation human stop) is
applied here exactly as it is to the other three `SCM-POLICY-CHECK-001`
skills, per §7.2.

**Verification procedure before Step 7's `git push` (and Step 8's
`gh pr create`) executes:**
1. Read AGENTS.md §AG4 (AG4.1 Commit, AG4.2 Push) and CLAUDE.md's "SCM
   Agent" doctrine (Human-Free Autonomy Doctrine section) for the current
   standing policy text.
2. Confirm git credentials are available in the current shell environment
   (AG4.2) and branch protection does not require an external identity
   unavailable to the agent.
3. Confirm Step 4's version recommendation and Step 6's CHANGELOG content
   were both explicitly confirmed by the user (or the current session's
   Supreme-Directive-authorized policy) before this point — Steps 5-8 do
   not proceed on an unconfirmed version or unconfirmed changelog content
   regardless of SCM-POLICY-CHECK-001's own disposition.
4. If all checks pass: proceed with Steps 5-8, and record the policy
   citation (file + section) in the invoking taskcard's evidence.
5. If any check fails or is ambiguous: do not push, do not open the PR.
   Emit `EXTERNAL_BLOCKER: git_push_credentials_unavailable` (or the more
   specific branch-protection variant per AG4.2/AD7), record it, and
   continue with the next safe work item rather than blocking the session
   — the same disposition CLAUDE.md's Hard Stops section already specifies
   for this exact blocker class.

## Mandatory Validations

- `tag_discovery_uses_git_tag_not_gh_release_list` — Step 2 never
  substitutes `gh release list` for `git tag --sort=-version:refname`.
- `code_diff_wins_reconciliation_conflict` — when Step 3's code-diff and
  commit-log signals disagree, the version recommendation follows the
  diff's actual content, not the commit message's self-classification.
- `semver_precedence_correctly_applied` — Step 4's recommendation reflects
  the highest-precedence category present in the reconciled change set
  (MAJOR > MINOR > PATCH), not merely the most recent commit's category.
- `version_confirmed_before_step_5` — Step 4's recommendation is explicitly
  confirmed before any Step 5-8 action begins.
- `changelog_confirmed_before_write` — Step 6's drafted CHANGELOG.md entry
  is explicitly confirmed before the file is written.
- `body_file_used_not_inline_body` — Step 8's `gh pr create` call always
  uses `--body-file`; `--body` with inline content is never used.
- `push_gated_by_scm_policy_check_001` — Step 7's `git push` never executes
  without a recorded SCM-POLICY-CHECK-001 confirmation (or a recorded
  `EXTERNAL_BLOCKER` in its place).
- `tag_creation_never_executed_by_this_skill` — no invocation of this skill
  ever runs `git tag` (creation or push of a tag ref), under any policy
  state, confirmed or not.
- `publish_never_executed_by_this_skill` — no invocation of this skill ever
  runs a package-publish command (`twine upload`, `dotnet nuget push`,
  `gh release create`, `npm publish`, or equivalent), under any policy
  state, confirmed or not.

## Allowed Paths

- `PUBLIC_PATH` (`src/python/<format>/` or `src/net/<format>/`) — read only,
  for Step 3's diff analysis; never written by this skill
- `git tag --sort=-version:refname`, `git diff`, `git log`, `git status` —
  read-only git commands for Steps 1-4
- `CHANGELOG.md` — write, gated by the Step 6 confirmation checkpoint above
- A new `release/vX.Y.Z` branch — create, commit, and push, gated by
  SCM-POLICY-CHECK-001
- `gh pr create --body-file <tempfile>` — the one `gh` mutation this skill
  may execute, gated by SCM-POLICY-CHECK-001
- `.local/evidences/**`, `reports/` — cycle evidence output (write)

## Forbidden Paths

- `git tag` (any form — local creation or `git push --tags`/`git push
  origin <tag>`) — this skill never creates or pushes a tag under any
  circumstance; tagging is Step 9, explicitly left to the user
- Any package-publish command (`twine upload`, `dotnet nuget push`,
  `gh release create`, `npm publish`, or equivalent) — this skill never
  publishes a package under any circumstance; publication is Step 9,
  explicitly left to the user
- `src/**` beyond `PUBLIC_PATH` read access for Step 3 — this skill never
  edits product source; it only reads a diff already produced by prior,
  separately governed work
- `main` (or any protected branch) as a direct push target — Step 7 pushes
  only the release branch created in Step 5
- `gh pr create --body <inline text>` — the escaping-unsafe inline form;
  only `--body-file` is permitted (Step 8)
- `.supervisor/skill-registry.yaml`, `registry/format-registry.yaml` — this
  skill does not alter governance or gate authority
- `plans/master-plan.md`, `.local/supervisor/active-plan-lock.json` — never
  touched by a release-preparation cycle

## Stop Conditions

- Stop before Step 5 if Step 4's version recommendation has not been
  explicitly confirmed — do not treat silence or an unrelated user message
  as confirmation.
- Stop before writing `CHANGELOG.md` (Step 6) if the drafted entry has not
  been explicitly confirmed.
- Stop before Step 7's `git push` (and Step 8's `gh pr create`) if
  SCM-POLICY-CHECK-001 has not been confirmed for the current session —
  classify `EXTERNAL_BLOCKER: git_push_credentials_unavailable` (or the
  applicable AG4.2/AD7 variant) and continue with other safe work instead
  of blocking the session.
- Stop and report verbatim (do not retry with escalated privilege) on any
  Error Handling table condition above.
- Never proceed to Step 9 under any condition — tag creation and package
  publish are permanently out of this skill's execution scope, not merely
  gated.

## Idempotency Contract

Given the same repository state at HEAD and the same `PREV_TAG` (from Step
2's `git tag --sort=-version:refname` scoped to `PUBLIC_PATH`), re-running
Steps 1-4 produces the same reconciled code-diff/commit-log analysis and the
same SemVer recommendation. Steps 5-8 are executed at most once per release
cycle (a re-run after a PR is already open is a no-op recon confirming the
existing PR reflects the same analysis) and are gated by SCM-POLICY-CHECK-001
plus the Step 4/Step 6 user-confirmation checkpoints. Step 9 is never
executed by this skill, so it has no idempotency surface here at all.

## Output Format

```
## Release Packet: <PUBLIC_PATH>

### Steps 1-2 — Recon
- Base: main @ <HEAD sha, post-pull>
- PREV_TAG (git tag --sort=-version:refname, scoped to PUBLIC_PATH): <tag or NONE>

### Step 3 — Analyze Changes
- Code diff signal (primary): <summary of added/changed/removed public surface>
- Commit log signal (secondary): <conventional-commit prefixes seen>
- Reconciliation: <AGREE | CONFLICT — diff wins: <reason>>

### Step 4 — SemVer Determination
- Recommendation: <MAJOR | MINOR | PATCH> -> <X.Y.Z>
- Rationale: <precedence-table category matched>
- Confirmation: <CONFIRMED | WAITING>

### Steps 5-8 — Gated Mutation (SCM-POLICY-CHECK-001: confirmed | EXTERNAL_BLOCKER)
- Release branch: <release/vX.Y.Z | not created>
- CHANGELOG.md entry: <CONFIRMED and written | drafted, awaiting confirmation>
- Push: <done | EXTERNAL_BLOCKER: <reason>>
- PR: <URL, opened via --body-file | not opened>

### Step 9 — Hand-off
- Tag creation: NOT PERFORMED (user action required)
- Publish: NOT PERFORMED (user action required)
```

## Governance Note

Per TC-EXT-012 (external-skill-import plan), this skill was cleared by
`/skill-scanner` before registration (TC-EXT-028-03) — the mandatory gating
step for every external-skill import in TC-EXT-013 through TC-EXT-028. Its
`risk_level: HIGH` reflects the single real external side effect it can
execute (`git push` of a release branch, immediately followed by
`gh pr create --body-file`), gated behind the SCM-POLICY-CHECK-001
precondition (§7.2 of
`plans/.claude/yes-my-earlier-answer-humming-waffle.md`) and reconciled
against CLAUDE.md's Supreme Directive per §7.1 item 2 — this skill's own
upstream design (read-only recon first, two explicit confirmation
checkpoints, and Step 9's explicit manual hand-off) already matches FF's
pre-existing "agent prepares the release packet, human does the final
publish" model, so no new exception was created to import it.
