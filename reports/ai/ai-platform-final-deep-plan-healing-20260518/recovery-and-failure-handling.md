# Recovery and Failure Handling

**Sprint:** FORMAT-FACTORY-AI-PLATFORM-FINAL-DEEP-PLAN-HEALING-001
**Date:** 2026-05-18
**Gate:** 8
**Lane:** L8

---

## 1. Purpose

Define recovery procedures for failures during AI platform planning and implementation sprints. No destructive git operations (stash, reset, restore, clean) are permitted.

## 2. Planning Sprint Recovery

### 2.1 Evidence Validation Fails

**Symptom:** `validate_evidence_bundle.py` reports BUNDLE_VALIDATION: FAIL.

**Recovery:**
1. Read validation error output to identify missing/invalid artifacts
2. Fix identified artifacts (update report content, add missing metadata)
3. Rebuild evidence bundle
4. Re-validate
5. If still fails: document failure in validation-command-log.md, continue with best-effort bundle

### 2.2 Prior Artifacts Missing

**Symptom:** Expected docs/ai/ file or taskcard not found.

**Recovery:**
1. Check git log for deletion commit
2. If accidentally deleted: recreate from memory/42 description and prior evidence bundles
3. If intentionally removed: document in live-artifact-inventory.md, adjust plan
4. Do NOT recreate files you cannot verify content for

### 2.3 Shared File Conflict with Parallel Sprint

**Symptom:** File modified by both AI planning sprint and R24 sprint.

**Recovery:**
1. Check which files overlap using `git diff --name-only`
2. If overlap is in plans/master-plan.md: AI sprint appends new section, does not modify existing
3. If overlap is in AGENTS.md or GOVERNANCE.md: AI sprint documents what needs to change but does NOT modify (defers to owning sprint)
4. If overlap is in memory/: AI sprint updates memory/42 only, does not touch other memory files
5. Stage only AI-owned files

### 2.4 Partial Commit Failure

**Symptom:** `git commit` fails after staging.

**Recovery:**
1. Check pre-commit hook output for failure reason
2. Fix identified issue (e.g., trailing whitespace, file too large)
3. Re-stage fixed files
4. Create NEW commit (do not amend)
5. If hook cannot be satisfied: document blocker in final-verdict.md, set verdict to BLOCKED

### 2.5 Evidence Tooling Cannot Run

**Symptom:** `build_evidence_bundle.py` or `validate_evidence_bundle.py` errors.

**Recovery:**
1. Check Python environment (PYTHONPATH prefix required)
2. Check that evidence contract YAML is valid
3. If tooling is broken: create manual evidence bundle (zip of relevant files with manifest)
4. Document tooling failure in validation-command-log.md
5. Set verdict to READY_WITH_REVIEW_NOTES (not BLOCKED)

## 3. Implementation Sprint Recovery (Future Reference)

### 3.1 Endpoint Unreachable

1. Check GPT_OSS_ENDPOINT env var is correct
2. Check network connectivity
3. If cached model registry is <24h old: use cache, log warning
4. If cache expired: fail closed, document in evidence
5. Do NOT retry in infinite loop — log failure and stop

### 3.2 Model Discovery Returns Empty

1. Log ROLE_UNAVAILABLE for all roles
2. Stop all AI operations
3. Document in telemetry
4. Human investigation required

### 3.3 Telemetry Write Failure

1. AI call result is NOT returned to caller (fail the call)
2. Log write failure to stderr
3. Do NOT silently proceed without telemetry
4. Check disk space, permissions, file locks

### 3.4 Vector Index Corruption

1. Log corruption detection
2. Delete corrupted index files
3. Rebuild from normalized spec artifacts
4. Verify rebuild by running retrieval test
5. Log rebuild in audit trail

### 3.5 Authority State Machine Violation

1. Log attempted invalid transition with full context
2. Reject the transition (do not apply)
3. Artifact remains in previous valid state
4. Investigate root cause (code bug vs data corruption)

## 4. What NOT to Do

| Action | Why Forbidden |
|--------|--------------|
| `git stash` | Can lose context if pop fails or conflicts |
| `git reset --hard` | Destroys uncommitted work |
| `git restore .` | Reverts all changes including intentional ones |
| `git clean -f` | Deletes untracked files including R24 sprint work |
| `git checkout .` | Same as restore — destroys uncommitted changes |
| Delete .local/ to "fix" issues | Destroys telemetry, vector indexes, model registry |
| Retry endpoint in infinite loop | Blocks sprint, wastes resources |
| Amend previous commit | Can lose previous commit's changes |
| Force push | Overwrites upstream history |
