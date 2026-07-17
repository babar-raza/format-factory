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
| TC-RG-002 | TODO |
| TC-RG-003 | TODO |

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
