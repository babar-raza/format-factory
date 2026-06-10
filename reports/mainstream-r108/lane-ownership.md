# R108 Lane Ownership

| Lane | Owner | Bounded Files | Status |
|------|-------|---------------|--------|
| A | Evidence supervisor | reports/mainstream-r108/r107-regrading.* | READY |
| B | Ledger supervisor | reports/mainstream-r108/source-ledger-*, git-state-proof.md | READY |
| C | FODS product agent | src/net/fods/FodsDocument.cs, tests/net/fods/FodsR108* | READY |
| D | FODT product agent | src/net/fodt/FodtDocument.cs, tests/net/fodt/FodtR108* | READY |
| E | Netpbm product agent | src/net/netpbm/Model/NetpbmImage.cs, tests/net/netpbm/NetpbmR108* | READY |
| F | FOSS product agent | tests/python/*/test_r108_* | READY |
| G | Dogfood supervisor | tests/net/*/R108Dogfood*, tests/python/*/test_r108_*dogfood* | READY |
| H | Package supervisor | reports/mainstream-r108/package-install-proof.md | READY |
| I | Planning supervisor | reports/mainstream-r108/fresh-mainstream-gaps.md | READY |
| J | IV supervisor | reports/mainstream-r108/final-adversarial-independent-verification.md | LAST |

## Overlap Check
- Lanes C, D, E each own distinct source files — no overlap.
- Lane F owns only Python test files — no overlap with C/D/E.
- Lane G may create .NET dogfood tests referencing same source but only reads src/.
- Coordinator serializes ledger updates after each product lane completes.
