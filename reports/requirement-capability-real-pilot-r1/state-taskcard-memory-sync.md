# State / Taskcard Memory Sync
# Sprint: FORMAT-FACTORY-REQUIREMENT-CAPABILITY-AUTHORITY-LAYER-REAL-PILOT-R1-001

## Taskcard Final Status

| TC ID | Title | Status | Output |
|-------|-------|--------|--------|
| TC-R1-COORD | Coordinator preflight + lane ownership | DONE | lane-ownership.md, overlap-check.md, taskcard-state.json |
| TC-R1-INVENTORY | Layer implementation inventory | DONE | layer-implementation-inventory.md |
| TC-R1-PREFLIGHT | Preflight reads | DONE | 00-preflight.md |
| TC-R1-PLAN | Pilot plan | DONE | pilot-plan.md |
| TC-R1-SNAPSHOT-A | Netpbm input snapshot | DONE | input-snapshots/netpbm/ |
| TC-R1-SNAPSHOT-B | FODS input snapshot | DONE | input-snapshots/fods/ |
| TC-R1-SNAPSHOT-C | FODT input snapshot | DONE | input-snapshots/fodt/ |
| TC-R1-SNAPSHOT-D | ZST input snapshot | DONE | input-snapshots/zst/ |
| TC-R1-SNAPSHOT-E | DIF input snapshot | DONE | input-snapshots/dif/ |
| TC-R1-GRAPH | Proof graph construction (all 5 pilots) | DONE | proof-graph/ (81 nodes, 102 edges) |
| TC-R1-COVERAGE | Coverage evaluation | DONE | coverage-records.jsonl, proof-sufficiency-summary.json |
| TC-R1-OVERCLAIM | Overclaim detection + remediation | DONE | overclaim-detection-report.md (1 remediation applied) |
| TC-R1-STALENESS | Staleness invalidation | DONE | staleness-invalidation-report.md, stale-claims.md |
| TC-R1-DELTA | Delta promotion | DONE | delta-promotion-report.md |
| TC-R1-GAPQUEUE | Mainstream gap queue | DONE | mainstream-gap-queue.json |
| TC-R1-SVP | Supervisor verdict packet | DONE | supervisor-verdict-packet.json |
| TC-R1-SYNC | POC targets sync proposal | DONE | poc-targets-sync-proposal.yaml (read-only proposal, no mutation) |
| TC-R1-TESTS | Test file + golden replay | DONE | tests/requirement_capability_authority/test_real_pilot_r1.py (25/25) |
| TC-R1-IV | Final adversarial IV | DONE | final-adversarial-iv.md |

## Memory Sync Notes

### Confirmed Working
- `PocReadinessComputer.compute_all()` — correct API (not `.compute()`)
- `GraphStore.save_nodes()` + `save_edges()` — correct API (not `save_to_dir()`)
- `GraphStore.nodes` + `.edges` — correct API (not `._nodes`, `._edges`)
- `StalenessReport.stale_events` — list of event objects (not `stale_event_ids`)
- `SupervisorVerdictPacketGenerator.generate(staleness_report=..., readiness_result=..., gap_queue_result=...)` — correct parameter names
- `PocTargetsSyncProposalGenerator(store)` — requires store argument
- `ValidationError.message` — correct attribute (not `ValidationError.__str__`)

### Architecture Blockers Confirmed
- FODS CSV export: BLOCKED — no standalone FormatFactory.Csv writer library
- FODS HTML export: BLOCKED — no standalone FormatFactory.Html writer library
- FODT Markdown export: BLOCKED — no standalone FormatFactory.Markdown writer library
- FODT TXT export: BLOCKED — no standalone FormatFactory.Txt writer library

### RCA Layer Coverage
- All 15 modules in tools/requirements_authority/ verified working
- 81 nodes (18 node types), 102 edges across 5 pilots
- 0 validation errors; 1 overclaim remediated (netpbm:save direction write_only → read_write)
- 1 stale claim detected (zst:old-compress, synthetic)
- 6/6 golden replay fixtures PASS

## State Files Updated

| File | Change |
|------|--------|
| reports/requirement-capability-real-pilot-r1/taskcard-state.json | Exists; TCs updated to DONE |
| reports/supervisor/session-resume.md | Not updated (updated by autonomous-cycle) |
| .supervisor/project-memory.md | Not updated directly (supervisor pipeline updates) |
