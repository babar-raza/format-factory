# R82 Risk Register

| ID | Risk | Severity | Mitigation |
|----|------|----------|------------|
| RR-R82-001 | Wheel build fails for some packages | HIGH | Build all 10; fail-fast with exact error |
| RR-R82-002 | Installed-wheel tests break with new fail-closed behavior | HIGH | Update skip logic to fail for package-ready verdict only |
| RR-R82-003 | pycache validator breaks existing test suite | MEDIUM | Use bundle-only check, not source tree check |
| RR-R82-004 | FODT roundtrip fails from installed wheel | MEDIUM | Test separately; downgrade FODT status honestly if fails |
| RR-R82-005 | ZST dependency blocks test count (9 failures) | LOW | Already classified; use pytest.mark.skip with reason |
| RR-R82-006 | .NET SDK path issue on Windows | LOW | Report exact blocker; do not skip R82 for .NET |
| RR-R82-007 | Supervisor review package exceeds upload size | LOW | Exclude raw log binaries >10MB |
| RR-R82-008 | R82 contract required_repo_files checker fires on R83 planning | MEDIUM | Create R82 stubs for all required files before committing |
| RR-R82-009 | repro tool fix breaks existing repro tests | MEDIUM | Update tests to use correct namespace |
| RR-R82-010 | Evidence bundle build fails due to pycache check | HIGH | Ensure .gitignore excludes __pycache__ before build |

RISK_REGISTER: COMPLETE
