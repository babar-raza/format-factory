# R52 Risk Register

**Sprint:** FORMAT-FACTORY-R52-STATE-CONSISTENT-INSTALLED-ARTIFACT-BASELINE-CLEAN-001

## Active Risks

| ID | Description | Severity | Mitigation |
|----|-------------|----------|------------|
| R52-R001 | Proof SHA sidecar not enforced — validators only WARN | LOW | WARN is appropriate; sidecar protocol documented |
| R52-R002 | State/verdict agreement check requires bundle file presence | LOW | INV-003 false-blocker detection implemented |
| R52-R003 | COMMAND_LOG_STALE_PATTERNS too broad — future legit content may match | LOW | Patterns are specific enough; monitor |
| R52-R004 | Auto-proof Pass 1 transient placeholder exclusion is exact-match — builder changes would break it | LOW | Document exact format; add test for regression |

## Closed Risks (resolved in R52)

| ID | Description | Resolution |
|----|-------------|------------|
| R51-R001 | State snapshot returns unknown for R51 verdict | RESOLVED — Format C support added |
| R51-R002 | Validator misses state/verdict contradiction | RESOLVED — check_state_verdict_agreement updated |
| R51-R003 | Auto-proof builder breaks on PROOF_FILE_PLACEHOLDER patterns | RESOLVED — IN PROGRESS text changed |
| R51-R004 | test_auto_proof_bundle.py: 7 failures from Pass 1 PLACEHOLDER catch | RESOLVED — transient exclusion added |
