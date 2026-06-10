# Lane Ownership Map
# Sprint: FORMAT-FACTORY-REQUIREMENT-CAPABILITY-AUTHORITY-LAYER-REAL-PILOT-R1-001

| Lane | Owner | Status | Key Outputs |
|------|-------|--------|-------------|
| A | RCA implementation investigator | CLOSED_VERIFIED | layer-implementation-inventory.md, rca-entrypoints.json, subsystem-coverage-matrix.json |
| B | Input snapshot supervisor | CLOSED_VERIFIED | input-snapshot-manifest.md, input-snapshots-manifest.json, spec-input-reliability-table.json |
| C | Evidence importer lead | CLOSED_VERIFIED | evidence-import-report.md, imported-evidence-artifacts.jsonl |
| D | Requirement/claim registry lead | CLOSED_VERIFIED | product-requirements.jsonl, capability-claims.jsonl, claim-registry-report.md |
| E | Proof graph lead | CLOSED_VERIFIED | proof-graph/nodes.jsonl, proof-graph/edges.jsonl, proof-graph/graph-manifest.json |
| F | Coverage evaluator lead | CLOSED_VERIFIED | coverage-records.jsonl, proof-sufficiency-evaluation.md, proof-sufficiency-summary.json |
| G | Overclaim detector lead | CLOSED_VERIFIED | overclaim-detection-report.md, claim-decomposition-results.json, unsupported-feature-ledger.jsonl |
| H | Staleness evaluator | CLOSED_VERIFIED | staleness-invalidation-report.md, stale-claims.md, recomputation-queue.json |
| I | Delta promotion lead | CLOSED_VERIFIED | capability-deltas/, delta-promotion-report.md, poc-targets-sync-proposal.yaml |
| J | Gap queue generator | CLOSED_VERIFIED | mainstream-gap-queue.json, mainstream-gap-queue-report.md |
| K | Supervisor packet generator | CLOSED_VERIFIED | supervisor-verdict-packet.json, supervisor-verdict-packet-report.md |
| L | Test supervisor | CLOSED_VERIFIED | test-run-report.md, golden-replay-results.json |
| M | Repair supervisor | CLOSED_VERIFIED | minimal-repair-report.md (1 overclaim remediated in pilot graph) |
| N | State/planning supervisor | CLOSED_VERIFIED | next-sprint-recommendation.md, generated-next-prompt.md |
| O | Independent verification supervisor | CLOSED_VERIFIED | final-adversarial-independent-verification.md |

## Coordinator: Integrates all lanes after IV.
