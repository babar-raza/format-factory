---
version: "1.0"
last-updated: "2026-07-14"
phase-available: "all"
gate-required: null
skill_type: ATOMIC_SKILL
idempotency: "Same target file/diff + same 5-phase checklist produce the same findings; read-only end to end"
loc_budget: "0 lines of executable code (prompt-driven checklist only; no bundled script)"
test_path: "N/A (prompt-spec skill, no executable code) — verification is the manual scan proof recorded under TC-EXT-017-01"
external_skill_origin: true
external_skill_source: anthropics/claude-code
external_skill_commit: 988b3e56432775c09bba903ba22522b97cd0f2fb
external_skill_license: Apache-2.0
risk_level: LOW
created-by: TC-EXT-017-01
product_track: governance
---

# /silent-failure-hunter

Read-only reviewer that hunts for silent failures — error-handling code that
swallows, hides, or misreports problems instead of surfacing them. Never
modifies the reviewed target; produces a findings list only.

## Attribution

This skill adapts the 5 named principles and the 5-phase review process from
the `silent-failure-hunter` skill in Anthropic's `claude-code` PR Review
Toolkit (`anthropics/claude-code`, Apache-2.0), commit
`988b3e56432775c09bba903ba22522b97cd0f2fb`. The principles, phase structure,
and per-issue output fields are carried over near-verbatim from the upstream
skill; the FF-specific finding-routing rule (CRITICAL/HIGH findings hand off
to `/found-issue-ownership`) is original to this repository. License:
Apache-2.0 — attribution preserved per license terms; no upstream code is
executed, only its documented methodology is adapted into prose. Cleared by
`/skill-scanner` per TC-EXT-012's mandatory gating rule.

## Purpose

Silently swallowed errors are one of the hardest defect classes to catch by
reading code casually — the code "works" until the exact input that would
have raised a signal instead vanishes into an empty catch block, a generic
`except Exception: pass`, or a fallback path nobody documented as
intentional. This skill applies a structured, repeatable review to surface
those cases as evidence-backed findings rather than leaving them for a future
incident to discover.

## When to Use

- Reviewing any diff or file that adds, modifies, or removes error-handling
  code (try/except, error callbacks, promise/future rejection handlers,
  validation-failure branches).
- Before closing a taskcard whose scope touched exception handling, input
  validation, or fallback/default-value logic.
- On request, against any existing file, as an ad hoc audit.

## 5 Principles

1. **Silent failures are unacceptable.** Errors must never disappear without
   a trace — no error should vanish without being logged, surfaced, or
   deliberately and explicitly re-raised.
2. **Users deserve actionable feedback.** Every error path should tell the
   user (or the calling code) what happened and what to do next — not just
   that "something went wrong."
3. **Fallbacks must be explicit and justified.** Silently degrading to a
   default value, cached value, or no-op is a failure mode unless the
   fallback's existence and trigger conditions are documented at the point
   of use.
4. **Catch blocks must be specific.** Catching a broad exception type
   (`Exception`, `Error`, bare `except:`) hides unrelated failures behind the
   same handler and is a finding unless narrowed or justified.
5. **Mock/fake implementations belong only in tests.** A stub, mock, or
   hardcoded placeholder return value reachable from a production code path
   is a silent failure waiting to happen, not a legitimate implementation.

## Steps (the real 5-phase process, adapted)

1. **Phase 1 — Identify All Error Handling Code.** Enumerate every
   try/except (or language-equivalent) block, error callback, promise/future
   rejection handler, and explicit error-code check in the reviewed target.
   Missing this step means later phases silently skip handlers that were
   never found.
2. **Phase 2 — Scrutinize Each Error Handler.** For every handler identified
   in Phase 1, assess these 5 dimensions:
   - **Logging Quality** — is the error logged with enough context
     (message, stack trace, relevant input) to diagnose it later?
   - **User Feedback** — does the user/caller learn that something failed,
     or does execution continue as if it succeeded?
   - **Catch Block Specificity** — is the caught exception type as narrow as
     the actual failure mode, or a broad catch-all?
   - **Fallback Behavior** — if a fallback/default is used, is it explicit,
     documented, and justified — or a silent substitution?
   - **Error Propagation** — does the error reach a layer that can act on
     it, or is it absorbed at a layer that cannot meaningfully respond?
3. **Phase 3 — Examine Error Messages.** Read the literal text of every
   error/log message surfaced by the handlers above. Flag messages that are
   vague ("something went wrong"), misleading (describe a different failure
   than what actually occurred), or absent entirely.
4. **Phase 4 — Check for Hidden Failures.** Specifically hunt for: empty
   catch blocks (**absolutely forbidden** — always a finding, no exception),
   catch-and-continue patterns with no logging, swallowed return codes, and
   any code path where a failure condition is checked but the check's
   negative branch does nothing observable.
5. **Phase 5 — Validate Against Project Standards.** Cross-check findings
   against this repository's own standards: EP-1 Zero-Stub Enforcement and
   the Human-Free Autonomy Doctrine's "never claim completion without
   evidence" rule (CLAUDE.md) — a silent failure in production code is a
   direct EP-1 violation if it stems from an unfinished/stubbed handler.

## Output Format

```
## Silent Failure Review: [Target]

### Summary
- Findings: <N> (Critical: x, High: x, Medium: x)

### Findings
1. Location: <file:line>
   Severity: CRITICAL | HIGH | MEDIUM
   Issue Description: <what the handler does wrong>
   Hidden Errors: <what failure(s) this handler currently conceals>
   User Impact: <what the user/caller experiences instead of a clear error>
   Recommendation: <concrete fix>
   Example: <before/after snippet or reference>

(repeat per finding, most severe first)
```

## Finding Routing

- **CRITICAL or HIGH severity findings** — hand off to
  `/found-issue-ownership` (Step 1 — Capture) before the reviewed taskcard
  closes. These are silent failures with a plausible production-impact path
  (data loss, masked crash, security-relevant bypass) and must become a
  durable `FI-NNN` record, not a prose-only review comment.
- **MEDIUM severity findings** — logged inline in the review output only;
  no mandatory hand-off, though the reviewing agent may open a
  `/found-issue-ownership` entry at its discretion if a pattern recurs
  across multiple MEDIUM findings in the same file.

## Allowed Paths

- The file(s)/diff under review — read only
- `.claude/commands/silent-failure-hunter.md` (this file, its own reference
  checklist)
- No report file is written by default — findings are recorded inline in the
  invoking taskcard's evidence

## Forbidden Paths

- **This skill never writes to the reviewed target, or to any other file.**
  It is read-only end to end: no edits to source, tests, configuration, or
  documentation under review.
- `src/**`, `tests/**` — read only, for the purpose of locating and
  scrutinizing error-handling code; never mutated by this skill
- `.supervisor/skill-registry.yaml`, `registry/found-issue-register.yaml` —
  never written directly; CRITICAL/HIGH hand-off goes through
  `/found-issue-ownership`, not a direct write from this skill

## Constraints

- Read-only in all 5 phases. No writes, no external network calls, no hooks
  executed.
- An empty catch block is always a finding — there is no severity threshold
  below which an empty catch block is acceptable to omit from the findings
  list.

## Idempotency Contract

Given the same target file/diff content and the same 5-phase checklist (this
file), the review produces the same findings and the same severities. No
randomness; no time-dependent output.

## Governance Note

Per TC-EXT-012 (external-skill-import plan) and TC-EXT-017 (5 read-only
reviewer imports), this skill was cleared by `/skill-scanner` before
registration. It is a pure prompt/methodology spec: no bundled script, no
automated file operations, no hooks, and no external network calls of its
own.
