# R45 Risk Register

**Sprint:** FORMAT-FACTORY-R45-TWO-PRODUCT-LOCAL-RC-REPLAYABLE-001

## Active Risks

| ID | Risk | Likelihood | Impact | Mitigation |
|----|------|-----------|--------|------------|
| R45-RR-001 | .NET consumer project requires dotnet CLI with local NuGet source | HIGH | HIGH | Use dotnet add source + dotnet run with local feed |
| R45-RR-002 | state_snapshot.py UTF-8 fix breaks existing state tests | LOW | MEDIUM | Run tests/state/ after fix; em dash test needed |
| R45-RR-003 | Package artifacts exceed bundle size limit | LOW | LOW | .whl files are ~10KB each; negligible |
| R45-RR-004 | pytest-timeout conftest.ini setting conflicts with auto-proof | LOW | MEDIUM | Set only for non-auto-proof suites; auto-proof has its own timeout |
| R45-RR-005 | Validator extension for LOCAL_RC breaks existing PASS bundles | LOW | HIGH | Only tighten — new check added, existing logic unchanged |

## Resolved Risks (From R44)

| ID | Risk | Resolution |
|----|------|-----------|
| R44-RR-001 | pycache in replay bundle | CLOSED — _should_exclude() + dont_write_bytecode |
| R44-RR-002 | FODT blocks=0 false-pass | CLOSED — explicit blocks >= 1 assertion |
| R44-RR-003 | NuGet missing readme warning | CLOSED — PackageReadmeFile added |
