# R32 — Truth Matrix, Gate Quality, and Drift Recovery

**Sprint:** FORMAT-FACTORY-R32-TRUTH-MATRIX-GATE-QUALITY-AND-DRIFT-RECOVERY-001
**Date:** 2026-05-19
**Type:** Non-feature governance/policy sprint
**Preceding:** R32 state-drift investigation verdict: PROJECT_HAS_SEVERE_DRIFT_RECOVERY_REQUIRED

---

## What happened

R32 converted the state-drift investigation findings into durable repo governance artifacts. No source code was modified, no gates advanced, no files moved.

## Key findings accepted

1. Only 3 of 22 formats are production_track_real (FODS, FODT, ZST)
2. 4 formats (FODP, FODG, Gnumeric, ABW) have overclaimed gates (G10 with probe-quality source)
3. AI platform is control_plane_only — not wired into acquisition pipeline
4. Gate criteria did not distinguish probe from library
5. Sprint incentives rewarded gate count over source depth

## Artifacts created

### Policies (docs/)
- `gate-quality-criteria.md` — G1-G11 minimum source/test/evidence requirements
- `prototype-quarantine-policy.md` — promotion rules and quarantine markers
- `source-track-maturity-policy.md` — quality tiers for Python FOSS / .NET commercial
- `format-feature-matrix-template.md` — per-format feature checklist template
- `format-completion-matrix.md` — human-readable summary

### Matrix (registry/)
- `format-completion-matrix.yaml` — canonical truth matrix for all 20+ formats

### Taskcards (taskcards/)
- 7 DRIFT-* overclaim review taskcards (FODP, FODG, Gnumeric, ABW, XCF, PPM, PGM/PBM)
- 7 DEEPEN-* / COMMERCIAL-* deepening taskcards (ODS, ODT, QOI, DIF, SYLK, ZST, FODS/FODT)

### Evidence validators (tests/evidence/)
- `test_format_completion_matrix.py` — matrix integrity and completeness
- `test_gate_quality_claims.py` — gate claims vs source evidence
- `test_source_track_maturity.py` — maturity class consistency

### Reports (reports/r32/)
- `ai-wiring-reality-and-decision-report.md`
- `truth-matrix-gate-quality-and-drift-recovery-report.md`
- `preflight-and-lane-ownership.md`
- `final-verdict.md`

## Key decisions

1. **AI paused:** AI investment stays out of main productization until gate/matrix recovery completes
2. **No physical moves:** Code stays in src/python/ but maturity class flags true state
3. **Gate criteria redesigned:** G10 now requires write/export/roundtrip or approved read-only scope
4. **Completion matrix is new authority:** Future agents must check matrix before advancing gates

## What this sprint did NOT do
- Did not change any gate states in pack.yaml or registry
- Did not move or delete source files
- Did not modify AI code
- Did not advance any format
- Did not approve commercial readiness

## Next recommended sprint
R33: Format deepening sprint focused on ODS and QOI (add write capability), with overclaim review for FODP/FODG/Gnumeric/ABW.
