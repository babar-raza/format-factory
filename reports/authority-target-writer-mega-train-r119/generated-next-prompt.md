# Generated Next Sprint Prompt
Sprint: FORMAT-FACTORY-AUTHORITY-LAYERS-AND-TARGET-WRITER-MEGA-TRAIN-R119-001
Generated: 2026-06-05

## Context

The R119 sprint completed verification and documentation of:
- FormatFactory.Csv (15 tests), Html (12), Txt (8), Markdown (11) — all built and wired
- FODS CSV integration verified (547/547 FODS tests pass)
- FODT TXT + Markdown integration verified (520/520 FODT tests pass)
- BLOCKED_GAP_IDS = frozenset() — all 4 architecture-blocked gaps unblocked
- RCA evidence quality repair methodology documented
- Gap queue policy confirmed and tested (23/23 new tests pass)
- Evidence detection hardening (16/16 new tests pass)

## Recommended Next Sprint: RCA R2 Proof Graph Wiring

### Sprint ID
FORMAT-FACTORY-RCA-R2-PROOF-GRAPH-WRITER-WIRING-001

### Objective
Wire the RCA proof graph to the 4 newly built target writer libraries, changing
FODS and FODT export claims from PARTIAL → READY in the proof graph.

### Required Work Items
1. Add TargetWriterLibrary nodes (4): ff-csv-writer-net-001, ff-html-writer-net-001, ff-txt-writer-net-001, ff-md-writer-net-001
2. Add ExporterIntegration edges: claim → writer → exporter → tests → dogfood
3. Re-run all 5 pilots (Netpbm, FODS, FODT, ZST, DIF)
4. Expected result: FODS PARTIAL → READY (CSV+HTML), FODT PARTIAL → READY (TXT+Markdown)
5. Update poc-targets.yaml proposed delta for 4 claims
6. Produce dogfood samples for HTML/TXT/Markdown exports
7. Add tests: RCA R2 pilot tests (extend tests/requirement_capability_authority/)

### Input Resources
- `reports/authority-target-writer-mega-train-r119/workahead/rca-next-fixtures.md`
- `reports/authority-target-writer-mega-train-r119/workahead/next-writer-readiness-matrix.json`
- `reports/spec-authority-r3-closure-repair/rca-r2-input-packet.json` (frozen RCA snapshot)
- `tests/requirement_capability_authority/test_r119_export_target_writer_policy.py` (policy tests)

### Prohibitions
- No gate approval
- No git push without user authorization
- No poc-targets.yaml direct mutation
- No registry direct mutation
- No FODT→HTML implementation (separate sprint)

### STOP_REASON_ADVISORY
- gate_11_required: STOP_RELEASE_APPROVAL_PENDING — requires Babar Raza approval
- push_required: STOP_PUSH_APPROVAL_REQUIRED — requires user authorization
- All other work items: autonomous-continue eligible

## Alternative Next Sprint: Apply Registry Patches
If Babar Raza approves proposed patches:
- Apply `proposed-authority-updates/csv-writer-registry-patch.yaml` to registry
- Apply proposed capability delta to poc-targets.yaml
- Sprint ID: FORMAT-FACTORY-REGISTRY-PATCHES-AND-AUTHORITY-SYNC-001
