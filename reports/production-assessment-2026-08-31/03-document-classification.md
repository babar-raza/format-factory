# 03 — Document Classification

**Baseline commit:** dd909cf3a
**Evidence:** Direct reading of each document

## Classification Key
- **NORMATIVE:** Defines rules that other systems enforce
- **DERIVED:** Generated from normative source; should be regeneratable
- **ADVISORY:** Provides guidance but nothing enforces it
- **HISTORICAL:** Records past decisions/events
- **STALE:** Contains information contradicting current repository state
- **CONTRADICTORY:** Contains internal contradictions

## Classification Table

| # | Document | Classification | Key evidence | Internal contradictions? | Cross-doc contradictions? |
|---|----------|---------------|--------------|--------------------------|---------------------------|
| 1 | README.md | STALE | Claims "840+ sprints" (actual 849), "166 validators" (actual 226), "20/20 certified" (GAP-008: 17 of 20 trace to synthetic manifests) | No | Yes — sprint count, validator count, certification claim |
| 2 | AGENTS.md | NORMATIVE | Non-negotiable operating contract. 195 capabilities. Sections A-AH | Minor — AF1-AF8 duplicated (copy-paste artifact) | No |
| 3 | CLAUDE.md | NORMATIVE | Session start protocol, plan lock, Supreme Directive, sprint closeout, FF6 resume | No | No |
| 4 | GOVERNANCE.md | NORMATIVE | Human governance rules. 591 lines | Minor — Section 25 appears twice with different content | No |
| 5 | ROADMAP.md | STALE | Last reviewed 2026-05-16. Only covers FODS/FODT/ZST. No mention of FF6 mission | No | Yes — omits FF6 entirely |
| 6 | PROJECT_STATUS.md | CONTRADICTORY | Summary: "20/20 certified," "200 validators." Detail table: ALL 31 formats show "no source" (generator bug) | Yes — summary contradicts detailed table | Yes — "20/20 certified" vs GAP-008 |
| 7 | plans/README.md | ADVISORY | 41-line navigation document | No | No |
| 8 | plans/master-plan.md | NORMATIVE | v6.1, 2026-07-10. Section 111: FF6 STAGE_1_COMPLETE. "six UNASSESSED; 0/6 certified" | No | Consistent with truth_boundary (contradicts promotion block) |
| 9 | plans/master-plan-memory.md | HISTORICAL | Ledger-only lineage. Explicitly: "MUST NOT be used as active execution plan" | No | No |
| 10 | plans/plan-hardening-addendum-from-latest-audit.md | HISTORICAL | All 3 taskcards CLOSED. Completed mission | No | No |
| 11 | plans/strategic/autonomous-six-python-production-execution-plan.md | NORMATIVE | STAGE_1_COMPLETE. All six UNASSESSED; 0/6 certified | No | Consistent with truth_boundary |
| 12 | plans/strategic/ff6/product-goal.yaml | NORMATIVE | Goal ACTIVE. Defines distributions and namespaces | No | ORA namespace disagreement with actual package |
| 13 | plans/strategic/ff6/controller-state.yaml | **CONTRADICTORY** | 891 lines, Event 522 | **YES — CRITICAL:** promotion (4/6 CERTIFIED) vs truth_boundary (0/6) vs production_certifications (0) | Yes — promotion contradicts master-plan, execution plan, current-state, current-gaps |
| 14 | plans/strategic/ff6/current-state.yaml | DERIVED | Snapshot at commit e4f8f5f0. All six not_certified | No | Consistent with truth_boundary |
| 15 | plans/strategic/ff6/current-gaps.yaml | DERIVED | 11 gaps. Zero certifications | No | Consistent with truth_boundary |
| 16 | plans/strategic/ff6/execution-recovery-directive.yaml | NORMATIVE | 26 structural gaps. GAP-008 identifies synthetic manifest problem | No | Intentionally contradicts README/PROJECT_STATUS (that's its purpose) |
| 17 | plans/codex/handover/START-HERE.md | STALE | References Event 47 (current: Event 522). 475 events behind | No | Stale relative to controller |
| 18 | plans/codex/handover/checkpoint.yaml | STALE | At Event 47. All UNASSESSED (correct) but deeply stale | No | Same staleness as START-HERE.md |
| 19 | docs/automation/operational-control-index.md | ADVISORY | Documents SQLite+FTS5 control index overlay | No | No |
| 20 | docs/automation/autonomous-continuation-policy.md | NORMATIVE | Defines continuation rule. States max_iterations default 5 | No | Minor — max_iterations 5 vs policies.yaml 12 (doc says "configurable") |
| 21 | docs/governance/current-state-and-evidence-authority.md | NORMATIVE | Run-state authority model | No | Scope narrower than current FF6-era project |
| 22 | docs/governance/product-first-operating-model.md | STALE | POC goal: FODS/FODT/Netpbm. Dated 2026-06-03. No FF6 reference | No | Yes — predates FF6 mission entirely |
| 23 | docs/governance/proof-authority-policy.md | NORMATIVE | Option B: Ledger-Backed Proof Graph. 129 entries, 7 products | No | No |
| 24 | .supervisor/README.md | ADVISORY | Says "99+ capabilities" (actual: 195) | No | Yes — stale count |
| 25 | .supervisor/policies.yaml | NORMATIVE | max_iterations: 12, hard prohibitions, supervisor_overrides_registry: false | No | Minor vs continuation-policy.md |
| 26 | .supervisor/config.yaml | DERIVED | Sprint_id from 2026-05-30 (stale runtime field) | No | Stale sprint_id vs session-resume.md |
| 27 | reports/supervisor/session-resume.md | DERIVED | Auto-generated 2026-08-05. Sprint 849. Autonomous continue: False. Trend: declining | No | Sprint count contradicts README.md |

## Critical Findings

### 1. controller-state.yaml is the most dangerous document
The promotion block is the SOLE certification authority read by goal_driver.py. Its values contradict two other sections in the same file and every external normative document.

### 2. PROJECT_STATUS.md has a generator bug
Summary claims 20 formats with source; detailed table shows ALL 31 as "no source."

### 3. "20/20 certified" is systemically overreported
README.md, PROJECT_STATUS.md repeat this claim. GAP-008 documents that 17 of 20 verdicts trace to synthetic manifests.

### 4. session-resume.md is the most honest runtime document
Reports "Autonomous continue: False," "trend: declining," sprint count 849 — consistent with 0/6 real certification.
