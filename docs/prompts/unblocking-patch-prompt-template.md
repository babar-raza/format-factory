# Unblocking Patch Prompt Template

**Mode:** EXECUTION MODE
**Sprint type:** UNBLOCKING PATCH
**Purpose:** Use this template for a minimal targeted fix to unblock a specific failing check, broken tool, or missing prerequisite. Scope is as narrow as possible.

---

MODE:
EXECUTION MODE.

Sprint type:
UNBLOCKING PATCH.

Sprint name:
Unblocking Patch: <exact blocker being fixed>.

Project:
format-factory

Repo path:
C:\Users\prora\OneDrive\Documents\GitHub\format-factory

Primary evidence input:
<absolute path to the blocker evidence bundle, or the latest passing bundle>

Goal:
Fix the specific blocker: <describe the exact blocker in one sentence>.
This patch changes only the minimum files required to unblock the failing check.
No scope expansion. No additional improvements. No gate changes.

Blocker description:
- What is failing: <exact failure message or check name>
- Root cause (if known): <root cause>
- Expected fix: <1-3 sentence description>

Hard prohibitions:
Do not fix anything beyond the specific blocker.
Do not change gate statuses.
Do not create product source.
Do not push.

Read first:

1. The specific file or tool that is failing.
2. The evidence bundle for the last passing sprint.
3. The evidence contract for the blocked sprint.
4. git status --short.

Patch steps:

1. Read the failing file or tool.
2. Identify the exact change needed.
3. Apply the change.
4. Re-run the failing check. Expected: PASS.
5. Run python tools/evidence/check_current_state_consistency.py. Expected: PASS.
6. Run the evidence bundle validator. Expected: BUNDLE_VALIDATION: PASS.

Scope boundary:

Only these files may change:
- <exact list of files that need patching>

No other files may change. If the fix requires additional files, stop and escalate to a PLAN MODE review.

Evidence contract

Contract path: tools/evidence/contracts/<patch-sprint-name>.yaml
min_metadata_count: 20
Output: .local/evidence-bundles/<patch-sprint-name>-YYYYMMDD-HHMMSS.zip

Commit message: fix: <short description of what was fixed>

Do not push.

Self-challenge:

1. Did I fix only the specific blocker?
2. Did I avoid scope expansion?
3. Did I re-run the failing check and confirm PASS?
4. Did I avoid gate changes?
5. Did I avoid product source?
6. Did I avoid pushing?
7. Did the evidence bundle validate?

Final response:

1. Blocker: <what was blocked>
2. Fix applied: <what was changed>
3. Check result after fix: PASS or FAIL
4. Commit hash.
5. UNBLOCKING PATCH ONLY -- NO GATE CHANGES -- NO PUSH

EVIDENCE_BUNDLE: <absolute Windows path to zip>
