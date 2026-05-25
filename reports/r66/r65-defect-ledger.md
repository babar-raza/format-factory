# R65 Defect Ledger

| ID | Description | Severity | R66 Resolution |
|---|---|---|---|
| IV-R65-001 | Bundled state says R65_IN_PROGRESS | RC-BLOCKING | Train B: final-state ordering |
| IV-R65-002 | Bundled metadata proofs contain placeholders | RC-BLOCKING | Train C: metadata repair |
| IV-R65-003 | Bundled invariants output is stale R23 content | RC-BLOCKING | Train B: fresh invariant output |
| IV-R65-004 | Package artifact manifest truncated hashes | RC-BLOCKING | Train E: full 64-char SHA-256 |
| IV-R65-005 | Dotnet nupkg manifest lacks required fields | RC-BLOCKING | Train E: full manifest |
| IV-R65-006 | Artifact discovery false positive in env-var mode | RC-BLOCKING | Train D: run-number check |
| IV-R65-007 | Sidecar/delivery manifest git_head mismatch | RC-BLOCKING | Train B: build after final commit |
| IV-R65-008 | Delivered ZIP missing final state update | RC-BLOCKING | Train B: correct ordering |
| IV-R65-009 | Build ordering defect (metadata placeholder → ZIP → update) | INFO | Train B: ordering policy |
| IV-R65-010 | Tests validate local files not bundled content | INFO | Train F: delivery final-mode |
