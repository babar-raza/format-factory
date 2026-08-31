# 14 — Productive Cycle Scorecard

**Baseline commit:** dd909cf3a
**Assessment date:** 2026-08-31

## Current State (Before)

| Metric | Value | Evidence |
|--------|-------|----------|
| Formats with real product behavior (installed) | 5/6 | Experiment 11: IPYNB, NRRD, SafeTensors, UBL, XLIFF load from installed packages |
| Formats with honest certification | 0/6 | truth_boundary says 0/6; false certification exploit PROVEN |
| Formats with false certification label | 4/6 | controller-state.yaml promotion block: ipynb, nrrd, xliff, safetensors |
| Stable obligations proven by current tests | UNKNOWN | Reconciler never executes tests; evidence is historical snapshot |
| Mandatory obligations unresolved | 1 (ORA-specific) + UNKNOWN | ORA has 1 known; others may have stale evidence |
| Capabilities at CERTIFIED maturity | 0 | No certification is honestly derived |
| Real corpus cases in CI | 0 | CI doesn't install gen-2 packages |
| Independent oracle cases for FF6 | Variable | Oracle layer exists for gen-1; FF6 coverage varies |
| Installed-wheel E2E scenarios in CI | 0 | CI uses source tree, not installed wheels |
| Downstream consumer scenarios | 0 | No consumer tests exist |
| Known false claims | 5 | 4 false certifications + "promotion computed from proof" invariant |
| Stale evidence detected & rejected | 0 | No staleness detection mechanism |
| Product defects closed this assessment | 0 | Investigation-only, no fixes |
| Duplicate machinery paths | 6 | Six competing control systems |
| Dry-run commands that mutate state | 1+ | autonomous_task_generator.py PROVEN |
| Governance blocks honored | 0 | blocks=True → exit 3 → continue |
| CI jobs testing gen-2 packages | 0 | ci.yml installs root only |
| Contradictions in controller-state | 3 | promotion vs truth_boundary vs production_certifications |

## Target State (After R1-R20)

| Metric | Target | Repair item |
|--------|--------|-------------|
| Formats with honest certification | Derived from proof | R4, R5 |
| False certification labels | 0 | R4 |
| Evidence with source hash tracking | 100% of accepted evidence | R6 |
| Stale evidence auto-invalidated | All changed-hash evidence | R6 |
| Clean-clone bootstrap | Correct state from committed files | R7 |
| Dry-run mutations | 0 | R8 |
| IPYNB test failures | 0 | R9 |
| CI gen-2 package installations | 7 (core + 6 formats) | R10 |
| ORA namespace references consistent | 100% | R11 |
| Controller-state contradictions | 0 | R3 |
| Competing control systems | 1 | R14, R15, R16 |
| Governance blocks honored | All non-advisory | R16 |
| Complete vertical cycles proven | 1+ | R18 |
| Formats through complete chain | 6/6 | R19 |
| Obsolete paths removed | All identified | R20 |

## Gap Analysis

The gap between current and target state reveals the core problem: **the machinery has been designed to never stop, but not designed to prove progress.** Product code works (5/6 loads successfully). Machinery runs (autonomous_cycle completes cycles). But the connection between "machinery ran" and "product improved" is not measured, enforced, or even defined.

The repair plan (R1-R20) addresses this by:
1. Making certification honest (R3-R5) — removing false positive capability
2. Making evidence current (R6) — enabling freshness detection
3. Making bootstrap deterministic (R7) — enabling reproducibility
4. Making CI test real packages (R10) — enabling automated verification
5. Consolidating to one path (R14-R16) — eliminating ambiguity
6. Proving the complete cycle (R18) — establishing the working pattern
