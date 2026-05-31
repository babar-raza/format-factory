# R83 Risk Register

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| R1: Wrong artifact uploaded again (inner bundle vs review package) | HIGH | CRITICAL | Automated selector test that rejects inner bundle; final response must say UPLOAD PRIMARY ARTIFACT: |
| R2: PENDING metadata in bundle | HIGH | HIGH | All metadata files finalized before bundle build |
| R3: State snapshot after bundle build | MEDIUM | HIGH | Run state_snapshot.py before bundle build; verify |
| R4: FODS/FODT workflow fails from extracted review package | MEDIUM | HIGH | Test extraction to temp dir first |
| R5: build_supervisor_review_package.py missing required component | MEDIUM | HIGH | Test all required components present before running |
| R6: Package artifacts not in review package | MEDIUM | HIGH | Validate package-artifacts/ in ZIP before finalizing |
| R7: sidecar not in review package | MEDIUM | HIGH | Copy sidecar to temp location; include in review package |
| R8: master-plan.md not updated | LOW | MEDIUM | Train U runs before bundle build |
| R9: Test failures from new R83 tests | LOW | MEDIUM | Fix tests before committing |
| R10: .NET tests fail due to concurrent access | LOW | LOW | Run .NET tests sequentially |
