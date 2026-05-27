# R67 Risk Register

Sprint: FORMAT-FACTORY-R67-CLEAN-LOCAL-RC-PACKAGE-REPLAY-FINALITY-WORKAHEAD-MEGA-TRAIN-001

| Risk | Probability | Impact | Mitigation |
|---|---|---|---|
| Artifact rebuild churn after freeze | Low | High | No source changes after wheel rebuild |
| Validator check false positive | Medium | Medium | Test validators with synthetic fixtures |
| Sprint-id.txt not in older bundles | Low | Low | Backward compat: no sprint-id.txt allows any run |
| Wheel import shadowing (csv/src) | Low | Medium | Use PROJECT_ROOT not src/python in sys.path |
| INV-003 fails due to missing reports | High | Low | All required reports created before evidence build |
| PENDING tokens in new metadata | Low | High | Verify manifests before bundle build |
