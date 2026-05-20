# R35 Lane Ownership and Overlap Matrix

| Lane | Owner | Files | Overlaps |
|------|-------|-------|----------|
| 0 (Coordinator) | AI | All | - |
| A (Separation verification) | AI | reports/ | None |
| B (Schema fix) | AI | tools/ai/run_ai_checks.py | C, E |
| C (Validator integration) | AI | tools/ai/run_ai_checks.py | B |
| D (Contract cleanup) | AI | tools/evidence/contracts/r33-*.yaml | None |
| E (Runner closure) | AI | tools/ai/run_ai_checks.py | B, C |
| F (Fail-closed live) | AI | tools/ai/pipeline/e2e_pilot.py | G |
| G (Contradiction required) | AI | tools/ai/run_ai_checks.py | F |
| H (Citation visibility) | AI | tools/ai/pipeline/e2e_pilot.py | F |
| I (Telemetry minimization) | AI | tools/ai/telemetry/artifacts.py | None |
| J (Runner contract) | AI | tools/ai/run_ai_checks.py | B, C, E |
| K (Matrix v3) | AI | docs/ai/ai-system-verification-matrix.md | None |
| L (Tests) | AI | tests/ai/test_r35_*.py | All |
| M (Full validation) | AI | - | All |
| N (IV) | AI | reports/verification/ | None |
| O (Adversarial) | AI | reports/governance/ | None |
