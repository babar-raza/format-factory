# Risk Register — Skills R106

| # | Risk | Likelihood | Impact | Mitigation |
|---|------|-----------|--------|------------|
| 1 | Transcript integration breaks existing grading | Medium | High | New tests first, then code changes |
| 2 | Orphan command resolution causes registry inconsistency | Low | Medium | Validate commands after changes |
| 3 | Global state overwritten by autonomous-cycle | High | Low | Document as non-primary, use stream-isolated evidence |
| 4 | Test count regression | Low | High | Baseline established (63), monitor throughout |
| 5 | Draft skill promotion without complete command file | Medium | Medium | Validate before promoting |
