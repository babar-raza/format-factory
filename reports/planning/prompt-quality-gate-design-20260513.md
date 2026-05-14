---
document_type: quality_gate_design
sprint: CONWAY-R1R2-ACCELERATED-FOUNDATION-SWARM-001
lane: F
title: "Prompt Quality Gate Design + Lane Library"
date: "2026-05-13"
visibility: internal
publish_allowed: false
---

# Prompt Quality Gate Design — Lane F

**Sprint:** CONWAY-R1R2-ACCELERATED-FOUNDATION-SWARM-001
**Date:** 2026-05-13

---

## Summary

`templates/commercial-sprint/lane-library.yaml` was created defining all lane contracts,
ownership rules, and quality gate criteria. No prompt generator was implemented.

**LANE_LIBRARY_STATUS: COMPLETE**
**PROMPT_QUALITY_GATE_DESIGN: DOCUMENTED**

---

## Section 1: Lane Library Contents

`templates/commercial-sprint/lane-library.yaml` defines:

### R-Lanes (Requirements + Verification)
| Lane | Purpose | Output |
|------|---------|--------|
| LANE-R3 | Requirements generation from local sources | 5 requirement YAML files |
| LANE-R4 | Format context resolver | Structured context block |
| LANE-R5 | Adversarial verifier review | verifier-review.yaml |
| LANE-C | Coordinator | Integration, evidence, state updates |

### I-Lanes (Implementation)
| Lane | Purpose |
|------|---------|
| LANE-I-LOAD | Load pipeline implementation |
| LANE-I-MODEL | Object model implementation |
| LANE-I-EDIT | Edit operations implementation |
| LANE-I-SAVE | Save + round-trip implementation |
| LANE-I-TESTS | Test suite implementation |
| LANE-I-GOVN | AI governance compliance check |

### Special Constraints
- **FODT-REQ-040 iterative traversal constraint** is explicitly surfaced in LANE-I-MODEL and LANE-I-LOAD for FODT format — must appear in every generated FODT implementation prompt
- **LANE-K** (AI orchestration) references `docs/agent-swarm-ai-orchestration.md`

---

## Section 2: Prompt Quality Gate Criteria (10)

When `tools/skills/swarm_prompt_generator.py` is built (Phase R4), it MUST pass a
10-criterion quality gate before emitting any generated prompt:

| # | Criterion | Description |
|---|-----------|-------------|
| 1 | No forbidden git commands | No stash, reset, restore, clean, push |
| 2 | No broad staging | No `git add -A` or `git add .` |
| 3 | No gate self-approval | No language claiming gate approval |
| 4 | No commercial readiness claim | No `commercial_product_ready: true` |
| 5 | 20-component completeness | All 20 required execution-handoff components present |
| 6 | ACCEPTED_FOR_VERTICAL_SLICE ID present | At least one authoritative requirement ID referenced |
| 7 | No NEEDS_REVIEW or GENERATED IDs | Blocked IDs must not appear as implementation targets |
| 8 | Evidence contract path referenced | Prompt must cite its evidence contract |
| 9 | DEC-034 IV prompt referenced | Prompt must include DEC-034 IV instruction |
| 10 | No overclaim beyond capability level | Cannot claim C8+ if current state is C6 |

**FODT-specific additional gate:**
- Gate 11 (FODT only): FODT-REQ-040 iterative traversal constraint must appear explicitly if any list entity is in scope

---

## Section 3: Forbidden Prompt Behaviors

These are authority violations if they appear in any generated prompt:

```
FORBIDDEN_PATTERNS = [
    "git stash",
    "git reset",
    "git restore",
    "git clean",
    "git push",
    "git add -A",
    "git add .",
    "Gate 11: PASSED",
    "commercial_product_ready: true",
    "gate_11_status: approved",
    "implementation is complete",
    "commercial readiness achieved",
    "recursive.*list.*traversal",   # FODT-REQ-040 violation
]
```

---

## Section 4: What Was NOT Implemented (By Design)

| Item | Status | Reason |
|------|--------|--------|
| `tools/skills/swarm_prompt_generator.py` | NOT BUILT | Phase R4 — not yet safe without Phase R3 lane_selector |
| Automatic prompt generation | NOT IMPLEMENTED | Requires human checkpoint at Phase R6 |
| `/commercial-sprint` command | NOT BUILT | Phase R6 — depends on R2-R5 completion |
| Autonomous execution | NOT IMPLEMENTED | Non-negotiable governance rule |

---

**LANE_F_STATUS: COMPLETE**
**LANE_LIBRARY_CREATED: YES**
**PROMPT_QUALITY_GATE_CRITERIA: 10 (documented, not yet implemented as code)**
**PROMPT_GENERATOR_CREATED: NO (Phase R4 — not yet safe)**
