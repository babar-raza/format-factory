# Risk Register (Skills R105)

| # | Risk | Likelihood | Impact | Mitigation |
|---|------|-----------|--------|------------|
| 1 | Grading pipeline integration breaks existing tests | Medium | High | Run all 50 supervisor tests before and after changes |
| 2 | Stream-state contamination unfixable (infra limitation) | High | Medium | Document and classify; don't claim fixed if not |
| 3 | LIVE handoff execution exceeds Skills stream scope | Medium | High | Generate handoffs only; delegate execution to Mainstream |
| 4 | Orphan command registration causes registry validation failures | Low | Medium | Validate before and after each registry change |
| 5 | Package self-containment regression | Low | Medium | Check package artifact count and missing count |
| 6 | Autonomous-cycle schema rejection | Medium | Medium | Pre-validate declaration YAML against known schema |
| 7 | Context window exhaustion before Train I | Medium | High | Keep train reports concise; parallelize where possible |
