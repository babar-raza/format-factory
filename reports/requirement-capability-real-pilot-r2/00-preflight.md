# RCA Real Pilot R2 — Preflight
# Sprint: FORMAT-FACTORY-REQUIREMENT-CAPABILITY-AUTHORITY-LAYER-REAL-PILOT-R2-001

## Python Resolver
```
PYTHON=.local/venv/Scripts/python
Resolved: .local/venv/Scripts/python (Python 3.13.2)
```

## Git State
```
HEAD: 3a86a05295cb4b82ed40a3408b0612a90f93643c
Branch: main
Dirty: yes (pre-existing M-tagged .claude/commands/ and supervisor files from R93+R1;
       untracked sprint reports — classified NON_BLOCKING_SPRINT_ARTIFACTS)
```

## Governance Reads
- CLAUDE.md: READ — no push, no gate approval, no commit without authorization
- AGENTS.md: READ (if present) — MODE EXECUTION, no self-approval, no push
- reports/supervisor/session-resume.md: READ — Last sprint RCA-R1 ACCEPTED, Autonomous Continue: True
- poc-targets.yaml: READ (read-only) — FODS/FODT/Netpbm COMMERCIAL_NET, ZST/DIF/SYLK FOSS_REDUCED
- reports/supervisor/approval-gates.md: autonomous-continue YES

## R1 Package Review
- Sprint: FORMAT-FACTORY-REQUIREMENT-CAPABILITY-AUTHORITY-LAYER-REAL-PILOT-R1-001
- autonomous-cycle exit: 0 (8/8 ACCEPTED)
- overall_verdict: ACCEPTED
- evidence_quality_score: 0.12 (1/8 verified — ACCEPTED_VERIFIED)
- anti-skip violations: 2 (missing_raw_logs MEDIUM, missing_sample_outputs LOW)
- Review package SHA-256: b57b21c55fee4b13be6232e780af79301aeb6c7303552d15fbd8955efd29986b

## Spec Authority R3 Input Snapshot
- snapshot_id: SAL-RCA-SNAPSHOT-R2R3-001
- Status: FROZEN_FOR_RCA_INPUT (rca_ready=true)
- FODT: NOW spec-backed (ACCEPTED_WITH_CAVEAT — ODF 1.3 scoped intro, Spec R3)
- FODS: ACCEPTED_WITH_CAVEAT (ODF 1.3 scoped intro)
- ZST: ACCEPTED_SPEC (RFC 8878 real fetch)
- Netpbm: ACCEPTED_WITH_CAVEAT (de facto public domain)
- DIF: EMPIRICAL_ONLY (no public spec, MUST NOT promote)

## R2 Allowed Write Paths
- reports/requirement-capability-real-pilot-r2/**
- .local/evidences/requirement-capability-real-pilot-r2/**
- tests/requirement_capability_authority/** (R2 tests)
- tools/requirements_authority/** (small tested fixes only)

## Prohibitions Affirmed
- No git push
- No poc-targets.yaml mutation
- No registry mutation
- No src/net/** or src/python/** edits
- No tests/net/** or tests/python/** edits
- No Spec Authority evidence mutation
- No ai_draft as proof
- No routing architecture-blocked export gaps to Mainstream-Dogfood
- No /add-dogfood-export for missing target writer claims
