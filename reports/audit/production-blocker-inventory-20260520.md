# Production Blocker Inventory

**Sprint:** FORMAT-FACTORY-MEGA-CLOSURE-R35-R36-AND-PRODUCTION-AUTHORITY-STABILIZATION-001
**Lane:** B (Production Blocker Inventory)
**Date:** 2026-05-20

---

## 1. Gate 11 (G11-G Human Approval)

| Format | G11-G Status | Blocker? | Notes |
|--------|-------------|----------|-------|
| FODS | NOT_STARTED | YES | Requires Babar Raza approval per GOVERNANCE.md 26.8 |
| FODT | NOT_STARTED | YES | Requires Babar Raza approval per GOVERNANCE.md 26.8 |

**Classification: HARD_BLOCKER** — No format can reach commercial_product_ready without G11-G.

---

## 2. commercial_product_ready

| Check | Result |
|-------|--------|
| Any format with `commercial_product_ready: true` | NO (0/22) |
| FODS C-level | C4-C6-vertical-slice |
| FODT C-level | C4-C6-vertical-slice |
| All others | Below C4 |

**Classification: HARD_BLOCKER** — Blocked by G11-G and C7+ capability requirements.

---

## 3. Gate Overclaim (R36 Corrections)

| Format | Previous Claimed | Evidence-Backed | Corrected? |
|--------|-----------------|-----------------|------------|
| FODP | G10 | G4 (probe_only) | YES (R36) |
| FODG | G10 | G4 (probe_only) | YES (R36) |
| Gnumeric | G10 | G4 (probe_only) | YES (R36) |
| ABW | G10 | G4 (probe_only) | YES (R36) |

**Classification: RESOLVED** — All overclaims corrected in R36 (d51d4a4).

---

## 4. Scope Finalization (R36)

| Format | Scope | Binary Status | Finalized? |
|--------|-------|---------------|------------|
| XCF | header_and_metadata_only | pixel decode not implemented | YES (R36) |
| PPM | read_only_ascii_p3 | P6 not_implemented | YES (R36) |
| PGM | read_only_ascii_p2 | P5 not_implemented | YES (R36) |
| PBM | read_only_ascii_p1 | P4 not_implemented | YES (R36) |

**Classification: RESOLVED** — Honest scope boundaries documented.

---

## 5. Gate 8 Security Reviews (Awaiting Human)

| Format | G8 Packet Ready | Human Approved | Blocker? |
|--------|----------------|----------------|----------|
| ODS | YES (R30) | NO | YES |
| ODT | YES (R30) | NO | YES |
| QOI | YES (R30) | NO | YES |
| XCF | YES (R30) | NO | YES |
| DIF | YES (R30) | NO | YES |
| PPM | YES (R30) | NO | YES |

**Classification: SOFT_BLOCKER** — Packets ready, awaiting human review per DEC-034.

---

## 6. Generated Requirements Provenance

| Format | Requirements Generated | Verifier Reviewed | IV Accepted |
|--------|----------------------|-------------------|-------------|
| FODS | YES (R22, 23 reqs) | YES (verifier-review.yaml) | PENDING |
| FODT | YES (R22, 24 reqs) | YES (verifier-review.yaml) | PENDING |
| ODS-PPM | NO | N/A | N/A |

**Classification: SOFT_BLOCKER** — FODS/FODT requirements generated and verifier-reviewed but awaiting formal IV acceptance. No requirements exist for Gate 8+ candidates.

---

## 7. Skill System Format Genericity

| Issue | Severity | Status |
|-------|----------|--------|
| `--format all` only iterates FODS/FODT | MEDIUM | DOCUMENTED (Lane H audit) |
| commercial_sprint.py rejects non-FODS/FODT | LOW | HONEST_LIMITATION |
| FODT-REQ-040 hardcoded in prompt generator | LOW | INTENTIONAL_DEFAULT |

**Classification: TECH_DEBT** — Hardening plan created, not a production blocker.

---

## 8. ZPAQ Gate 3 Blocked

| Issue | Status |
|-------|--------|
| ZPAQ Gate 3 requires zpaq CLI | BLOCKED |
| ZPAQL VM complexity score 6.2/10 | REVIEW_BAND |

**Classification: DEFERRED** — Not on critical path.

---

## 9. .NET FOSS Packaging (DEC-033)

| Decision | Status |
|----------|--------|
| DEC-033: .NET Commercial Only | RESOLVED (Babar Raza 2026-05-12) |
| .NET FOSS packaging | DEFERRED indefinitely |

**Classification: RESOLVED_BY_DECISION** — No blocker.

---

## 10. Evidence Contract Schema

| Check | Status |
|-------|--------|
| All contracts use required_repo_files | YES (R34 migration) |
| Zero contracts use required_artifacts | YES (239 guard tests) |
| All sprint contracts meet floor 30 | YES (R34 normalization) |

**Classification: RESOLVED** — Schema migration complete.

---

## Summary

| Category | Count | Classification |
|----------|-------|---------------|
| Hard blockers | 2 | G11-G approval, commercial_product_ready |
| Soft blockers | 2 | G8 human review (6 formats), requirements IV |
| Resolved | 3 | Gate overclaim, scope finalization, contract schema |
| Tech debt | 1 | Skill system genericity |
| Deferred | 2 | ZPAQ, .NET FOSS |

## VERDICT: LANE_B_PASS_INVENTORY_COMPLETE
