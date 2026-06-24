# Structural Assessment: tools/supervisor/ Directory
# TC-VNK-H-011 — Assessment Only (no files moved)
# Date: 2026-06-23

authoritative_plan: plans/vivid-napping-kurzweil-hardening-addendum.md
artifact_role: analysis_or_evidence_only
execution_authority: false

---

## Summary

- **Total files:** 161 Python files + 1 existing subdirectory (`backends/`, 8 files)
- **Total LOC:** ~62,493
- **Recommendation:** CONDITIONAL GO — phased approach required
- **Phase 1 risk:** LOW (31 files, ~16 import updates)
- **Full reorganization risk:** HIGH (128+ import updates, CLAUDE.md/test path changes)

---

## Categorization (18 groups)

| Group | Proposed Subdir | Files | Est. LOC | Inbound Imports | Risk |
|-------|----------------|-------|----------|-----------------|------|
| AI Advisors | `ai_advisors/` | 6 | ~2,050 | 2 | LOW |
| Continuation & Session | `continuation/` | 7 | ~3,100 | 42 | HIGH |
| Grading | `grading/` | 4 | ~2,200 | 14 | MEDIUM |
| Governance | `governance/` | 5 | ~8,600 | 14 | MEDIUM |
| Evidence & Declaration | `evidence/` | 13 | ~4,500 | 27 | MEDIUM |
| External Host | `external_host/` | 5 | ~2,900 | 3 | LOW |
| Sprint Execution Core | `sprint_core/` | 6 | ~6,600 | 35 | HIGH |
| Plan Management | `plan_mgmt/` | 4 | ~700 | 13 | MEDIUM |
| Capability | `capability/` | 5 | ~2,000 | 10 | LOW-MEDIUM |
| Autonomy Routing | `autonomy_routing/` | 3 | ~1,500 | 9 | MEDIUM |
| Libforge Integration | `libforge/` | 4 | ~2,000 | 2 | LOW |
| Product Deepening | `product/` | 7 | ~2,800 | 5 | LOW |
| Next-Action | `next_action/` | 4 | ~1,200 | 7 | LOW |
| Stream/Forecasting | `stream/` | 5 | ~1,500 | 2 | LOW |
| Lane Execution | `lane/` | 4 | ~1,600 | 4 | LOW |
| Utility/Infrastructure | `util/` | 8 | ~2,200 | 23 | HIGH |
| Validators (misc) | `validators/` | 17 | ~4,500 | varies | LOW-MEDIUM |
| Remaining/Uncategorized | (root) | 48 | ~15,000 | varies | — |
| Existing `backends/` | `backends/` | 8 | — | — | DONE |

---

## Hub Files (highest coupling)

| File | Inbound Imports | Notes |
|------|-----------------|-------|
| `autonomous_cycle.py` | 20 | Most coupled file; also referenced in 60+ test files |
| `continuation_state.py` | 12 | Foundational infrastructure |
| `continuation_identity.py` | 11 | Session identity |
| `supervisor_loop.py` | 9 | CLI entry point; path in CLAUDE.md |
| `evidence_declaration.py` | 8 | Evidence schema |
| `check_continuation.py` | 8 | CLI entry point; path in CLAUDE.md |
| `action_queue.py` | 8 | Utility |
| `governance_validators.py` | 7 | Largest file (3,081 LOC) |
| `atomic_io.py` | 7 | Utility |
| `grade_declared_work.py` | 6 | Grading hub |
| `write_plan_lock.py` | 6 | CLI entry point; path in CLAUDE.md |

---

## Phased Reorganization Proposal

### Phase 1 — LOW RISK (immediate)
Move 6 groups with <5 inbound imports:
- `ai_advisors/` (6 files, 2 imports to fix)
- `libforge/` (4 files, 2 imports)
- `product/` (7 files, 5 imports)
- `stream/` (5 files, 2 imports)
- `external_host/` (5 files, 3 imports)
- `lane/` (4 files, 4 imports)

**Total: 31 files, ~16 import path updates.**

### Phase 2 — MEDIUM RISK
Move medium-coupling groups with `__init__.py` re-exports:
- `capability/` (5 files, 10 imports)
- `next_action/` (4 files, 7 imports)
- `autonomy_routing/` (3 files, 9 imports)
- `plan_mgmt/` (4 files, 13 imports)
- `evidence/` (13 files, 27 imports)

**Total: 29 files, ~66 import updates + `__init__.py` re-exports.**

### Phase 3 — HIGH RISK (dedicated sprint)
Move hub groups:
- `governance/` (5 files, 14 imports + bidirectional internals)
- `grading/` (4 files, 14 imports + bidirectional internals)
- `continuation/` (7 files, 42 imports)
- `util/` (8 files, 23 imports)
- `sprint_core/` (6 files, 35 imports + 60 test files + CLI path refs)

**Total: 30 files, ~128+ import updates, CLAUDE.md/AGENTS.md path updates required.**

### Phase 4
Categorize and move remaining 48 uncategorized files.

---

## Blockers for Any Phase

1. Each `__init__.py` must re-export all public names for backward compatibility
2. CLI path references in CLAUDE.md, AGENTS.md, `.claude/commands/*.md` must be
   updated atomically with file moves
3. 60+ test files in `tests/supervisor/` use `from tools.supervisor.X import ...`
4. `governance_validators.py` absolute import issue (known-failure-ledger) may worsen
5. Every moved file requires corresponding test import updates in same commit

---

## Go/No-Go Verdict

**CONDITIONAL GO with Phase 1 only as immediate next step.**

Phase 1 is safe: 31 leaf-node files with only 16 import fixes. Zero CLAUDE.md
path references affected. Zero CLI entry point changes.

Phases 2-4 require dedicated sprints with full import analysis and atomic
commit discipline. Do NOT attempt Phases 2-4 as part of a plan addendum.

The alternative "keep flat" is also valid — 164 files in one directory is
large but not unprecedented for a supervisor/orchestration layer.
