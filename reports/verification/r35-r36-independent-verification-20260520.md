# R35/R36 Independent Verification

**Sprint:** FORMAT-FACTORY-MEGA-CLOSURE-R35-R36-AND-PRODUCTION-AUTHORITY-STABILIZATION-001
**Lane:** A (R35/R36 Verification)
**Date:** 2026-05-20
**Verifier:** Independent agent (separate session)

---

## 1. Commit Existence

| Check | SHA | Result | Evidence |
|-------|-----|--------|----------|
| R35 commit exists | 27ba09a | PASS | `fix(governance): establish clean recovery baseline and execute gate corrections` |
| R36 commit exists | d51d4a4 | PASS | `fix(governance): establish clean recovery baseline and execute gate corrections` |

---

## 2. Gate 11 Not Approved

| Check | Result | Evidence |
|-------|--------|----------|
| FODS G11-G remains NOT_STARTED | PASS | format-registry.yaml line 209: "G11-G human approval NOT_STARTED" |
| FODT G11-G remains NOT_STARTED | PASS | format-registry.yaml line 421: "G11-G human approval NOT_STARTED" |
| No self-approval of G11 in R35 final verdict | PASS | R35 safety proof: "No G11-G approved" |
| No self-approval of G11 in R36 final verdict | PASS | R36 safety proof: "No G11-G approved" |

---

## 3. commercial_product_ready Remains False

| Check | Result | Evidence |
|-------|--------|----------|
| Zero instances of `commercial_product_ready: true` in format-registry.yaml | PASS | Grep returned no matches |
| All entries show `commercial_product_ready: false` | PASS | 65 instances of `false` found, zero `true` |

---

## 4. FODP/FODG/Gnumeric/ABW Gate Corrections (probe_only / G4)

| Format | gate_correction present | previous_claimed_gate | evidence_backed_gate | maturity_class | Result |
|--------|------------------------|----------------------|---------------------|----------------|--------|
| FODP | YES (line 773) | G10 | G4 | probe_only | PASS |
| FODG | YES (line 921) | G10 | G4 | probe_only | PASS |
| Gnumeric | YES (line 1068) | G10 | G4 | probe_only | PASS |
| ABW | YES (line 1222) | G10 | G4 | probe_only | PASS |

All four corrections applied in format-registry.yaml with correction_sprint: R36, correction_date: 2026-05-20.

Corresponding format-completion-matrix.yaml entries confirm:
- FODP: actual_maturity_class: probe_only, evidence_backed_gate: "G4 (prototype quality)", overclaim_risk: high
- FODG: actual_maturity_class: probe_only, evidence_backed_gate: "G4 (prototype quality)", overclaim_risk: high
- Gnumeric: actual_maturity_class: probe_only, evidence_backed_gate: "G4 (prototype quality)", overclaim_risk: high
- ABW: actual_maturity_class: probe_only, evidence_backed_gate: "G4 (prototype quality)", overclaim_risk: high

---

## 5. XCF/PPM/PGM/PBM Scope Finalization Entries

| Format | scope_finalization present | scope | binary_status | Result |
|--------|--------------------------|-------|---------------|--------|
| XCF | YES (line 1741) | header_and_metadata_only | pixel decode not implemented | PASS |
| PPM | YES (line 1982) | read_only_ascii_p3 | P6 not_implemented | PASS |
| PGM | YES (line 2055) | read_only_ascii_p2 | P5 not_implemented | PASS |
| PBM | YES (line 2128) | read_only_ascii_p1 | P4 not_implemented | PASS |

All four scope finalizations applied in format-registry.yaml with finalization_sprint: R36, finalization_date: 2026-05-20.

Corresponding format-completion-matrix.yaml entries confirm:
- XCF: actual_maturity_class: probe_only, r35_scope_finalization: "APPLIED"
- PPM: actual_maturity_class: read_only_prototype, r35_scope_finalization: "APPLIED"
- PGM: actual_maturity_class: read_only_prototype (no overclaim)
- PBM: actual_maturity_class: read_only_prototype (no overclaim)

---

## 6. Registry Alignment Guard Tests

| Check | Result | Evidence |
|-------|--------|----------|
| test_r36_registry_alignment_guards.py | 8/8 PASS | `8 passed in 1.89s` |

---

## 7. Report Integrity

| Report | Exists | Internally Consistent | Result |
|--------|--------|----------------------|--------|
| reports/r35/final-verdict.md | YES | Verdict matches test counts, safety proof complete | PASS |
| reports/r35/preflight-and-lane-ownership.md | YES | 12 lanes, clean preflight, HEAD at f7981d3 | PASS |
| reports/r35/probe-format-gate-correction-report.md | YES | 4 corrections + 4 scope finalizations documented | PASS |
| reports/r35/adversarial-review.md | YES | 12/12 checks pass | PASS |
| reports/r36/final-verdict.md | YES | 27 new tests, safety proof complete | PASS |
| reports/r36/preflight-and-lane-ownership.md | YES | HEAD at 27ba09a (R35), clean preflight | PASS |
| reports/r36/adversarial-review.md | YES | 12/12 checks pass | PASS |

---

## 8. R35 Classification

- Reports present and complete: YES
- Gate corrections in pack.yaml: Documented in correction report
- Scope finalizations in pack.yaml: Documented in correction report
- Safety proof: No tools/ai, no tests/ai, no G11-G, no commercial_product_ready: true
- Adversarial review: 12/12 PASS
- **Classification: ACCEPTED_CLEAN**

## 9. R36 Classification

- Reports present and complete: YES
- format-registry.yaml gate_correction sections: 4/4 confirmed
- format-registry.yaml scope_finalization sections: 4/4 confirmed
- format-completion-matrix.yaml synchronized: YES
- Registry alignment guard tests: 8/8 PASS
- Safety proof: No tools/ai, no tests/ai, no G11-G, no commercial_product_ready: true
- Adversarial review: 12/12 PASS
- **Classification: ACCEPTED_CLEAN**

---

## VERDICT: LANE_A_PASS_R35_R36_ACCEPTED

Both R35 (27ba09a) and R36 (d51d4a4) pass independent verification. Gate corrections are evidence-backed, scope finalizations are honest, no governance violations detected, and automated guard tests confirm registry alignment.
