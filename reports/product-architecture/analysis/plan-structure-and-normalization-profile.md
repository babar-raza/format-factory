# Plan Structure and Normalization Profile
Generated: 2026-07-04
Source: plans/.claude/imperative-drifting-conway.md

## Plan Structure

| Part | Content | Type |
|------|---------|------|
| Part A | Plan Reasoning Layer (§1-§13) | Reasoning (preserved) |
| Part B | Task Overview (19 parent TC table + DAG) | Execution overview |
| Part C | Micro-taskcardized Execution (TC-ARC-000 to TC-ARC-018) | Execution control |
| Part D | Unified Three-Plan Execution Schedule (Phases 0-6) | Cross-plan sequencing |

## Normalization Profile

| Dimension | Value |
|-----------|-------|
| Plan ID | ARC-QNAME-001 |
| Version | 3.0 |
| Format | Markdown with YAML-embedded taskcard schemas |
| Naming convention | TC-ARC-{3-digit}, child: TC-ARC-{parent_num}-{2-digit}, micro-step: MS-{parent}-{child}-{2-digit} |
| State vocabulary | parent: 11 states, child: 8 states, micro-step: 6 states |
| Quality gate | 8 dimensions scored ≥4/5 per child before CLOSED |
| Evidence contract | Each TC has named evidence file + verification command |
| Completion counters | 23 counters (§13) all must reach 0 |

## Normalization Actions Applied

1. Stable ID map created (stable-id-map.yaml) — IDs never renumbered
2. All file ownership resolved (file-ownership-and-locks.yaml) — no concurrent write conflicts
3. All parallel-safe pairs documented (parallel-execution-safety-map.yaml)
4. All cross-plan constraints documented (contradiction-and-duplication-ledger.yaml)
5. All actionable items mapped to taskcards (no-actionable-item-loss-audit.md)
