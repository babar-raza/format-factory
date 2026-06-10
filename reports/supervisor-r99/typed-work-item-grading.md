# Train E: Typed Work-Item Grading

## Grade Taxonomy (R99 — complete set)
| Grade | Meaning | Blocks Continuation? |
|-------|---------|---------------------|
| ACCEPTED_VERIFIED | Evidence found, tests verified, criteria confirmed | No |
| ACCEPTED_WITH_LIMITATIONS | Core evidence exists, minor limitation documented | No |
| ACCEPTED_WITH_WARNINGS | Evidence exists, warning noted | No |
| REWORK_REQUIRED | Missing evidence, failed test, or incomplete | No (safe lanes continue) |
| OVERCLAIMED | Declared complete but evidence missing/shallow | YES (critical) |
| REJECTED | Contradicted by evidence, unsafe, fabricated | YES (critical) |
| INSUFFICIENT_EVIDENCE | Declared complete but evidence weak/missing | No (rework lane) |
| BLOCKED_EXTERNAL_GATE | Requires external gate approval | No (blocked lane) |
| NOT_ATTEMPTED | Work item not attempted | No |
| NOT_IN_SCOPE | Not required, no claim made | No |
| DEFERRED_WITH_REASON | Explicitly deferred with documented reason | No |

## Fix (R99: D99-GRADE-01)
Added `declared_status == "deferred"` handler to `grade_declared_work.py` that produces `DEFERRED_WITH_REASON` grade.

## Grading Rules
1. **Path existence is not enough** — the grader checks test file content (D92-03 deep grading)
2. **Source changes require diffs and ledger** — materializer captures these
3. **Product claims require tests/logs** — test methods counted, not just file existence
4. **Tool claims require replay/schema tests or documented rationale**
5. **Summary strings vs file paths** — R98 fix distinguishes summary text from file paths in tests_supporting

## REJECTED vs OVERCLAIMED
- REJECTED: Reserved for manual override or clear fabrication (no automated path produces it)
- OVERCLAIMED: Automatic grade when declared=completed but no evidence found
- Both are CRITICAL and block autonomous continuation
