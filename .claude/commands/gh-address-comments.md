---
version: "1.0"
last-updated: "2026-07-14"
phase-available: "all"
gate-required: "Supervisor approval + SCM-POLICY-CHECK-001 (see 'SCM-POLICY-CHECK-001 Precondition' below) — gates ONLY the `gh api .../replies` network call in Step 6 POST; classification, verification, and drafting require no additional gate beyond ordinary Supervisor review"
skill_type: ATOMIC_SKILL
idempotency: "Same PR comment thread content + same 4-category classification model produce the same per-comment classification and the same drafted response text; the `gh api .../replies` call is the only step with an external side effect and is gated by SCM-POLICY-CHECK-001 rather than executed unconditionally"
loc_budget: "0 lines of executable code (prompt-driven classification model + checklist only; no bundled script)"
test_path: "N/A (prompt-spec skill, no executable code) — verification is the manual scan proof recorded under TC-EXT-021-03"
product_track: infrastructure
created-by: TC-EXT-021
risk_level: HIGH
---

# /gh-address-comments

Classify and respond to PR review comments before implementing or replying
to any of them. Every comment is sorted into exactly one of four categories
(code-change / question-explanation / style-nit / governance-concern), each
with its own routing rule, before any `gh api` reply is posted. This is the
**second `risk_level: HIGH`** skill in the TC-EXT-0XX external/FF-original
skill family (after `/receiving-code-review`, TC-EXT-016) — it shares the
identical external-visible-action profile: a real network call that posts
content to GitHub on the repository's behalf
(`gh api repos/{owner}/{repo}/pulls/{pr}/comments/{id}/replies`).

## Origin

FF-original skill — no upstream project was verified during this session's
external-skill-adoption research to cite as a source (see
`plans/.claude/yes-my-earlier-answer-humming-waffle.md` §7.3, TC-EXT-021:
"Build gh-address-comments (FF-original)"). There is no upstream commit or
license to cite, and this file carries no `external_skill_*` provenance
fields. Its Response-Pattern shape (READ → CLASSIFY → VERIFY → RESPOND →
IMPLEMENT → POST) is modeled on this repository's own `/receiving-code-review`
(TC-EXT-016, itself adapted from `obra/superpowers`, MIT) rather than on any
new external source — that modeling is an internal design choice, not an
import.

## Purpose

Addressing PR review comments end-to-end — reading them, deciding what kind
of comment each one is, drafting a response, implementing any required code
change, and posting the reply — is a single workflow with two very different
risk profiles inside it: drafting/classifying is ordinary prompt work, while
posting the reply is an external, third-party-visible network call. This
skill keeps those two halves explicit so that the classification and
drafting work always happens before the gated posting call, never blended
into one undifferentiated "respond to PR" action.

## When to Use

- A PR has open review comments that need a response, a fix, or both.
- Before posting any reply to a GitHub PR comment thread via `gh api` —
  this skill's classification step is mandatory first, even for comments
  that look trivial (a "trivial" comment misclassified as style-nit when it
  is actually a governance-concern is exactly the failure mode this skill
  prevents).

## Comment Classification Model (4 categories)

| Category | Definition | Routing |
|---|---|---|
| `code-change` | Comment requests a concrete change to behavior, a bug fix, a missing test, or a refactor | Run `/receiving-code-review`'s 5-point External Reviewer checklist + YAGNI grep (Step 3 VERIFY below); if the comment is specifically about a **failing CI job**, run `/gh-fix-ci` (TC-EXT-020) first to get a real diagnosis before drafting the fix; any resulting `src/**` change is delegated to the applicable governed mutation skill (`/product-source-task`, `/add-python-api`, `/add-dotnet-api`, etc., per EP-3) — this skill never edits `src/**` directly |
| `question-explanation` | Comment asks "why" or "what does this do" without requesting a change | Draft a technical explanation in the reply; no code change, no delegation |
| `style-nit` | Comment suggests a minor stylistic change (naming, formatting, comment wording, docstring phrasing) with no behavior impact | If scoped to `tests/**`/comments/docs only, may be applied directly; if it touches `src/**`, it is still routed through a governed mutation skill per EP-3 — "nit" does not exempt a change from the governed-mutation rule |
| `governance-concern` | Comment raises a concern about process, architecture, an existing validator, or a policy gap — it may or may not reveal a real defect | Investigate per `/systematic-debugging`'s Phase 1-2; if it reveals a genuine defect, route to `/found-issue-ownership` (Step 1 Trigger Conditions → Step 3 Root Cause → an `FI-NNN` record); if it is a process preference or already-settled architectural decision, respond with technical reasoning citing the existing decision and take no further action |

## Steps (READ → CLASSIFY → VERIFY → RESPOND → IMPLEMENT → POST)

1. **READ**: read the full PR comment thread content — every comment in the
   batch, completely, before reacting to any single one (same discipline as
   `/receiving-code-review` Step 1).
2. **CLASSIFY**: assign exactly one of the 4 categories above to each
   comment. A comment that seems to span two categories (e.g. a question
   that also implies a code change) is classified by its primary ask; note
   the secondary aspect in the drafted response rather than opening a second
   classification.
3. **VERIFY** (per comment, category-specific):
   - `code-change`: apply `/receiving-code-review`'s 5-point External
     Reviewer checklist (technically correct for this codebase? breaks
     existing functionality? reason for current implementation? works on
     all platforms/versions? does the commenter have full context?) and the
     YAGNI grep ("implement properly" → grep for actual usage first).
   - `question-explanation`: verify the explanation being drafted is
     factually accurate against the current codebase state (not
     stale/aspirational).
   - `style-nit`: confirm the suggested change has no behavior impact before
     treating it as a nit (a "nit" that turns out to affect behavior is
     reclassified as `code-change`).
   - `governance-concern`: run `/systematic-debugging` Phase 1-2 (Root Cause
     Investigation, Pattern Analysis) far enough to determine whether a real
     defect exists, before deciding whether `/found-issue-ownership` applies.
4. **RESPOND**: draft the reply text per comment — technical acknowledgment,
   reasoned pushback, explanation, or a defect confirmation with its
   `FI-NNN` reference. Same "actions over words, no performative agreement"
   discipline as `/receiving-code-review`.
5. **IMPLEMENT** (category-specific, before POST): `code-change` and
   `src/**`-touching `style-nit` comments are implemented by delegating to
   the applicable governed mutation skill per EP-3 (never a direct `src/**`
   edit from this skill); `code-change` comments specifically about a CI
   failure are diagnosed via `/gh-fix-ci` first. `question-explanation` and
   non-`src/**` `style-nit` comments need no implementation step — the
   drafted reply itself is the deliverable. `governance-concern` comments
   with a confirmed defect are implemented via whatever taskcard
   `/found-issue-ownership` produces, not directly here.
6. **POST**: post the reply via
   `gh api repos/{owner}/{repo}/pulls/{pr}/comments/{id}/replies`, gated by
   the SCM-POLICY-CHECK-001 precondition below. One reply per addressed
   comment thread; do not batch multiple distinct comments' responses into
   a single reply.

## SCM-POLICY-CHECK-001 Precondition (gates the `gh api .../replies` call ONLY)

This precondition applies **only** to Step 6 POST — the concrete action
`gh api repos/{owner}/{repo}/pulls/{pr}/comments/{id}/replies`. It does not
gate READ/CLASSIFY/VERIFY/RESPOND/IMPLEMENT, and it does not gate any
IMPLEMENT action that is a local file edit rather than a network call. This
is the identical gate `/receiving-code-review` (TC-EXT-016) applies to its
own Step 6 IMPLEMENT network call — same precondition, same wording, applied
here to this skill's own posting step.

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

**Applied to this skill specifically:** before this skill's Step 6 POST
executes `gh api repos/{owner}/{repo}/pulls/{pr}/comments/{id}/replies`:

1. Read AGENTS.md §AG4 and CLAUDE.md's "SCM Agent" doctrine (Human-Free
   Autonomy Doctrine section) for the current standing policy text.
2. Confirm no narrower policy override exists for `gh api` PR-comment
   posting specifically (a gap-ledger entry or plan amendment restricting
   it beyond the general commit/push policy).
3. If both checks pass: proceed with the call, and record the policy
   citation (file + section) in the invoking taskcard's evidence.
4. If either check fails or is ambiguous: do not call `gh api`. Emit
   `EXTERNAL_BLOCKER: gh_pr_comment_reply_not_authorized`, record it, and
   continue with the next safe work item rather than blocking the session —
   the same disposition `/receiving-code-review` uses for the identical gap.

**Why a policy-state check rather than a per-invocation human stop:** same
reasoning as `/receiving-code-review`'s own precondition section — AGENTS.md
§AG4 governs commit/push as SCM Agent action classes; the plan's §7.1
reconciliation extends that same shape of policy-based authorization to
`gh api` PR-comment-reply posting rather than inventing a new per-instance
gate.

## Mandatory Validations

- `comment_read_completely_before_classification` — Step 1 (READ) completed
  for the entire comment batch before any comment in it is classified.
- `every_comment_classified` — every comment in the batch has exactly one
  of the 4 categories assigned before Step 4 (RESPOND) begins for any of
  them.
- `code_change_checklist_applied` — the 5-point External Reviewer checklist
  and YAGNI grep are recorded for every `code-change`-classified comment.
- `ci_failure_comments_diagnosed_via_gh_fix_ci` — any `code-change` comment
  that concerns a failing CI job is diagnosed via `/gh-fix-ci` (TC-EXT-020)
  before a fix is drafted, rather than guessed at directly.
- `governance_concern_checked_for_real_defect` — every
  `governance-concern`-classified comment runs `/systematic-debugging`
  Phase 1-2 far enough to determine defect-or-not before disposition.
- `gh_api_reply_gated_by_scm_policy_check_001` — the `gh api .../replies`
  call never executes without a recorded SCM-POLICY-CHECK-001 confirmation
  (or a recorded `EXTERNAL_BLOCKER: gh_pr_comment_reply_not_authorized` in
  its place).
- `no_direct_src_mutation_outside_governed_skill` — any Step 5 IMPLEMENT
  action touching `src/**` is executed by invoking the applicable
  already-governed mutation skill per EP-3; this skill creates no direct
  product-source mutation pathway of its own.

## Allowed Paths

- The PR comment thread content itself — read
- `tests/**` — write directly for a Step 5 fix that is test-only
- Any source/spec/documentation file relevant to a comment — read only, for
  Step 3 VERIFY
- `gh api repos/{owner}/{repo}/pulls/{pr}/comments/{id}/replies` — the one
  external network call this skill may execute, gated by
  SCM-POLICY-CHECK-001 above
- `registry/found-issue-register.yaml` (via `/found-issue-ownership`, not a
  direct write) — for a confirmed `governance-concern` defect
- `.local/evidences/**`, `reports/` — cycle evidence output (write)

## Forbidden Paths

- `src/**` — no direct write; any `src/**` change required by Step 5 is
  executed by invoking `/product-source-task`, `/add-python-api`,
  `/add-dotnet-api`, or an equivalent governed mutation skill (EP-3)
- Any `gh api` call other than the named PR-comment-reply endpoint — this
  skill's external-network surface is exactly one endpoint
- `.supervisor/skill-registry.yaml`, `registry/format-registry.yaml` — this
  skill does not alter governance or gate authority
- `plans/master-plan.md`, `.local/supervisor/active-plan-lock.json` — never
  touched by a comment-addressing cycle

## Stop Conditions

- Stop before Step 4 RESPOND if any comment in the batch has not yet been
  classified into one of the 4 categories.
- Stop before the `gh api .../replies` call if SCM-POLICY-CHECK-001 has not
  been confirmed for the current session — classify
  `EXTERNAL_BLOCKER: gh_pr_comment_reply_not_authorized` and continue with
  other safe work instead of blocking the session.
- Stop and route through `/found-issue-ownership` if a `governance-concern`
  comment's investigation confirms a real defect — do not respond with a
  generic acknowledgment in place of opening the governed record.
- Stop and delegate (do not self-implement) if a `code-change` or
  `style-nit` fix would touch `src/**`.

## Idempotency Contract

Given the same PR comment thread content and the same 4-category
classification model (this file), re-running this skill's classification
and drafting steps produces the same per-comment classification and the
same drafted response text. The `gh api .../replies` call is the only
non-idempotent, externally-visible action and is executed at most once per
addressed comment thread, gated by SCM-POLICY-CHECK-001.

## Output Format

```
## PR Comment Response: <PR number / thread description>

### Step 1 — READ
- Comments in batch: <N>

### Step 2 — CLASSIFY (per comment)
1. <comment excerpt> → <code-change | question-explanation | style-nit | governance-concern>

### Step 3 — VERIFY (per comment, category-specific)
1. <checklist / grep / systematic-debugging Phase 1-2 result, as applicable>

### Step 4 — RESPOND (per comment)
1. <drafted reply text>

### Step 5 — IMPLEMENT (category-specific)
- code-change: <delegated to /<skill> | gh-fix-ci diagnosis + delegated | N/A>
- style-nit: <applied directly (tests/docs only) | delegated to /<skill> | N/A>
- governance-concern: <found-issue-ownership FI-NNN | no defect, responded only>

### Step 6 — POST
- gh api .../replies calls made: <N> (SCM-POLICY-CHECK-001: confirmed | EXTERNAL_BLOCKER)
```

## Governance Note

FF-original skill, built under TC-EXT-021 of the external-skill-adoption
plan (`plans/.claude/yes-my-earlier-answer-humming-waffle.md` §7.3),
depending on TC-EXT-020 (`/gh-fix-ci`) for CI-failure-specific diagnosis
before drafting a `code-change` reply. No upstream project was verified
during this session's research to cite as a source — this is not an
external import and carries no `external_skill_*` provenance fields.
Cleared by `/skill-scanner` before registration (TC-EXT-021-03). Its
`risk_level: HIGH` mirrors `/receiving-code-review`'s (TC-EXT-016) — the
same external, third-party-visible `gh api .../replies` network call,
gated behind the same SCM-POLICY-CHECK-001 precondition rather than either
being excluded entirely or executed unconditionally.
