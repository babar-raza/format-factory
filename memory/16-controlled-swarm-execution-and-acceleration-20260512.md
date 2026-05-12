# Memory 16 — Controlled Swarm Execution and Acceleration

**Created:** 2026-05-12
**Sprint:** POST-FODT-GATE10-CONTROLLED-SWARM-001 (Lane M)
**Scope:** Key patterns and decisions from FODT Gate 10 approval + controlled swarm execution

---

## 1. Controlled Swarm Model (Established This Sprint)

The controlled swarm model separates concerns across named lanes with explicit ownership:
- **Coordinator** owns shared files (registry, master-plan, taskcards, AGENTS.md, GOVERNANCE.md)
- **Lanes** operate in isolated file scopes
- **Lane ownership matrix** at `.local/<swarm-id>/lane-ownership-matrix.md` prevents conflicts
- Integration happens in Phase 2 (coordinator reviews all lane outputs before any merging)

Lanes in POST-FODT-GATE10-CONTROLLED-SWARM-001:
- Lane A: audit (reports/audit/ scope only)
- Lane B: tooling acceleration (tools/evidence/, tests/evidence/ scope only)
- Lane C: secondary sprint S-F2F-05 (acquisition-packs/_families/ + tests/playbook/ scope only)
- Lane D: planning documents (reports/planning/ + taskcards/ scope only, no registry changes)
- Lane M: memory + governance docs

## 2. ACCEL-003 Two-Pass Auto-Proof (Implemented Lane B)

`build_auto_proof_bundle()` function in `tools/evidence/build_evidence_bundle.py`:
- Pass 1: Write placeholder proof → build candidate zip → validate → extract metrics
- Pass 2: Write real proof with sha256/entries/bytes/metadata → rebuild final → validate
- CLI: `--auto-proof` flag on build_evidence_bundle.py (backwards compatible)
- `sprint_id` extracted from contract file content (not filename) to avoid METADATA_IDENTITY mismatch
- Test contracts must use `emergency_blocker_bundle: true` to bypass git-clean during test isolation
- 6/6 ACCEL-003 tests PASS (tests/evidence/test_auto_proof_bundle.py)

Key learning: `require_clean_git: false` only affects the validator; the builder ALWAYS fails on dirty git unless `emergency_blocker_bundle: true` is set in the contract.

## 3. S-F2F-05 ODF-Flat Family Playbook (Completed Lane C)

Family playbook at `acquisition-packs/_families/odf-flat/`:
- `playbook.yaml`: `playbook_kind: family_playbook`, covers all 5 formats (fods, fodt, fodp, fodg, fodb)
- `reuse-policy.md`: `inherited_gate_approval: false` — EXPLICITLY PROHIBITS inheritance
- `format-overrides.yaml`: fods+fodt=gates_1_through_10_passed; fodp/fodg/fodb=candidate_only

Schema fix required: `reuse_level: partial` is not valid; correct value is `reuse_level: adapt`.
Valid reuse_level enum: `['none', 'full', 'adapt', 'guide', 'new']`

9/9 tests PASS at `tests/playbook/test_odf_flat_family_playbook.py`

## 4. METADATA_IDENTITY Check Pattern

When writing proof files for evidence bundles, the sprint/contract ID line must use:
```
contract_id: SPRINT-ID-001
```
NOT:
```
Contract: sprint-name-without-suffix.yaml
```
Reason: The validator regex extracts yaml filenames and compares against sprint_id. If the filename omits the `-001` suffix that the sprint_id has, it creates a spurious identity mismatch.

## 5. DEC-033 and Gate 11 Status

- DEC-033: UNRESOLVED — human decision required before any .NET source
- Recommended: Option B (.NET Commercial Only) — Python covers FOSS obligation
- Gate 11 blocked for both FODS and FODT until DEC-033 resolves
- Python FOSS source complete and independent: src/python/fods/ and src/python/fodt/
- Execution-ready taskcards created: DEC-033-resolution-execution-plan.md + FODT-GATE11-readiness-execution-plan.md
- .NET target framework: net10.0 LTS recommended (9.0.200 near EOL)

## 6. FODT Gate 10 Approval Record

- Approved: Babar Raza, 2026-05-11
- TC-0052 completed; Phase 4 Python FODT implementation done
- Commit faed6da: 22 files; 6 pre-existing files classified ACCEPTED_WITH_NOTE
- Bundle: BUNDLE_VALIDATION: PASS (560 entries, 1,373,735 bytes, 30 metadata)
- FODT is now fully complete through Gate 10 (Python FOSS)

## 7. Gate 10 Scope Audit Protocol (Lane A Pattern)

When auditing a gate approval commit:
1. Verify all expected files are present in the commit
2. Classify unexpected files: ACCEPTED_WITH_NOTE (no blockers) vs BLOCKED
3. Categories: gate-work, context-enrichment, memory-sync, documentation-update
4. Unexpected files that are pre-existing content (not new work) are ACCEPTED_WITH_NOTE
5. Record in `reports/audit/<format>/gate<N>-approval-and-<commit>-scope-audit-<date>.md`

## 8. Pytest Availability (Windows)

On this project's Windows environment, pytest is installed to user site-packages.
Use: `PYTHONPATH="C:/Users/prora/AppData/Roaming/Python/Python313/site-packages" python -m pytest ...`
Or use the existing pytest in PATH if available via venv.
