# Lane Ownership

## 10 Lanes

| Lane | Name | Owner | Description |
|------|------|-------|-------------|
| C0 | Preflight | Worker | Read authority files, capture git status |
| C1 | Plan Healing | Worker | Normalize plan from ZIP-first to directory-first |
| C2 | Schemas | Worker | Create JSON schemas for declaration/manifest/grading |
| C3 | Tools | Worker | Implement supervisor tools (validate, inspect, grade, prompt, cycle) |
| C4 | Regression Repair | Worker | Fix R85 quality regressions in existing tools |
| C5 | Policy | Worker | Update policies.yaml, product-factory targets |
| C6 | State Sync | Worker | Memory sync, config updates |
| C7 | Tests | Worker | Write and run tests |
| C8 | Demo | Worker | Run demo with synthetic evidence directory |
| C9 | Evidence | Worker | Create final evidence directory and self-declaration |

## Lane-to-Taskcard Mapping

| Lane | Taskcards |
|------|-----------|
| C0 | TC-SUP-DIR-001 |
| C1 | TC-SUP-DIR-002 |
| C2 | TC-SUP-DIR-003, TC-SUP-DIR-004 |
| C3 | TC-SUP-DIR-005, TC-SUP-DIR-006, TC-SUP-DIR-007, TC-SUP-DIR-008, TC-SUP-DIR-009 |
| C4 | TC-SUP-DIR-010 |
| C5 | TC-SUP-DIR-011 |
| C6 | TC-SUP-DIR-012 |
| C7 | TC-SUP-DIR-013 |
| C8 | TC-SUP-DIR-014 |
| C9 | TC-SUP-DIR-015 |

## Lane Dependencies

```
C0 (preflight) -> C1 (plan) -> C2 (schemas) -> C3 (tools) -> C7 (tests) -> C8 (demo) -> C9 (evidence)
                                                    |
                                               C4 (regression) [parallel]
                                               C5 (policy) [parallel]
                                               C6 (state sync) [parallel]
```

C4, C5, C6 can execute in parallel with C3 but must complete before C9.
