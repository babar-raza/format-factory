# Dual-Orchestration KPI Model

## KPI Definitions

### Baseline (Manual Loop — Before Retirement)

| ID | KPI | Value |
|----|-----|-------|
| KPI-01 | Manual upload actions per sprint | 1 |
| KPI-02 | Manual copy-paste events per sprint | 2 |
| KPI-03 | ChatGPT review sessions required | 1 per sprint |
| KPI-04 | Time from bundle to next-sprint artifact (minutes) | 30–90 |
| KPI-05 | Human interventions not at true gates | 2–4 per sprint |
| KPI-06 | Automatable stop points | ~2 per sprint |

### Target (MODE 5 Autonomous Loop)

| ID | KPI | Target |
|----|-----|--------|
| KPI-01 | Manual upload actions per sprint | 0 |
| KPI-02 | Manual copy-paste events per sprint | 0 (non-gate sprints) |
| KPI-03 | ChatGPT sessions required | 0 (optional only) |
| KPI-04 | Time from bundle to next-sprint artifact (minutes) | < 10 |
| KPI-05 | Human interventions not at true gates | 0 |
| KPI-07 | Successful autonomous loop iterations | Measured per sprint |

## Measurement Data Location

`supervisor_loop.py` writes timing metadata to `.supervisor/state/current-run.json`:

```json
{
  "run_start": "2026-05-30T16:56:03",
  "discover_timestamp": "...",
  "review_timestamp": "...",
  "next_timestamp": "...",
  "memory_sync_timestamp": "...",
  "run_end": "...",
  "final_exit_code": 0,
  "critical_contradictions": 0,
  "autonomous_continue": true
}
```

## KPI Reporting

Per-sprint KPI capture:

1. `run_end - run_start` = total pipeline time (KPI-04 target: < 10 minutes)
2. `critical_contradictions == 0 AND autonomous_continue == true` = successful autonomous loop (KPI-07)
3. `final_exit_code == 0` = no manual intervention required (KPI-05)
4. `final_exit_code in (1, 2, 3)` = manual intervention required (count toward KPI-05)

## Success Criteria

MODE 5 is considered SUCCESSFUL when:
- KPI-01 = 0 (no uploads) for 3 consecutive sprints
- KPI-02 = 0 (no copy-paste) for 3 consecutive sprints
- KPI-04 < 10 minutes for 3 consecutive sprints
- KPI-07 >= 3 (three successful autonomous iterations)

## Stop Events That Reset KPI-07

Any of these resets the autonomous loop counter:
- `final_exit_code == 3` (critical contradictions)
- Human intervention for non-gate reason
- Evidence validation failure requiring manual repair
- Forbidden file modification detected

## Relationship to Format Factory Gates

KPIs measure operational efficiency — not product quality.
Gate approval (G11-G) is always a human event and is NOT counted against KPI-05.
Human gate approvals are required and expected.

KPI-05 measures non-gate human interventions only.
