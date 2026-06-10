# Risk Register — Acceleration R107

| Risk | Impact | Mitigation |
|------|--------|-----------|
| Hard gates break existing test suite | High | Run full suite after each gate change |
| Evidence quality enforcement too strict | Medium | Use thresholds, not binary pass/fail |
| Continuation policy changes break autonomous loop | High | Add integration tests, preserve backward compat |
| Prompt quality gate rejects valid prompts | Medium | Allow known-good exemptions in tests |
