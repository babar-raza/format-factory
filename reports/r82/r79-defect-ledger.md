# R82 — R79 Defect Ledger

All defects found by supervisor in R79 review.

| ID | Severity | Description | Fix Train |
|----|----------|-------------|-----------|
| D79-01 | CRITICAL | Wrong artifact uploaded — inner bundle not supervisor review package | Q |
| D79-02 | CRITICAL | Physical package artifacts absent from uploaded bundle | D |
| D79-03 | CRITICAL | Package manifest has SHA prefixes (8 chars) not full 64-char hashes | D |
| D79-04 | CRITICAL | `installed_artifact_policy: none` unacceptable for package-readiness sprint | R82 contract |
| D79-05 | CRITICAL | Installed-wheel tests skip (not fail) when wheel missing | E |
| D79-06 | HIGH | 88 __pycache__/.pyc files in evidence bundle | G |
| D79-07 | HIGH | `tools/repro/reproduce_format.py` wrong import namespaces | F |
| D79-08 | HIGH | Review package claim without physical artifacts in bundle | D/Q |
| D79-09 | MEDIUM | R80/R81 reports contaminate R79 bundle (authority contamination) | A |
| D79-10 | MEDIUM | State shows R81 deferred — sprint mismatch | C |
| D79-11 | MEDIUM | State JSON points to R81 deferred | C |
| D79-12 | MEDIUM | Sprint-state mismatch (R79 uploaded, state says R81) | C |
| D79-13 | MEDIUM | reports/r81/final-verdict.md is stub (R81_DEFERRED_NOT_YET_EXECUTED) | A |
| D79-14 | MEDIUM | reports/r81/authoritative-test-result.md says NOT_STARTED | A |
| D79-15 | MEDIUM | R80/R81 classification absent — need formal authority classification | A |
| D79-16 | LOW | ZST 9 failures in supervisor sandbox (missing dependency, expected) | K |
| D79-17 | LOW | No finalized format — overclaim risk | B/I |

DEFECT_COUNT: 17
CRITICAL: 5
HIGH: 3
MEDIUM: 7
LOW: 2
