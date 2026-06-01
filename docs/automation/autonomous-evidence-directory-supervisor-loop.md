# Autonomous Evidence-Directory Supervisor Loop

## Canonical Model

The supervisor operates in the same repo/worktree as the worker. The canonical evidence unit is a directory, not a ZIP.

### Evidence Path
`.local/evidences/<run_id>/`

### Declaration Path
`.local/evidences/<run_id>/evidence-declaration.yaml`

### Loop Steps
1. Worker receives execution handoff (next-worker prompt or human instruction).
2. Worker executes work.
3. Worker writes evidence directory under `.local/evidences/<run_id>/`.
4. Worker writes `evidence-declaration.yaml` and optionally `evidence-manifest.yaml`.
5. Supervisor receives declaration path.
6. Supervisor validates declaration schema and checks declared paths exist.
7. Supervisor inspects declared evidence artifacts.
8. Supervisor grades each declared work item (8 grade levels).
9. Supervisor returns failed/incomplete/overclaimed items as rework.
10. Supervisor adds forward product-factory work from master plan.
11. Supervisor generates next worker prompt.
12. Loop continues autonomously unless a true external gate blocks it.

### ZIP Rule
ZIP is optional. Used only for:
- External upload or transfer
- Archival
- Delivery-package inspection
- Cross-machine transfer

The declaration-driven loop must work without ZIP.

### Watcher/Discovery Demotion
- `watch_for_bundle.py` is optional. It may detect new declarations but does not produce verdicts.
- `discover_latest_evidence.py` is optional convenience.
- `run-on-latest` is legacy. Use `autonomous-cycle` instead.

### Supervisor Commands
```
python tools/supervisor/supervisor_loop.py autonomous-cycle --declaration PATH
python tools/supervisor/supervisor_loop.py validate-declaration --declaration PATH
python tools/supervisor/supervisor_loop.py inspect-declared --declaration PATH
python tools/supervisor/supervisor_loop.py grade-declared --declaration PATH
python tools/supervisor/supervisor_loop.py plan-next --review PATH
python tools/supervisor/supervisor_loop.py create-sample-declaration --out PATH
python tools/supervisor/supervisor_loop.py list-unreviewed-declarations
```

### Review Outputs
Written to `.local/supervisor/reviews/<run_id>/`:
- supervisor-review.json / .md
- item-grades.yaml / .json
- accepted-items.yaml
- rework-items.yaml
- rejected-items.yaml
- overclaimed-items.yaml
- next-work-items.yaml / .json
- combined-next-worker-prompt.md
- supervisor-cycle-manifest.yaml

Latest summaries copied to `reports/supervisor/latest-*.md`.

### Exit Codes
- 0: Success, autonomous continue possible
- 1: Declaration not found or invalid
- 3: Critical rework exists (overclaimed/rejected items)
- 9: Unexpected error
