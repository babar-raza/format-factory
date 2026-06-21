# Evidence Index — Format Factory Machinery Audit v2
# Sprint ID: ff-machinery-readiness-audit-v2-20260621-827f5a52

## Artifacts Produced This Audit

| File | Description |
|------|-------------|
| sprint-overview.md | Audit purpose, delta summary, verdict |
| preflight-state.md | Git state, dirty files, run IDs, key state files |
| qname-schema-audit.md | QName schema design and per-format compliance |
| per-product-qname-compliance.yaml | Matrix of all products vs QName criteria |
| src-source-quality-review.md | Per-product source quality ratings |
| sal-audit.md | SAL pipeline status, fact quality analysis |
| capability-layer-audit.md | Gap ledger analysis, compiler path bug |
| skill-inventory-and-gaps.md | Skill inventory, QName gaps in skills |
| autonomous-supervisor-audit.md | Validator count, continuation state, missing validators |
| lane-separation-and-collision-risk.md | Lane boundary map, collision risk matrix |
| backfill-facility-design.md | Updated backfill design (design-only, not built) |
| gate11-readiness-review.md | Per-product Gate 11 readiness status |
| product-deepening-readiness-plan.md | Stop/go gate, pilot selection, expansion rules |
| system-gap-matrix.yaml | 11 gaps with severity, root cause, taskcard ID |
| taskcards.yaml | 8 governed taskcards |
| next-agent-execution-prompt.md | Exact steps for next sprint |
| final-verdict.md | READY_AFTER_TARGETED_MACHINERY_REPAIRS verdict |
| evidence-index.md | This file |

## Live Evidence Collected

| Evidence | Tool Used | Result |
|----------|-----------|--------|
| QName compliance scan | qname_structure_validator.py | FODS=COMPLIANT(15), FODT=COMPLIANT(8), others=NO_SPEC_CLASSES |
| FODS Python test run | pytest tests/python/fods/ | 44 passed, 32 collection errors |
| SAL facts inspection | Python json.load | 4987 FODS facts, source=workbench_verified |
| verified-facts-review analysis | Python yaml.safe_load | 4991 facts, generated_by=TCA-010 auto-seed |
| .NET FODS source inspection | Read FodsDocument.cs | 1293 LOC, 30 methods, namespace FormatFactory.Fods |
| Gap ledger inspection | Python json.load | 958 gaps (932 closed, 26 open) |
| Plan lock inspection | Python json.load | TERMINAL_CLOSED, track_type=product |
| Continuation signal | Python json.load | state=YES, iter=10 |
| Git status | git status | 6 modified, 4 untracked |
| Capability compiler inspection | Read capability_compiler.py | Wrong SAL path identified |
| SAL master runner inspection | Grep + Read | workbench integration confirmed but auto-seed source |

## Prior Audit Reference

Prior audit: reports/ff-machinery-readiness-audit-20260621-23d1333/
Prior verdict: NOT_READY_REPAIR_MACHINERY_FIRST
Current verdict: READY_AFTER_TARGETED_MACHINERY_REPAIRS

Delta: 17 commits applied between audits. Key improvements: spec/ stubs, SAL pipeline wiring,
plan lock cleared. Key remaining: test errors, uncommitted work, auto-seeded facts, wrong compiler path.

## Gap Between Claims and Evidence

| Claim | Evidence Quality | Assessment |
|-------|-----------------|------------|
| "4987 SAL facts verified" | Yellow — auto-seeded by TCA-010 downgrade pass | PARTIAL |
| "QName COMPLIANT for FODS/FODT" | Green — live validator run | PROVEN |
| "SAL idempotency fixed" | Yellow — commit message claim, not live tested | CLAIMED |
| "Gate 11 G11-G approved" | Gray — reference in prior audit, code says NOT release-ready | UNCONFIRMED |
| "932 capability gaps closed" | Red — status set by sprint tool, not by independent evidence | INFLATED |
| "1490 tests pass" | Green — session-resume.md confirmed ACCEPTED sprint | PROVEN |
