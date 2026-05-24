# R61 Train D: artifact_source_commit / final_git_head Policy

**Sprint:** FORMAT-FACTORY-R61-EXTRACTED-BUNDLE-REPLAY-DOTNET-SELF-CONTAINED-SOURCE-COMMIT-POLICY-PHASE12-MEGA-TRAIN-001
**Date:** 2026-05-24
**Status:** COMPLETE

## Defects Repaired

- **IV-R60-009:** source-commit-proof.txt called mega-train commit "FINAL HEAD"
- **IV-R60-010:** Reports described 61780e4 as "final HEAD" — inaccurate
- **IV-R60-011:** No explicit artifact_source_commit / final_git_head policy defined

## Policy Definition

### artifact_source_commit

The last git commit that modified source code or package artifacts.
This is the commit from which all packages were built.

For R60:
- `artifact_source_commit = 61780e4cbd33100460ba872ded5b96c1feae2847`
- This is the mega-train commit (feat: massive changes)
- All 10 Python packages were built from this commit

### final_git_head

The last git commit in the sprint, including chore commits (SHA updates, metadata updates).
This is what `git rev-parse HEAD` returns at sprint closure.

For R60:
- `final_git_head = 1171b4fd55d9199c825705c1e2182578cf0becfb`
- This is the chore commit (update final-verdict with pass 2 SHA)
- No source or package changes after artifact_source_commit

### Relationship

```
artifact_source_commit (61780e4) ← packages built from this
         |
         | (chore: update pass 1 SHA)
         v
    95fdefd
         |
         | (chore: update pass 2 SHA)
         v
final_git_head (1171b4f) ← git HEAD at bundle validation
```

### Invariant

No source files in `src/` and no package artifacts should change after `artifact_source_commit`.
The only commits between `artifact_source_commit` and `final_git_head` should be chore commits
touching only: `reports/`, `state/`, `.local/` (gitignored), metadata files.

## Metadata Fields

R61 sprint metadata should include both fields:

In `source-commit-proof.txt`:
```
artifact_source_commit: <SHA>
final_git_head: <SHA>
commits_between: <count>
source_changes_after_artifact_commit: none
```

In `package-artifact-manifest.yaml`:
```yaml
artifact_source_commit: <full SHA-256 64 chars>
final_git_head: <full SHA-256 64 chars>
```

## Validator Support

The validate_evidence_bundle.py check `check_no_pending` already enforces:
- No PENDING text in any metadata file
- All SHAs must be full 64-char

The artifact_source_commit / final_git_head distinction is enforced by:
- `test_r61_artifact_source_commit_policy.py` (new tests in this train)
- Documentation policy (this file)

## New Tests

See `tests/packaging/test_r61_artifact_source_commit_policy.py` — 6 tests.
