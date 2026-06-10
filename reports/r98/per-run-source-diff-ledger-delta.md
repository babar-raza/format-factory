# Per-Run Source Diff and Ledger Delta Requirement

## Policy (R98+)
Each autonomous run must capture:
1. Base tree/ref (git HEAD at start)
2. Source diffs for changed src/* files
3. Product-code ledger delta (new entries this run)
4. POC matrix delta

## Storage
- `source-diffs/<run_id>.patch`
- `ledger-deltas/<run_id>.json`
- `matrix-deltas/<run_id>.yaml`

## Implementation Status
- Requirement documented (R98)
- R93-R97 best-effort: final source state available, per-run diffs not reconstructible
