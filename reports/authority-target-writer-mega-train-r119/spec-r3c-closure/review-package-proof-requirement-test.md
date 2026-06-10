# Review Package Proof Requirement Test
Sprint: FORMAT-FACTORY-AUTHORITY-LAYERS-AND-TARGET-WRITER-MEGA-TRAIN-R119-001

## Protocol
Per `reports/spec-authority-r3-closure-repair/package-proof-protocol.md`:
- `review-package-proof.md` is written AFTER the ZIP (cannot be inside the ZIP it describes)
- Evidence declarations must NOT list review-package-proof.md in `evidence_artifacts` if it hasn't been written yet
- Anti-skip should not flag the ABSENCE of review-package-proof.md as a rework violation when the declaration marks it as post-cycle

## Validation

### Check 1: review-package-proof.md present after cycle
**Result:** PASS
`reports/spec-authority-r3-closure-repair/review-package-proof.md` exists.

### Check 2: SHA-256 in proof file matches bundle
**Result:** PASS
SHA-256: `cda78872d5b98e5e1b5634257700c63ef452b3111f9153d58d827acab409e96d`

### Check 3: Proof file was written after ZIP creation (not before)
**Result:** PASS (by design per protocol)
The proof file timestamp is AFTER the ZIP timestamp — correct sequence.

### Check 4: Anti-skip should not block if proof is post-cycle
**Result:** DOCUMENTED ISSUE
The anti-skip detector does not distinguish between pre-cycle and post-cycle artifacts.
Future fix: add `post_cycle_artifacts` list to evidence declaration schema to suppress
false violations for review-package-proof.md and final-git-status.txt.

## Recommendation
Add `post_cycle_artifacts` field to `evidence-declaration.yaml` schema:
```yaml
post_cycle_artifacts:
  - review-package-proof.md
  - final-git-status.txt
```
These should be skipped by anti-skip checking since they cannot exist before cycle runs.
