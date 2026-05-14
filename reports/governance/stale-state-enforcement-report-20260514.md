---
document_type: stale_state_enforcement_report
sprint: CONWAY-R7R8-MULTI-FORMAT-PLANNING-AND-STALENESS-SWARM-001
lane: A
title: "Stale-State Enforcement Report"
date: "2026-05-14"
visibility: internal
---

# Stale-State Enforcement Report — Lane A

**Sprint:** CONWAY-R7R8-MULTI-FORMAT-PLANNING-AND-STALENESS-SWARM-001
**Date:** 2026-05-14

---

## VERDICT: STALE_STATE_ENFORCEMENT_STATUS: COMPLETE

---

## Section 1: What Was Built

### New Module
- `tools/skills/stale_detection.py` — standalone stale detection module (5 checks)

### Extensions
- `tools/skills/format_context_resolver.py` — populates `requirements_state.stale` field (was `None` stub)
- `tools/skills/lane_selector.py` — STALE_BLOCKED redirects implementation lanes to LANE-R5
- `tools/skills/swarm_prompt_generator.py` — STALE_BLOCKED hard-blocks prompt generation

### Tests
- `tests/skills/test_stale_detection.py` — 32 tests (all PASS)

---

## Section 2: Stale Detection Checks

| # | Check | Severity | Verdict Impact |
|---|-------|----------|----------------|
| 0 | Directory exists | BLOCKER | STALE_BLOCKED |
| 1 | Timestamp consistency across files | WARN | REVIEW_REQUIRED |
| 2 | Verifier review newer than requirements generation | BLOCKER | STALE_BLOCKED |
| 3 | Registry IV date on or after verifier review | BLOCKER/WARN | STALE_BLOCKED/REVIEW_REQUIRED |
| 4 | Registry accepted_count matches file count | BLOCKER | STALE_BLOCKED |
| 5 | No requirements file modified after IV date (mtime) | WARN | REVIEW_REQUIRED |

### Verdict Logic

| Condition | Verdict |
|-----------|---------|
| Any BLOCKER check fails | STALE_BLOCKED |
| ≥2 WARNings, no blockers | REVIEW_REQUIRED |
| ≤1 WARNING, no blockers | FRESH |

---

## Section 3: Integration Points

### Resolver Integration
`resolve_format_context()` now calls `detect_stale_state(fmt)` and populates
`requirements_state["stale"]` with the full stale detection result. The prior stub
(`stale: None`) is replaced with a live dict containing `verdict`, `checks`, `reasons`, `blocker_count`.

### Lane Selector Integration
When `requirements_state.status == REQUIREMENTS_AUTHORITATIVE` AND `stale.verdict == STALE_BLOCKED`:
- LANE-R5 (re-verification) is selected
- All implementation lanes (LANE-I-LOAD, LANE-I-OBJECT-MODEL, LANE-I-EDIT, LANE-I-SAVE, LANE-I-TESTS) are blocked
- REVIEW_REQUIRED and FRESH do not block implementation lanes

### Prompt Generator Integration
When `stale.verdict == STALE_BLOCKED`:
- Returns `generator_status = "BLOCKED_STALE"`
- Returns `prompt = None`
- Blocks independently of the REQUIREMENTS_AUTHORITATIVE state check

---

## Section 4: Live State (2026-05-14)

| Format | Stale Verdict |
|--------|--------------|
| FODS | FRESH or REVIEW_REQUIRED (not STALE_BLOCKED) |
| FODT | FRESH or REVIEW_REQUIRED (not STALE_BLOCKED) |

Both formats pass the live stale check. Implementation lanes remain available.

---

## Section 5: Known Limitations

| Limitation | Severity | Mitigation |
|------------|----------|------------|
| File mtime check (check 5) is informational (WARN only) | LOW | mtime is unreliable across checkouts; YAML timestamps are the authority |
| No auto-regeneration on stale detection | BY DESIGN | Autonomous regeneration is not allowed (AGENTS.md AF9) |
| Registry must be manually updated when requirements change | LOW | Consistency check script catches divergence |

---

**LANE_A_STATUS: COMPLETE**
**STALE_DETECTION_MODULE: tools/skills/stale_detection.py**
**STALE_VERDICTS: FRESH | REVIEW_REQUIRED | STALE_BLOCKED**
**TESTS: 32/32 PASS**
**RESOLVER_INTEGRATED: YES**
**LANE_SELECTOR_INTEGRATED: YES**
**PROMPT_GENERATOR_INTEGRATED: YES**
