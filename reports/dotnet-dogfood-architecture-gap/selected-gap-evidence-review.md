# Lane A: Selected-Gap Evidence Review
**Sprint:** FORMAT-FACTORY-DOTNET-DOGFOOD-ARCHITECTURE-GAP-INVESTIGATION-AND-PLANNING-001
**Reviewer Lane:** Lane A
**Review Date:** 2026-06-05

---

## Evidence Sources

| # | File | Path | Generated At |
|---|------|------|--------------|
| 1 | selected-product-gaps.json (primary) | `.local/supervisor/selected-product-gaps.json` | 2026-06-03T02:57:17.883306+00:00 |
| 2 | selected-product-gaps-mainstream.json (stream view) | `.local/supervisor/streams/selected-product-gaps-mainstream.json` | 2026-06-03T02:57:17.883306+00:00 |

Both files share identical `generated_at` timestamps — they were produced in the same supervisor pipeline run (R98 sprint selection, policy v3).

---

## Gap Confirmation Table

All four architecture-blocked gaps were found. Confirmed data from both source files:

| gap_id | product | target_format | score | poc_impact | depth_bonus | classification | stream | decision | rank |
|--------|---------|---------------|-------|------------|-------------|----------------|--------|----------|------|
| commercial-net-fods-dogfood-status-fods-to-csv-dotnet | FODS .NET | csv | **125** | 95 | 10 | **GAP_DOGFOOD_EXTERNAL** | mainstream | GOVERNED_SKILL_REQUIRED | 1 |
| commercial-net-fods-dogfood-status-fods-to-html-dotnet | FODS .NET | html | **125** | 95 | 10 | **GAP_DOGFOOD_EXTERNAL** | mainstream | GOVERNED_SKILL_REQUIRED | 2 |
| commercial-net-fodt-dogfood-status-fodt-to-markdown-dotnet | FODT .NET | markdown | **125** | 95 | 10 | **GAP_DOGFOOD_EXTERNAL** | mainstream | GOVERNED_SKILL_REQUIRED | 3 |
| commercial-net-fodt-dogfood-status-fodt-to-txt-dotnet | FODT .NET | txt | **125** | 95 | 10 | **GAP_DOGFOOD_EXTERNAL** | mainstream | GOVERNED_SKILL_REQUIRED | 4 |

Additional fields confirmed for all four gaps:
- `handoff_required`: false
- `external_gate`: false
- `governed_skill`: "governed-dogfood-export"

The four gaps occupy ranks 1-4 (the top four positions) in both JSON files, making them the highest-priority items in the entire selected gap queue. No other gap reaches score=125; the next tier is score=110 (SYLK installed workflow).

---

## Freshness Analysis

- **File generation timestamp:** 2026-06-03T02:57:17 UTC
- **Review date:** 2026-06-05
- **Age:** approximately 47-48 hours (nearly 2 full days)
- **Threshold:** 24 hours
- **Flag:** **STALE_>24H**

The gap selection file was produced during the R98 sprint selection run. Sprint work has continued since (R93 context-pack, R94-R116 test additions visible in git status). The underlying `poc-targets.yaml` source matrix may have been updated by subsequent sprints. However, the four GAP_DOGFOOD_EXTERNAL items relate to dogfood export architecture and are unlikely to have been resolved without an explicit architecture decision — they require an external writer dependency that does not yet exist in the .NET product source. The staleness flag is noted but does not invalidate the gap identity; it signals that a re-run of `select_poc_gaps.py` before implementation is prudent.

---

## Top 10 Non-Blocked Gaps

These are the gaps from the file that are NOT among the four architecture-blocked dogfood gaps. They represent safe alternative lanes that do not require an external architecture decision.

| rank | gap_id | score | product | format | status | stream | recommended_as_alternative |
|------|--------|-------|---------|--------|--------|--------|---------------------------|
| 5 | foss-reduced-sylk-python-status-installed-workflow | 110 | SYLK Python | SYLK | PARTIAL | mainstream | YES — installed workflow verification, FOSS, no external arch dependency |
| 6 | foss-reduced-netpbm-blockers-1 | 90 | Netpbm Python | Netpbm | BLOCKED | mainstream | YES — installed-package proof refresh, FOSS, governed skill available |
| 7 | foss-reduced-sylk-blockers-1 | 90 | SYLK Python | SYLK | BLOCKED | mainstream | YES — SYLK writer scope clarification, FOSS |
| 8 | foss-reduced-zst-blockers-1 | 90 | ZST Python | ZST | BLOCKED | mainstream | YES — dependency resolution (zstandard PyPI), FOSS |
| 9 | commercial-net-fods-blockers-1 | 70 | FODS .NET | FODS | BLOCKED | supervisor | ESCALATION — Gate 11 G11-G, requires Babar Raza approval |
| 10 | commercial-net-fodt-blockers-1 | 70 | FODT .NET | FODT | BLOCKED | supervisor | ESCALATION — Gate 11 G11-G, requires Babar Raza approval |
| 11 | commercial-net-netpbm-blockers-1 | 70 | Netpbm .NET | Netpbm | BLOCKED | supervisor | ESCALATION — Gate 11 G11-G, requires Babar Raza approval |
| 12 | commercial-net-fods-gate-11-g11g | 30 | FODS .NET | FODS | NOT_STARTED | supervisor | ESCALATION — Gate 11 G11-G |
| 13 | commercial-net-fodt-gate-11-g11g | 30 | FODT .NET | FODT | NOT_STARTED | supervisor | ESCALATION — Gate 11 G11-G |
| 14 | commercial-net-netpbm-gate-11-status | 30 | Netpbm .NET | Netpbm | NOT_STARTED | supervisor | ESCALATION — Gate 11 status |

Note: Ranks 9-14 all have `external_gate: true` and `handoff_required: true`; they are not autonomous lanes. The total gap count in the file is **14** (8 mainstream + 6 supervisor stream).

**Top 5 safe alternatives (non-blocked, non-external-gate) for Lane recommendation:**
1. `foss-reduced-sylk-python-status-installed-workflow` — score 110, SYLK FOSS Python, PARTIAL status, governed skill available
2. `foss-reduced-netpbm-blockers-1` — score 90, Netpbm FOSS Python, install proof refresh
3. `foss-reduced-sylk-blockers-1` — score 90, SYLK FOSS Python, writer scope
4. `foss-reduced-zst-blockers-1` — score 90, ZST FOSS Python, dependency resolution
5. (Next available autonomous lane after those four is external-gate-only territory — supervisor stream only)

---

## Local Verdict

**ACCEPT**

All four architecture-blocked gaps are confirmed present in both evidence sources with:
- score = 125 (exactly as expected)
- classification = GAP_DOGFOOD_EXTERNAL (exactly as expected)
- stream = mainstream (exactly as expected)
- ranks 1-4 (top-ranked items in the entire gap queue)
- decision = GOVERNED_SKILL_REQUIRED with governed_skill = governed-dogfood-export

The staleness flag (STALE_>24H, ~47-48h) is noted. A re-run of gap selection before implementation is recommended but does not change the architectural reality: these four gaps require dogfood export via a downstream FF writer that has not yet been built into the .NET product. The gap data is internally consistent across both JSON files (identical timestamps, identical field values).

**Confidence:** HIGH — four gaps confirmed, zero discrepancies between primary and stream-view files.
