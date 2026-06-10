# R106 Supervisor Sprint Preflight
Sprint: FORMAT-FACTORY-SUPERVISOR-R106-STREAM-CLEAN-CYCLE-ENFORCEMENT-RAW-LOGS-AND-STRICT-GRADING-001
PYTHON: .local/venv/Scripts/python

## Mandatory Reads
- [x] CLAUDE.md
- [x] reports/supervisor/session-resume.md — Last: Supervisor-R105, ACCEPTED, 686 passed
- [x] reports/supervisor/approval-gates.md — AUTONOMOUS_CONTINUE: YES
- [x] .supervisor/policies.yaml — max_iterations: 12, max_consecutive_accept_with_limitations: 2
- [x] tools/supervisor/inspect_declared_evidence.py — R105 :: suffix fix applied
- [x] tools/supervisor/grade_declared_work.py — R104 ACCEPTED_VERIFIED proof rules
- [x] tools/supervisor/materialize_declared_evidence.py — R104 all-changed-files diffs
- [x] tools/supervisor/build_declaration_review_package.py — R104 changed-files + stream identity
- [x] tools/supervisor/autonomous_cycle.py — continuation states, bridge, signal

## R105 Package Review
- 5 ACCEPTED_VERIFIED, 1 ACCEPTED_WITH_LIMITATIONS (reports-only, correct)
- stream_identity_warnings: context-pack/evidence-review/contradictions reference Skills
- Raw logs: not captured (deferred)
- Dirty state: M inspect_declared_evidence.py, ?? test_r105*, ?? reports/supervisor-r105/

## R106 Scope
- Lane A: R105 review and proof-gap classification
- Lane B: Raw logs documentation (architectural — not capturable this sprint)
- Lane C: Stream-primary cleanup documentation
- Lane D: Strict grading tests (node IDs, report-only, empty tests)
- Lane E: Materializer/package enforcement verification
- Lane F: Autonomous-cycle enforcement verification
- Lane G: Clean closure (dirty state classification)
- Lane H: Dashboard + next prompt
- Lane I: Final IV + evidence closeout
