# Original Plan Reconciliation

**Sprint:** FORMAT-FACTORY-MEGA-CLOSURE-R35-R36-AND-PRODUCTION-AUTHORITY-STABILIZATION-001
**Lane:** J (Plan Reconciliation)
**Date:** 2026-05-20

---

## 1. Original Plan vs Current State

Source: `plans/master-plan.md` (single operational authority)

### 1.1 Three Product Tracks

| Track | Plan | Current | Status |
|-------|------|---------|--------|
| Python FOSS | src/python/{format}/ | 12 parsers implemented | ON_TRACK |
| .NET Commercial | src/net/{format}/ | FODS/FODT C4-C6 vertical slice | ON_TRACK |
| Acquisition Layer | acquisition-packs/ | 22 formats registered | ON_TRACK |

### 1.2 11-Gate Pipeline

| Gate | Plan | Current | Status |
|------|------|---------|--------|
| G1-3 (Acquisition) | All candidates pass | 22 formats at G1+, 4 at G3+ | ON_TRACK |
| G4-7 (Prototype) | Evidence-backed progression | FODS/FODT G10, 6 formats G7, 3 at G7 | ON_TRACK |
| G8-10 (Production) | Security review + readiness | 6 G8 packets ready, awaiting human | ON_TRACK |
| G11 (Release) | Human approval required | NOT_STARTED for all | ON_TRACK (by design) |

### 1.3 Evidence System

| Component | Plan | Current | Status |
|-----------|------|---------|--------|
| Evidence contracts | YAML-based | 20+ contracts, all using required_repo_files | ON_TRACK |
| Bundle builder | Automated | tools/evidence/build_evidence_bundle.py | COMPLETE |
| Bundle validator | Automated | tools/evidence/validate_evidence_bundle.py | COMPLETE |
| Clean git requirement | Mandatory | require_clean_git: true enforced | COMPLETE |
| Metadata floor | >= 30 | All sprint contracts meet floor | COMPLETE |

### 1.4 AI Platform

| Component | Plan (Section 39) | Current | Status |
|-----------|-------------------|---------|--------|
| Type A: Agentic | Claude/Codex high-risk, Qwen2 low-risk | Implemented, governed | ON_TRACK |
| Type B: Synthesis | GPT-OSS gateway | Implemented, fixture-mode proven | ON_TRACK |
| Type C: Embeddings | LanceDB format-segregated | Schema designed, not yet live | PLANNED |
| Control plane | Model discovery + routing | Phase 2 complete (202+ tests) | ON_TRACK |
| Risk register | 40 items | docs/ai/ai-risk-register.md | COMPLETE |

---

## 2. Deviations from Plan

### 2.1 Positive Deviations (Ahead of Plan)

| Area | Expected | Actual | Impact |
|------|----------|--------|--------|
| Format count | ~10 by R30 | 22 registered | +12 candidates ahead of schedule |
| AI test count | ~100 | 588 | Significantly deeper coverage |
| Evidence hardening | Basic | 239 contract migration tests + 284 evidence guards | Far exceeds plan |
| Gate corrections | Not planned | R36 corrected 4 overclaimed formats | Governance improvement |

### 2.2 Neutral Deviations

| Area | Expected | Actual | Impact |
|------|----------|--------|--------|
| .NET FOSS packaging | Parallel track | DEC-033 deferred | Reduced scope, correct decision |
| Sprint cadence | Weekly | ~daily R-series | Faster iteration, more evidence |

### 2.3 Negative Deviations (Behind Plan)

| Area | Expected | Actual | Gap |
|------|----------|--------|-----|
| G11 approval | At least FODS by R30 | NOT_STARTED | Blocked on human review |
| G8 security reviews | Approved by R32 | 6 packets PENDING | Blocked on human review |
| IV acceptance of requirements | Done by R28 | PENDING | Blocked on DEC-034 |
| Skill system genericity | Format-generic | FODS/FODT hardcoded | Tech debt (plan exists) |
| ZPAQ | G3+ by R28 | G3 BLOCKED | CLI dependency |

---

## 3. Risk Assessment

| Risk | Severity | Mitigation |
|------|----------|------------|
| G11 never approved | HIGH | All evidence ready; requires human scheduling |
| G8 reviews delayed | MEDIUM | Packets complete; no technical blocker |
| Requirements IV stalled | LOW | Provenance intact; can be done any time |
| Skill system limits expansion | LOW | Hardening plan created (Lane H) |

---

## 4. Plan Integrity Check

| Check | Result |
|-------|--------|
| master-plan.md is single operational authority | CONFIRMED |
| No competing plan documents | CONFIRMED |
| AGENTS.md consistent with plan | CONFIRMED |
| GOVERNANCE.md consistent with plan | CONFIRMED |
| format-registry.yaml reflects plan decisions | CONFIRMED |
| DEC-031/032/033/034 all documented and enforced | CONFIRMED |

---

## 5. Recommendations

1. **Schedule G11-G review session** — All FODS/FODT evidence is ready
2. **Schedule G8 security review** — 6 format packets have been waiting since R30
3. **Run IV acceptance sprint** — FODS/FODT requirements provenance is complete
4. **Execute skill system Phase 1** — ~110 lines, low risk, high value
5. **Attempt ZPAQ G3** — Requires zpaq CLI installation

---

## VERDICT: LANE_J_PASS_PLAN_RECONCILED

The project is broadly on track with the original plan. The 11-gate pipeline is functioning as designed. Evidence system exceeds planned rigor. The primary gaps are human-approval bottlenecks (G11, G8, IV), not technical deficits. No plan integrity violations detected.
