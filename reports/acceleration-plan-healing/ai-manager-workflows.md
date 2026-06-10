# AI Manager Workflows

**Sprint:** FORMAT-FACTORY-ACCELERATION-PRODUCT-FIRST-AI-LLM-EMBEDDING-EXECUTION-001
**Date:** 2026-06-04

---

## Workflow A: System Observation (ai_product_brain)

| Field | Value |
|-------|-------|
| Input | poc-targets.yaml (read-only); gateway config |
| Output | product-capability-graph.json, poc-distance-score.json, product-gap-rankings.json, over-investment-analysis.json |
| Authority | ai_draft — never modifies poc-targets.yaml |
| Gateway Role | summarization (fixture OK) |
| Trigger | Start of each sprint; updates lane selection |

## Workflow B: Pre-Sprint Planning (ai_sprint_manager --pass pre)

| Field | Value |
|-------|-------|
| Input | Brain outputs; gap selection |
| Output | pre-sprint-plan.json with lane_design + dependency_map |
| Authority | advisory_only: true; never prescriptive |
| Gateway Role | agentic_low_risk (NO fixture — skipped if unavailable) |
| Trigger | Before sprint begins; informs Mainstream lane assignment |

## Workflow C: Pattern Mining + Design (source_pattern_miner + ai_implementation_designer)

| Field | Value |
|-------|-------|
| Input | src/ files (read-only); selected gap |
| Output | {format}-patterns.json; {format}-{gap}-design.md; test-strategy.md; dogfood-strategy.md |
| Authority | ai_draft frontmatter in all files; src/ never modified |
| Gateway Role | summarization / structured_extraction (fixture OK) |
| Trigger | Per format gap; runs for all 4 selected gaps |

## Workflow D: Mid-Sprint Reroute (ai_sprint_manager --pass mid)

| Field | Value |
|-------|-------|
| Input | Lane ledger; partial outputs from Wave C |
| Output | mid-sprint-reroute.json with stuck_lanes + reroute_suggestions + breadth_warning |
| Authority | advisory_only: true; NEVER modifies lane assignments directly |
| Gateway Role | agentic_low_risk (NO fixture — skipped if unavailable) |
| Trigger | After initial implementation; detects imbalance |

## Workflow E: Evidence Critique (ai_evidence_critic)

| Field | Value |
|-------|-------|
| Input | Sprint output artifacts; anti_skip results |
| Output | evidence-critique.json with sprint_grade; overclaim-risk.md |
| Authority | MACHINERY_CREEP verdict is advisory — never blocks autonomous-cycle |
| Gateway Role | evidence_review (fixture OK) |
| Trigger | After all implementations complete; before evidence declaration |

## Workflow F: Learning + Final Pass (ai_learning_loop + ai_sprint_manager --pass final)

| Field | Value |
|-------|-------|
| Input | final-review.json; evidence-critique.json |
| Output | sprint-learnings.jsonl (JSONL); final-review.json; next-sprint-recommendation.md |
| Authority | All outputs ai_draft; JSONL machine-readable by next sprint pre-pass |
| Gateway Role | summarization (fixture OK) / agentic_low_risk (skipped if unavailable) |
| Trigger | Sprint closeout; feeds into next sprint pre-pass |
