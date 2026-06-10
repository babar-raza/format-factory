# Shared File Control Policy
Sprint: FORMAT-FACTORY-SUPERPOWERS-AGENTIC-AUTONOMY-EXECUTION-001 (future)

## Coordinator-Owned Shared Files
- `reports/superpowers-agentic-autonomy/execution-state.json` — COORDINATOR WRITE ONLY; all other lanes READ-ONLY
- `reports/superpowers-agentic-autonomy/taskcard-state.json` — COORDINATOR WRITE ONLY; all other lanes READ-ONLY

## Overlap Violation Protocol
1. Two lanes declare same owned path → BLOCKED_LOCAL, coordinator resolves
2. Coordinator must inspect both lanes' claims, reassign one path, update lane-claims.json
3. Resolution must be documented in execution-state.json before blocked lane continues

## Touched-Files Ledger
Each file write must emit a JSONL entry: {"ts": "<ISO>", "lane": "<ID>", "action": "CREATE|EDIT", "path": "<path>"}
Any path written by a lane not in its owned_paths = DIRTY_STATE violation.
