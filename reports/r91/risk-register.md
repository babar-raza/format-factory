---
sprint: R91
generated_by: r91-worker
---

# R91 Risk Register

| ID | Risk | Severity | Status | Mitigation |
|----|------|----------|--------|------------|
| R1 | Inherited 12 failures block `autonomous_continue` | MEDIUM | CLASSIFIED | Repair lane added (Train C). Failures are pre-existing and non-R91-introduced. Classified before execution so they do not block R91 product work grading. |
| R2 | .NET product work needs governed skill | LOW | MITIGATED | Skills exist in `.supervisor/skill-registry.yaml`: `/add-dotnet-api`, `/add-dogfood-export`. All .NET changes go through governed skill invocations. |
| R3 | Supervisor grading not yet item-by-item | HIGH | ADDRESSED | Trains D and V implement per-item grading. Output: `reports/supervisor/work-item-grades.md` + `work-item-grades.json`. Per-item grades enable rework lanes in next-sprint. |
| R4 | Context drift between sprints | MEDIUM | ADDRESSED | Context pack definition created in Train K. Next-sprint generator updated (Train E) to embed context pack in generated sprint prompt. |
| R5 | Evidence metadata cosmetics stalling product | LOW | PROHIBITED | Explicitly prohibited. Review package shallowness (D91-02) is deferred as EVIDENCE_COSMETIC_DEFER. Product work takes priority over cosmetic evidence improvements. |

## Risk Thresholds

- **HIGH**: Must be addressed before product work begins (Group 1 trains)
- **MEDIUM**: Must be classified/mitigated before closeout
- **LOW**: Noted, monitored, deferred if cosmetic

## R1 Detail — Inherited Failure Classification

The 12 inherited failures are:

| Count | Source | Class |
|-------|--------|-------|
| 5 | `test_auto_proof` — R84 sidecar | PRE_EXISTING |
| 1 | `test_r28` — R88 contract | PRE_EXISTING |
| 2 | `test_r84` — R84 review package | PRE_EXISTING |
| 3 | Cross-layer invariants | PRE_EXISTING |
| 1 | Stale package count | PRE_EXISTING |

None were introduced by R90 or R91 work. Classification confirmed in `reports/r91/r90-independent-verification.md`.
