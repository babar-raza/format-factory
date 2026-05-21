# R44 Risk Register

| ID | Risk | Likelihood | Impact | Mitigation |
|----|------|-----------|--------|------------|
| R44-R01 | `pytest-timeout` not installed — timeout tests skip | High | Medium | Install in .local/test-venv or use signal-based timeout |
| R44-R02 | `python -m build` not in system Python | High | Low | Use `.local/build-venv` from R43 (build==1.5.0) |
| R44-R03 | .NET NuGet consumer project `restore` fails on local feed | Medium | High | Use `dotnet nuget add source` with local .local/packages/ |
| R44-R04 | replay pycache defect causes bundle validation FAIL | High | High | Fix in Lane 1B (sys.dont_write_bytecode + exclusion filter) |
| R44-R05 | FODT block_count=None causes smoke to falsely pass | Medium | High | Assert paragraphs > 0 AND headings detected in Lane 2C |
| R44-R06 | G11-G approval not granted this sprint | Certain | Accepted | Gate 11 requires human approval; out of scope for R44 |
| R44-R07 | Gate 8 security review not completed this sprint | Certain | Accepted | Human approval required; out of scope for R44 |
