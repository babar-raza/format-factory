# Risk Register (Skills R107)

| Risk | Severity | Mitigation |
|------|----------|------------|
| Inspector modification breaks existing grading | HIGH | All 101 baseline tests must still pass after changes |
| Stream-state contamination persists | MEDIUM | Use isolated reports/skills-r107/ directory |
| Transcript enrichment changes grade outcomes | MEDIUM | Test both with and without transcripts |
| artifacts_missing_count may be builder limitation | LOW | Investigate before attempting fix |
