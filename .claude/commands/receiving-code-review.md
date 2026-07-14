---
version: "1.0"
last-updated: "2026-07-14"
phase-available: "all"
gate-required: "Supervisor approval + SCM-POLICY-CHECK-001 (see 'SCM-POLICY-CHECK-001 Precondition' section below) — gates ONLY the gh api repos/{owner}/{repo}/pulls/{pr}/comments/{id}/replies network call inside Step 6 IMPLEMENT; the READ/UNDERSTAND/VERIFY/EVALUATE/RESPOND steps and any non-network IMPLEMENT action require no additional gate beyond ordinary Supervisor review"
skill_type: ATOMIC_SKILL
idempotency: "Same feedback content + same 6-step Response Pattern produce the same clear-vs-needs-clarification classification and the same Implementation Order sequencing; the gh api PR-comment-reply call is the only step with an external side effect and is gated by SCM-POLICY-CHECK-001 rather than executed unconditionally"
loc_budget: "0 lines of executable code (prompt-driven checklist only; no bundled script)"
test_path: "N/A (prompt-spec skill, no executable code) — verification is the manual scan proof recorded under TC-EXT-016-03"
external_skill_origin: true
external_skill_source: obra/superpowers
external_skill_commit: d884ae04edebef577e82ff7c4e143debd0bbec99
external_skill_license: MIT
risk_level: HIGH
created-by: TC-EXT-016-01
product_track: governance
---

# /receiving-code-review

Technical-rigor discipline for processing code review feedback — human,
Supervisor, or automated-reviewer sourced — before implementing any of it.
This is the **first `risk_level: HIGH`** skill in the TC-EXT-0XX
external-skill-import family (TC-EXT-012 through TC-EXT-028): every other
skill imported so far (`skill-scanner`, `systematic-debugging`,
`test-driven-development`, and the 5 Group-2 reviewers) is read-only or
test-file-scoped with no external network call of its own. This skill's Step
6 (IMPLEMENT) can, in the GitHub-thread-reply case, execute a **real external
network call that posts content to GitHub** —
`gh api repos/{owner}/{repo}/pulls/{pr}/comments/{id}/replies`. Posting to a
third-party service on the repository's behalf is qualitatively different
from every LOW/MEDIUM skill registered before it, which is why this entry
carries `risk_level: HIGH` and an explicit gate (see "SCM-POLICY-CHECK-001
Precondition" below) rather than the `Supervisor review`-only gate used for
the read-only imports.

## Attribution

This skill adapts the 6-step Response Pattern, the "Handling Unclear
Feedback" hard stop, the "From External Reviewers" 5-point verification
checklist, the YAGNI check for "implement properly" suggestions, the
Implementation Order, and the "GitHub Thread Replies" `gh api` call from
`obra/superpowers`'s `receiving-code-review` skill (MIT), commit
`d884ae04edebef577e82ff7c4e143debd0bbec99`. These sections are carried over
verbatim-adapted from the upstream skill (fetched directly from
`obra/superpowers` at that commit for this import). The FF-specific actor
mapping (replacing upstream's "your human partner" escalation target, since
this repository has no ambient human partner mid-session per the Human-Free
Autonomy Doctrine — see FF-Specific Actor Mapping below), the wiring into
this repository's Group-2 read-only reviewers (TC-EXT-017), and the
SCM-POLICY-CHECK-001 gate around the `gh api` call are original to this
repository. License: MIT — attribution preserved per license terms; no
upstream code is executed, only its documented methodology is adapted into
prose. Cleared by `/skill-scanner` per TC-EXT-012's mandatory gating rule
(TC-EXT-016-03).

## Purpose

Code review feedback — whether from the user, from a Supervisor-generated
taskcard, or from an automated reviewer skill — is a **suggestion to
evaluate, not an order to follow.** This skill prevents two failure modes at
once: (1) performative agreement followed by blind implementation of
technically wrong or already-considered-and-rejected suggestions, and (2)
silent non-response to feedback that never gets implemented or explicitly
pushed back on. Every item of feedback gets read completely, checked against
codebase reality, and either implemented (one item at a time, tested each)
or pushed back on with technical reasoning — never both simultaneously and
never neither.

## When to Use

- Before implementing any suggestion from a code review — a human reviewer,
  a Supervisor-generated rework item, an inline PR comment, or a
  `/found-issue-ownership` finding routed from one of this repository's own
  reviewer skills.
- Whenever feedback "seems unclear or technically questionable" — this is
  the primary trigger condition, not an edge case.
- Whenever a reviewer requests something be "done properly" or "implemented
  fully" — the YAGNI check below applies before adding generality nobody
  uses.

## The Response Pattern (6 steps, verbatim-adapted)

```
WHEN receiving code review feedback:

1. READ: Complete feedback without reacting
2. UNDERSTAND: Restate requirement in own words (or ask)
3. VERIFY: Check against codebase reality
4. EVALUATE: Technically sound for THIS codebase?
5. RESPOND: Technical acknowledgment or reasoned pushback
6. IMPLEMENT: One item at a time, test each
```

**Core principle:** Verify before implementing. Ask before assuming.
Technical correctness over social comfort.

### Forbidden Responses

**NEVER:** "You're absolutely right!" / "Great point!" / "Excellent
feedback!" (performative), or "Let me implement that now" (before
verification).

**INSTEAD:** Restate the technical requirement; ask clarifying questions;
push back with technical reasoning if wrong; just start working (actions
over words).

## Handling Unclear Feedback (hard stop)

```
IF any item is unclear:
  STOP - do not implement anything yet
  ASK for clarification on unclear items

WHY: Items may be related. Partial understanding = wrong implementation.
```

This is a hard stop, not a soft preference. Partial implementation while
deferring the unclear items is explicitly the wrong pattern — all items in a
multi-item feedback batch are clarified together before Step 6 begins on
any of them, because an unclear item may change how a "clear" item should be
implemented.

**Example:**
```
Reviewer: "Fix 1-6"
Understood: 1, 2, 3, 6. Unclear: 4, 5.

WRONG: Implement 1, 2, 3, 6 now, ask about 4, 5 later
RIGHT: "Items 1, 2, 3, 6 are clear. Need clarification on 4 and 5 before
        proceeding with any of them."
```

## From External Reviewers (5-point checklist, verbatim-adapted)

```
BEFORE implementing:
  1. Check: Technically correct for THIS codebase?
  2. Check: Breaks existing functionality?
  3. Check: Reason for current implementation?
  4. Check: Works on all platforms/versions?
  5. Check: Does reviewer understand full context?

IF suggestion seems wrong:
  Push back with technical reasoning

IF can't easily verify:
  Say so: "I can't verify this without [X]. Should I [investigate/ask/proceed]?"

IF conflicts with a prior architectural decision recorded in this
repository (a plan, a taskcard closeout, an ADR-equivalent note):
  Stop and route through the FF-Specific Actor Mapping's escalation path
  below rather than silently overriding the prior decision.
```

**Rule (adapted from upstream's "External feedback - be skeptical, but check
carefully"):** treat every non-user-authored review comment — including
findings from this repository's own reviewer skills — with the same
skepticism-plus-verification discipline. A finding is a claim to check, not
an instruction to obey.

## Consuming Group-2 Reviewer Findings (TC-EXT-016-02)

This skill's EVALUATE / RESPOND / IMPLEMENT steps are the mechanism by which
an agent processes findings produced by the 5 read-only reviewers registered
under TC-EXT-017 — `silent-failure-hunter`, `type-design-analyzer`,
`comment-analyzer`, `pr-test-analyzer`, and `sharp-edges`. Each of those
skills produces a structured, severity-rated findings list and explicitly
does not modify code itself ("analysis and feedback only" /
"never create, edit, or write files" per their own Constraints sections).
Concretely:

- **EVALUATE**: run the "From External Reviewers" 5-point checklist above
  against each individual finding (by its `Location`/equivalent field), not
  against the reviewer's output as one undifferentiated block. A
  `silent-failure-hunter` CRITICAL finding and a `comment-analyzer` LOW-value
  suggestion in the same batch get evaluated independently.
- **RESPOND**: state a technical acknowledgment or reasoned pushback per
  finding, referencing the finding's own identifying fields (e.g. a
  `silent-failure-hunter` finding's `file:line`, a `type-design-analyzer`
  dimension score, a `sharp-edges` Category/Severity pair) — not a generic
  "addressed the review" statement.
- **IMPLEMENT**: follow the Implementation Order below. The severity/rating
  fields those 5 reviewers already emit map directly onto the "blocking
  issues first" bucket: `silent-failure-hunter`/`comment-analyzer` CRITICAL
  or HIGH severity, `type-design-analyzer` dimensions rated <=4/10,
  `pr-test-analyzer` findings rated 8-10, and `sharp-edges` Critical-severity
  findings are treated as blocking; everything below that threshold is
  triaged into the simple-fix or complex-fix buckets on its own technical
  merits.
- Findings those 5 reviewers already routed to `/found-issue-ownership`
  (per their own Finding Routing sections) retain that `FI-NNN` record —
  this skill's IMPLEMENT step references the existing `found_issue_id`
  rather than opening a duplicate one.

## YAGNI Check for "Professional" Features (verbatim-adapted)

```
IF reviewer suggests "implementing properly":
  grep codebase for actual usage

  IF unused: "This isn't called anywhere in the codebase. Remove it (YAGNI)?"
  IF used: Then implement properly
```

Both a human reviewer's "do this properly" and a `type-design-analyzer`
finding suggesting a fuller invariant-enforcement implementation are subject
to this same check before any generality is added — grep for actual callers
first; do not implement generality nobody exercises.

## Implementation Order (verbatim-adapted)

```
FOR multi-item feedback:
  1. Clarify anything unclear FIRST
  2. Then implement in this order:
     - Blocking issues (breaks, security)
     - Simple fixes (typos, imports)
     - Complex fixes (refactoring, logic)
  3. Test each fix individually
  4. Verify no regressions
```

## FF-Specific Actor Mapping (replaces upstream's "your human partner")

Upstream's "your human partner" framing assumes an ambient human collaborator
mid-session. This repository has no ambient human partner mid-session and
operates under the Human-Free Autonomy Doctrine (CLAUDE.md), so this skill
does not adopt that literal escalation path — consistent with the same
adaptation already applied in `/systematic-debugging` (TC-EXT-013) and
`/test-driven-development` (TC-EXT-014):

- **"From your human partner" (trusted source)** maps to feedback that is
  the user's direct instruction in the current session, or a Supervisor
  taskcard/plan's explicit text — implement after understanding; still ask
  if scope is unclear; skip performative agreement; skip to action.
- **"Conflicts with your human partner's prior decisions: stop and discuss"**
  maps to: stop, and route through `/found-issue-ownership` Step 8
  disposition (or, if the conflict is a genuine architecture-level question
  rather than a defect, classify per AGENTS.md §AG1-AG2's decision loop) —
  never silently override a recorded prior decision, and never treat the
  absence of an ambient human as license to guess.
- **"If uncomfortable pushing back out loud, tell your partner"** maps to:
  state the pushback plainly, in the same response, with technical
  reasoning — there is no separate private channel to defer to in this
  repository's autonomous execution model.

## When To Push Back

Push back when: the suggestion breaks existing functionality; the reviewer
lacks full context; it violates YAGNI (unused feature); it is technically
incorrect for this stack; legacy/compatibility reasons exist; or it
conflicts with a prior architectural decision recorded in this repository.

**How:** technical reasoning, not defensiveness; specific questions;
reference working tests/code; route through the FF-Specific Actor Mapping's
escalation path above if the conflict is architectural.

## Acknowledging Correct Feedback

```
"Fixed. [Brief description of what changed]"
"[specific issue] confirmed. Fixed in [location]."
[Just fix it and show it in the diff]

NOT: "You're absolutely right!" / "Great point!" / "Thanks for catching that!"
     / any gratitude expression
```

Actions over words — the diff itself shows the feedback was heard.

## Gracefully Correcting Your Own Pushback

If a pushback turns out to be wrong:
```
"Verified this and the suggestion is correct — my initial understanding was
wrong because [reason]. Implementing now."
```
State the correction factually; no long apology, no over-explaining.

## SCM-POLICY-CHECK-001 Precondition (gates the `gh api .../replies` call ONLY)

This precondition applies **only** to Step 6 IMPLEMENT when the concrete
action is `gh api repos/{owner}/{repo}/pulls/{pr}/comments/{id}/replies`
(replying to an inline GitHub PR review-comment thread). It does not gate
READ/UNDERSTAND/VERIFY/EVALUATE/RESPOND, and it does not gate any IMPLEMENT
action that is a local file edit rather than a network call.

Quoted from the plan's §7.2 (`plans/.claude/yes-my-earlier-answer-humming-waffle.md`),
adapted for this skill's file:

```yaml
precondition_id: SCM-POLICY-CHECK-001
statement: >
  Before this skill posts any PR comment reply via
  `gh api repos/{owner}/{repo}/pulls/{pr}/comments/{id}/replies`, the
  executing agent must confirm that Format Factory's existing SCM Agent
  sprint/user policy (AGENTS.md §AG4, CLAUDE.md's Human-Free Autonomy
  Doctrine) currently authorizes this action class. This is a policy-state
  read, not a request for a human to approve this specific invocation.
if_policy_already_authorizes: proceed autonomously, no further human
  involvement at any stage
if_policy_does_not_yet_authorize: classify as EXTERNAL_BLOCKER (per
  CLAUDE.md's existing named pattern, e.g.
  EXTERNAL_BLOCKER: gh_pr_comment_reply_not_authorized) rather than silently
  stopping or silently proceeding — this is Format Factory's own existing
  classification discipline, not a new gate invented by this skill.
```

**Why a policy-state check rather than a per-invocation human stop:**
AGENTS.md §AG4 names commit (AG4.1) and push (AG4.2) as the SCM Agent's
governed action classes — it does not literally enumerate "reply to a GitHub
PR comment." The plan's §7.1 reconciliation extends the same shape of
reasoning that already governs commit/push to this new action class: *"SCM
Agent executes when sprint policy authorizes"* / *"Push tasks: SCM Agent
executes when credentials available + branch policy allows + sprint/user
policy authorizes."* Applying that shape here: if the standing SCM Agent
policy for this repository currently authorizes `gh api` PR-comment-reply
posting, this skill proceeds with no additional per-instance stop. If it
does not yet authorize it, this skill does not silently execute the call —
it classifies the gap honestly (`EXTERNAL_BLOCKER:
gh_pr_comment_reply_not_authorized`) and record it in the gap register,
exactly as AG4.3 requires for an honest push blocker.

**Verification procedure before the `gh api .../replies` call executes:**
1. Read AGENTS.md §AG4 and CLAUDE.md's "SCM Agent" doctrine (Human-Free
   Autonomy Doctrine section) for the current standing policy text.
2. Confirm no narrower policy override exists for `gh api` PR-comment
   posting specifically (e.g. a gap-ledger entry or a plan amendment that
   restricts it beyond the general commit/push policy).
3. If both checks pass: proceed with the call, and record the policy
   citation (file + section) in the invoking taskcard's evidence.
4. If either check fails or is ambiguous: do not call `gh api`. Emit
   `EXTERNAL_BLOCKER: gh_pr_comment_reply_not_authorized`, record it, and
   continue with the next safe work item rather than blocking the session.

## GitHub Thread Replies (verbatim-adapted, gated as above)

When replying to inline review comments on GitHub, reply in the comment
thread — `gh api repos/{owner}/{repo}/pulls/{pr}/comments/{id}/replies` —
not as a top-level PR comment. This is the one command in this skill with an
external, third-party-visible side effect, and it executes only after the
SCM-POLICY-CHECK-001 precondition above is satisfied (or the gap is
classified per that section).

## Mandatory Validations

- `feedback_read_completely_before_response` — Step 1 (READ) completed for
  the entire feedback batch before any Step 5 (RESPOND) or Step 6 (IMPLEMENT)
  action, for any item in the batch.
- `unclear_items_block_all_implementation` — if any item in a multi-item
  feedback batch is unclear, no item in that batch (including the clear
  ones) proceeds to Step 6 until clarification is obtained.
- `external_reviewer_checklist_applied` — the 5-point checklist is recorded
  as having been run (or explicitly marked "cannot verify, asking") for
  every item sourced from an external/automated reviewer, including the 5
  Group-2 reviewer skills.
- `yagni_grep_recorded` — when a reviewer requests a feature be "implemented
  properly," the codebase-usage grep result is recorded before deciding to
  implement or remove.
- `gh_api_reply_gated_by_scm_policy_check_001` — the
  `gh api .../replies` call never executes without a recorded
  SCM-POLICY-CHECK-001 confirmation (or a recorded
  `EXTERNAL_BLOCKER: gh_pr_comment_reply_not_authorized` in its place).
- `no_direct_src_mutation_outside_governed_skill` — any Step 6 IMPLEMENT
  action that touches `src/**` is executed by invoking the applicable
  already-governed mutation skill (`/product-source-task`,
  `/add-python-api`, `/add-dotnet-api`, etc.) per EP-3 (CLAUDE.md,
  "Skill-Driven Architecture"); this skill creates no direct product-source
  mutation pathway of its own.

## Allowed Paths

- The feedback content itself (review comment text, taskcard rework items,
  Group-2 reviewer findings) — read
- `tests/**` — write directly for a Step 6 fix that is test-only
- Any source/spec/documentation file relevant to the feedback — read only,
  to VERIFY (Step 3) against codebase reality
- `gh api repos/{owner}/{repo}/pulls/{pr}/comments/{id}/replies` — the one
  external network call this skill may execute, gated by
  SCM-POLICY-CHECK-001 above
- `registry/found-issue-register.yaml` (via `/found-issue-ownership`, not a
  direct write) — for routing blocking findings
- `.local/evidences/**`, `reports/` — cycle evidence output (write)

## Forbidden Paths

- `src/**` — no direct write; any `src/**` change required by Step 6 is
  executed by invoking `/product-source-task`, `/add-python-api`, or
  `/add-dotnet-api` (EP-3)
- Any `gh api` call other than the named PR-comment-reply endpoint — this
  skill's external-network surface is exactly one endpoint, not a general
  `gh` capability
- `.supervisor/skill-registry.yaml`, `registry/format-registry.yaml` — this
  skill does not alter governance or gate authority
- `plans/master-plan.md`, `.local/supervisor/active-plan-lock.json` — never
  touched by a review-response cycle

## Stop Conditions

- Stop (Handling Unclear Feedback) if any item in a multi-item batch is
  unclear — ask before implementing any item in that batch.
- Stop before the `gh api .../replies` call if SCM-POLICY-CHECK-001 has not
  been confirmed for the current session — classify
  `EXTERNAL_BLOCKER: gh_pr_comment_reply_not_authorized` and continue with
  other safe work instead of blocking the session.
- Stop and route through the FF-Specific Actor Mapping's escalation path if
  feedback conflicts with a recorded prior architectural decision.
- Stop (do not batch-implement) if Step 6 would touch more than one
  unrelated item without testing the previous one first.

## Idempotency Contract

Given the same feedback content and the same 6-step Response Pattern (this
file), re-running the methodology produces the same clear/unclear
classification, the same push-back-or-implement disposition per item, and
the same Implementation Order sequencing. The `gh api .../replies` call is
the only non-idempotent, externally-visible action and is executed at most
once per reply target, gated by SCM-POLICY-CHECK-001.

## Output Format

```
## Code Review Response: <short feedback source description>

### Step 1-2 — READ / UNDERSTAND
- Items: <N>, restated in own words (or flagged unclear)

### Handling Unclear Feedback
- Unclear items: <list, or "none">
- If any unclear: STOPPED here pending clarification

### Step 3-4 — VERIFY / EVALUATE (per item)
1. Item: <description>
   - External Reviewer checklist (if applicable): <5 checks, pass/fail/N-A>
   - YAGNI grep (if applicable): <result>
   - Verdict: implement | push back | cannot verify

### Step 5 — RESPOND (per item)
1. <technical acknowledgment or reasoned pushback text>

### Step 6 — IMPLEMENT (Implementation Order)
- Blocking issues: <list, status>
- Simple fixes: <list, status>
- Complex fixes: <list, status>
- gh api .../replies calls made: <N> (SCM-POLICY-CHECK-001: confirmed | EXTERNAL_BLOCKER)
- Regression check: PASS/FAIL
```

## Governance Note

Per TC-EXT-012 (external-skill-import plan), this skill was cleared by
`/skill-scanner` before registration (TC-EXT-016-03) — the mandatory gating
step for every external-skill import in TC-EXT-013 through TC-EXT-028. Its
`risk_level: HIGH` (the first HIGH entry in this family) reflects the single
real external network call it can execute
(`gh api repos/{owner}/{repo}/pulls/{pr}/comments/{id}/replies`), which is
gated behind the SCM-POLICY-CHECK-001 precondition (§7.2 of
`plans/.claude/yes-my-earlier-answer-humming-waffle.md`) rather than either
being excluded entirely or executed unconditionally.
