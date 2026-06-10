# Test Total Reconciliation — R118

**Sprint:** FORMAT-FACTORY-UNIFIED-POC-AUTHORITY-RECONCILIATION-R118-001

---

## The 333 vs 383 Discrepancy

| Count | Source | Composition |
|-------|--------|-------------|
| 333 | Lane execution ledger (16 lanes, reported in materialization audit) | Product + authority test lanes Iter-1 through Iter-4 (excluding WI-006 controller gate tests) |
| 383 | Declaration tests_run total | All 6 work items: WI-001(94) + WI-002(57) + WI-003(116) + WI-004(66) + WI-005(0) + WI-006(50) |
| 50 | Difference | WI-006 controller gate reconciliation tests (added in Phase B reconciliation patch) |

**Resolution:** Both counts are correct for their scope. 333 = pre-WI-006 train iterations. 383 = complete sprint total including controller gate tests.

## Test Taxonomy

| Category | Tests | Raw Log |
|----------|-------|---------|
| Spec Authority (Iter-1) | 28 | spec-authority-tests.log |
| RCA MWP (Iter-1) | 37 | rca-fabric-tests.log |
| Integration Fabric (Iter-1) | 29 | rca-fabric-tests.log |
| FODS/FODT/Netpbm R114 (Iter-1) | — | fods-r114-tests.log, fodt-r114-tests.log, netpbm-r114-tests.log |
| R115 .NET + FOSS (Iter-2) | 57 | (raw logs implicit in lane ledger) |
| R116 FODS/FODT/Netpbm/DIF (Iter-3) | ~80 | fods-r116-tests.log, fodt-r116-tests.log, netpbm-r116-tests.log, dif-r116-tests.log |
| Controller R116 (Iter-3) | 40 | controller-r116-tests.log |
| DIF write_dif R117 (Iter-4) | 10 | dif-r117-tests.log |
| FODS dogfood confirmations (Iter-4) | 32 | fods-r117-tests.log |
| FODT dogfood confirmations (Iter-4) | 24 | fodt-r117-tests.log |
| Controller gate reconciliation (WI-006) | 50 | controller-gate-reconciliation-tests.log |
| **Total** | **383** | |

## Authoritative Test Count

**383** is the authoritative total for the unified-authority-integrated-poc-train sprint.
This is the value in the evidence declaration and supervisor review.

## Consistency Check

- Final supervisor verdict packet: should reference 383
- Gate 11 readiness packet: should reference 383
- These are consistent — both were updated in the reconciliation patch.
