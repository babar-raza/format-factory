# Risk Register — Acceleration R106

| Risk | Impact | Mitigation |
|------|--------|-----------|
| R105 regrading reveals deeper issues | Medium | Fix in-sprint if possible; document as forward work otherwise |
| Cycle integration breaks existing autonomous-cycle | High | Add integration tests; preserve backward compatibility |
| Raw-proof hardening too complex for single sprint | Medium | Implement core scoring; defer edge cases |
| Multi-stream dirty state causes test interference | Low | Use isolated test fixtures; no global state mutation |
| Anti-skip changes break existing 42 tests | Medium | Run full test suite after changes |
| Package pilot fails identity validation | Medium | Debug using R105 validator; fix and re-pilot |
