# R118 Lane Ownership

**Sprint:** FORMAT-FACTORY-UNIFIED-POC-AUTHORITY-RECONCILIATION-R118-001

| Lane | Group | Title | Owner | Status |
|------|-------|-------|-------|--------|
| A | 1 | Terminal verdict contradiction audit | Evidence review supervisor | CLOSED_VERIFIED |
| B | 2 | Evidence manifest and artifact count repair | Evidence materialization auditor | CLOSED_VERIFIED |
| C | 2 | Raw logs, tests, totals reconciliation | Test evidence supervisor | CLOSED_VERIFIED |
| D | 3 | Export/dogfood policy audit | Export target authority supervisor | CLOSED_VERIFIED |
| E | 4 | Proof graph verification | RCA/proof-graph supervisor | CLOSED_VERIFIED |
| F | 4 | Supervisor verdict packet repair | Supervisor packet lead | CLOSED_VERIFIED |
| G | 5 | Path-only grading repair | Supervisor grading engineer | CLOSED_VERIFIED |
| H | 6 | Corrected POC readiness decision | Release-readiness classifier | CLOSED_VERIFIED |
| I | 7 | Final adversarial IV + evidence closeout | IV supervisor | CLOSED_VERIFIED |

## File-Path Rules

- **Writes allowed:** `reports/unified-poc-authority-reconciliation-r118/**`, `.local/evidences/unified-poc-authority-reconciliation-r118/**`
- **Supervisor tools:** `tools/supervisor/**` (tested fixes only)
- **Test additions:** `tests/supervisor/**` only
- **No source edits:** `src/net/**`, `src/python/**`, `tests/net/**`, `tests/python/**`
- **No authority mutation:** `product-capability-matrix/poc-targets.yaml`, `registry/format-registry.yaml`
