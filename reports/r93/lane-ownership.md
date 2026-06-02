---
sprint: R93
generated_by: r93-worker
---

# R93 Lane Ownership Matrix

Sprint: FORMAT-FACTORY-R93-CONTEXT-PACK-SUPERVISOR-MCP-ACCELERATION-POC-PARALLEL-MEGA-TRAIN-001

## Lane Assignments

| Lane | Owner | Trains | Files |
|------|-------|--------|-------|
| C1 | Governance | A | reports/r93/00-preflight.md, reports/r93/r92-declaration-review-package-verification.md |
| C2 | Supervisor | B, C, D, E, F | tools/supervisor/*.py, .supervisor/*.yaml, reports/supervisor/ |
| C3 | Acceleration | G, H, I, J | .claude/commands/*.md, reports/r93/acceleration-*.md, tools/supervisor/validate_product_code_ledger.py |
| C4 | .NET Product | K, L, M | src/net/**/*.cs, tests/net/**/*.cs, reports/r93/*-dotnet-*.md |
| C5 | FOSS Product | N, O, P | src/python/**/*.py, tests/python/**/*.py, reports/r93/*-foss-*.md |
| C6 | Dogfood/Package | Q, R, S | src/python/**/*, tests/python/**/*, examples/, reports/r93/*-dogfood-*.md |
| C7 | Next Sprint | T, U | reports/supervisor/*, reports/r93/continuation-*.md |
| C8 | State Sync | V | .supervisor/project-memory.md, product-capability-matrix/poc-targets.yaml |
| C9 | Adversarial IV | W | reports/r93/final-adversarial-independent-verification.md |

## File Ownership Rules

- `src/net/**/*.cs`: C4 only (governed via /add-dotnet-api skill)
- `src/python/**/*.py`: C5 or C6 (governed via /add-python-api or /add-dogfood-export)
- `reports/supervisor/`: C2 and C7
- `tools/supervisor/*.py`: C2 only
- `.supervisor/*.yaml`: C2 and C8
- `tests/net/**`: C4 only
- `tests/python/**`: C5 or C6
- `reports/r93/**`: any lane (own train reports only)
- `reports/r90/product-code-change-ledger.json`: C4, C5, C6 (must add entries for any src change)

## Hard Prohibitions (all lanes)

- git push (requires explicit user authorization)
- git commit (requires explicit user authorization)
- Gate 8, Gate 11 approval (requires Babar Raza)
- PyPI/NuGet publication
- MCP activation changes

## Status: LANE OWNERSHIP LOCKED
