# Risk Register — Acceleration R105

| ID | Risk | Severity | Mitigation |
|----|------|----------|------------|
| R1 | Package identity contamination from global supervisor state | HIGH | Add stream-scoped packaging; label global artifacts as historical |
| R2 | Stale selected-product-gaps.json from R98/wrong stream | HIGH | Regenerate acceleration-specific gaps with R105 sprint ID |
| R3 | Dirty git state prevents clean ACCEPTED | MEDIUM | Classify dirty state honestly; do not claim clean if uncommitted |
| R4 | Acceleration advancement is only packaging repair | MEDIUM | Ensure at least 2 real acceleration improvements land |
| R5 | Test regressions from tool changes | LOW | Run full supervisor test suite before closeout |
