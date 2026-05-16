# R19 Evidence Hygiene and Post-Commit Bundle Policy
Sprint: FORMAT-FACTORY-R19-HIGH-THROUGHPUT-ACQUISITION-TRAIN-001
Date: 2026-05-16
Gate: 1 — Evidence Hygiene Repair

## R18 Stale Metadata Audit

### Issue 1: verdict.md — Stale HEAD Reference

**Finding:** R18 verdict.md references HEAD as 8ba4f83 (the R17 commit), but the actual
R18 commit was 42052c2.

**Root Cause:** verdict.md was written as a metadata artifact before the git commit was made.
The pre-commit bundle metadata captured the pre-commit HEAD.

**Classification:** PRE-COMMIT_ARTIFACT — historical. Do not retroactively modify
evidence bundles. The git-log.txt in the bundle *does* show 42052c2 as the correct commit.

**Corrective Policy (new):**
1. verdict.md MUST NOT reference specific git commit hashes unless built post-commit
2. If pre-commit, verdict.md must state: "git-log.txt is authoritative for HEAD"
3. Alternatively: use `[POST-COMMIT-HEAD]` placeholder filled by build script

### Issue 2: r18-sprint-gate-status.md — Gate 14 "IN_PROGRESS" After Bundle

**Finding:** The sprint gate status file records Gate 14 (evidence bundle) as "IN_PROGRESS"
even though the bundle was successfully built and validated.

**Root Cause:** Sprint gate status file was written mid-sprint before bundle completion.

**Classification:** PRE-COMMIT_ARTIFACT — historical.

**Corrective Policy (new):**
1. Sprint gate status file must be updated AFTER bundle validation
2. Gate 14 status must read "PASS" or "COMPLETE" if BUNDLE_VALIDATION: PASS was output
3. The build script should validate that no metadata file contains "IN_PROGRESS" for
   gates that have evidence of completion

### Issue 3: Inconsistent Test Count Narratives

**Finding:** Sprint summary referenced 1405 passed (full suite), while prototype-specific
metadata referenced 38/38. Both are correct but uncoordinated.

**Root Cause:** Different files describe different test scopes without making that explicit.

**Classification:** SCOPE_AMBIGUITY — not an error, but confusing.

**Corrective Policy (new):**
1. validation-command-log.txt must contain ONE authoritative summary line labeled:
   `AUTHORITATIVE_TEST_RESULT: <N> passed, <M> skipped, <K> failed (scope: <scope>)`
2. scope values: "full_suite" | "skills_only" | "format_specific:<name>"
3. All other test references must note their scope

### Issue 4: "Human Approval Required" Blockers in Agent-Actionable Positions

**Finding:** Multiple documents (gate5-requirements-readiness.md, sprint gate status,
taskcards) say "requires human approval" for decisions the agent can make under delegated
authority per master-plan.md governance model.

**Classification:** POLICY_DRIFT — corrected in Gate 2 normalization.

## New Evidence Tooling Policy

### Policy P-EVID-001: Post-Commit Bundle Preferred

Evidence bundles must be built AFTER the git commit. If pre-commit build is required
(emergency_blocker_bundle: true), the git-log.txt MUST contain the final commit that
will be made, updated as the last step before bundle validation.

### Policy P-EVID-002: No IN_PROGRESS in Final Bundle

The --check-no-pending flag on validate_evidence_bundle.py exists to catch this.
R19 and all future sprints must use --check-no-pending in the final validation step
for gate status files.

### Policy P-EVID-003: Authoritative Test Line

validation-command-log.txt must end with:
```
AUTHORITATIVE_TEST_RESULT: <N> passed, <M> skipped (scope: full_suite)
```

### Policy P-EVID-004: Verdict Must Not Reference Stale HEAD

verdict.md must either:
a) Be written after commit and reference the actual commit hash, or
b) Say "git-log.txt is authoritative for HEAD" without specifying a hash

## Evidence Tooling Test Enhancement

The existing evidence bundle tests in tests/evidence/ should be extended to check:
1. That metadata files don't claim BUNDLE_BUILT_BEFORE_COMMIT without emergency_blocker
2. That validation-command-log.txt contains an AUTHORITATIVE_TEST_RESULT line

This enhancement is flagged as a taskcard (EVIDENCE-HYGIENE-ENFORCEMENT).
Implementation is not required to unblock R19 gate progress.

GATE_1_EVIDENCE_HYGIENE: CLASSIFIED_AND_POLICY_DOCUMENTED
