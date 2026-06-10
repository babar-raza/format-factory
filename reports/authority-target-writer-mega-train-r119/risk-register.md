# Risk Register
Sprint: FORMAT-FACTORY-AUTHORITY-LAYERS-AND-TARGET-WRITER-MEGA-TRAIN-R119-001

| ID | Risk | Likelihood | Impact | Mitigation | Status |
|----|------|-----------|--------|-----------|--------|
| R01 | .NET build fails for new tests | LOW | HIGH | Writers already built and tested | MITIGATED |
| R02 | FODS/FODT regression from source changes | LOW | HIGH | No new source changes planned (verify only) | MITIGATED |
| R03 | Gap queue test fails due to module import | MEDIUM | MEDIUM | Run in tools/supervisor sys.path context | WATCH |
| R04 | Evidence quality still low after repairs | MEDIUM | MEDIUM | Populate tests_supporting field in declaration | WATCH |
| R05 | HTML writer not wired to FODS exporter | KNOWN | LOW | Documented as separate sprint, not overclaimed | ACCEPTED |
| R06 | Markdown/TXT not wired to FODT exporter | KNOWN | LOW | Documented as separate sprint, not overclaimed | ACCEPTED |
| R07 | anti-skip detector still misses some artifacts | MEDIUM | LOW | Add targeted test; caveated in lane verdict | WATCH |
| R08 | autonomous-cycle exit != 0 | LOW | HIGH | Populate all required YAML fields correctly | WATCH |
