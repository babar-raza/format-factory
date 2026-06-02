# Supervisor-Generated Next Sprint Prompt
# Source sprint: FORMAT-FACTORY-R92-DECLARATION-MATERIALIZER-WORK-ITEM-GRADING-ACCELERATION-POC-MAINSTREAM-MEGA-TRAIN-001
# Generated: 2026-06-02T16:10:47.800817
# ADVISORY ONLY — not a Format Factory authority document
# This is INPUT to the next sprint, not a gate approval or commit authorization.

---

## Sprint Focus
ADVANCE: Continue normal mega-train lanes

## Prior Sprint Summary
- Sprint ID: FORMAT-FACTORY-R92-DECLARATION-MATERIALIZER-WORK-ITEM-GRADING-ACCELERATION-POC-MAINSTREAM-MEGA-TRAIN-001
- Evidence verdict: ACCEPTED
- Tests: 5179 passed, 0 failed, 11 skipped
- Autonomous continue: True

## Section 1: New Product Work (Advisory — Always Execute)
- [pending] TASK-001: Select governed product gaps and validate the product-code ledger
- [approval-blocked] TASK-002: Commit uncommitted product code and build sprint evidence bundle
- [approval-blocked] TASK-003: Advance FODS Gate 11 commercial readiness
- [approval-blocked] TASK-004: Advance FODT Gate 11 commercial readiness
- [blocked] TASK-005: Open ZST Gate 11
- [pending] TASK-006: Work on open taskcard: ABW-GATE4-001-parser-prototype
- [pending] TASK-007: Work on open taskcard: AI-USAGE-LEDGER-AND-METRICS
- [pending] TASK-008: Work on open taskcard: EVIDENCE-HYGIENE-ENFORCEMENT
- [pending] TASK-009: Product deepening: commercial-net-fods-dogfood-status-fods-to-csv-dotnet — dogfood_status.fods_to_csv_dotnet
- [pending] TASK-010: Product deepening: commercial-net-fods-dogfood-status-fods-to-html-dotnet — dogfood_status.fods_to_html_dotnet
- [pending] TASK-011: Product deepening: commercial-net-fodt-dogfood-status-fodt-to-markdown-dotnet — dogfood_status.fodt_to_markdown_dotnet
- [pending] TASK-012: Product deepening: commercial-net-fodt-dogfood-status-fodt-to-txt-dotnet — dogfood_status.fodt_to_txt_dotnet
- [pending] TASK-013: Product deepening: foss-reduced-sylk-python-status-write-sylk — python_status.write_sylk
- [pending] TASK-014: Advance one dogfood export path using a Format Factory library
- [pending] TASK-015: Build package artifacts and run installed-workflow proof
- [pending] TASK-016: Write evidence declaration and run supervisor autonomous-cycle

## Section 2: Rework / Repair (Advisory — Fix Before Closeout)
None

## Contradictions Context
None

## Non-Negotiable Rules (always apply)
1. No push without explicit user authorization.
2. No commit without explicit user authorization.
3. No gate self-approval.
4. No active .vscode/mcp.json without MODE 4 approval.
5. No Task Master / Ruflo init without MODE 3+ authorization.
6. Load `.local/supervisor/selected-product-gaps.json` and `.supervisor/skill-registry.yaml` before product work.
7. All gate closures require human approval (gates 1-11).
8. Format Factory authority is final — supervisor is advisory only.
9. No direct ad-hoc `src/` edits. Use a governed skill or generated execution handoff.
10. Every `src/` edit requires an entry in `reports/r90/product-code-change-ledger.json`.

## Evidence Requirements for Next Sprint
- Write `.local/evidences/<run_id>/evidence-declaration.yaml`
- Run `python tools/supervisor/supervisor_loop.py autonomous-cycle --declaration .local/evidences/<run_id>/evidence-declaration.yaml`
- ZIP bundle export is optional for archive or external transfer
- Final verdict must contain: VERDICT: <enum>
- All SHAs must be filled (no PENDING markers in final state)
- Tests: 0 failures required

## Suggested Lane Manifest (Advisory)
- Lane C0: Coordinator — integration, manifest authority, stop-gate monitoring
- Lane C1: Governance discovery — read AGENTS.md, GOVERNANCE.md, master-plan state
- Lane C2: Repair lanes — address any open contradictions from prior sprint
- Lane C3: Governed implementation — selected gaps, skill registry, product-code ledger
- Lane C4: Dogfood export — use a Format Factory-produced library
- Lane C5: Package/install proof — build physical artifacts and run installed workflows
- Lane C6: Evidence — declaration + autonomous-cycle
- Lane C7: Adversarial — challenge all claims before finalizing

## Acceptance Criteria Per Lane
(Fill from open taskcards in taskcards/ directory)

## Project Memory Context
```
- governed_src_change: src/python/ppm/ppm_to_pgm.py (new, /add-dogfood-export skill)
- new_tests: 5 (test_r90_ppm_to_pgm_dogfood.py)
- commercial_product_ready: false
- gate_11_approved: false
- publication_authorized: false

## Entry: FORMAT-FACTORY-R91-AUTONOMOUS-SUPERVISOR-DECLARATION-GRADING-POC-ACCELERATION-MAINSTREAM-MEGA-TRAIN-001
- timestamp: 2026-06-02
- status: COMPLETE
- verdict: R91_AUTONOMOUS_SUPERVISOR_HEALED_POC_DEEPENED_PUBLICATION_BLOCKED
- supervisor_flow_healed: true (declaration→grading→rework+new-work→continuation)
- inherited_failures_repaired: 12 (R84 sidecar git-rm, R88 contract_id, test tolerance fixes)
- python_tests: 4675 passed, 0 failed, 18 skipped
- dotnet_fods_tests: 199 (191 baseline + 8 new SetCellValue)
- dotnet_fodt_tests: 184 (176 baseline + 8 new SaveToFile)
- dotnet_netpbm_tests: 104 (94 baseline + 10 new SetPixelColor)
- python_new_tests: 7 (test_r91_sylk_csv_hardening.py)
- dotnet_total: 487
- governed_src_changes:
  - src/net/fods/FodsDocument.cs (SetCellValue API, R91-GOVERNED-DOTNET-FODS-SETCELLVALUE-001)
  - src/net/fodt/FodtDocument.cs (SaveToFile alias, R91-GOVERNED-DOTNET-FODT-SAVETOFILE-001)
- acceleration_layer_repairs:
  - autonomous_cycle.py: true_with_rework continuation mode + grade output copy
  - policies.yaml: rework_continues_safe_lanes + inherited_failure_isolation
  - generate_supervisor_packet.py: product-first next-sprint sections
- commercial_product_ready: false
- gate_11_approved: false
- publication_authorized: false

## Entry: FORMAT-FACTORY-R92-DECLARATION-MATERIALIZER-WORK-ITEM-GRADING-ACCELERATION-POC-MAINSTREAM-MEGA-TRAIN-001
- timestamp: 2026-06-02
- status: COMPLETE
- verdict: R92_DECLARATION_MATERIALIZER_SKILL_EXPANSION_POC_DEEPENED_PUBLICATION_BLOCKED
- declaration_materializer: tools/supervisor/materialize_declared_evidence.py (Train B)
- review_package_builder: tools/supervisor/build_declaration_review_package.py (Train C)
- r91_work_item_grades: 12/12 ACCEPTED (Train A)
- new_skills: add-dotnet-object-model-feature, add-roundtrip-test, add-installed-package-example (Train J)
- governed_src_changes:
  - src/net/fods/FodsDocument.cs (GetSheetNames API, R92-GOVERNED-DOTNET-FODS-GETSHEETNAMES-001)
  - src/net/fodt/FodtDocument.cs (GetHeadingParagraphs API, R92-GOVERNED-DOTNET-FODT-GETHEADINGPARAGRAPHS-001)
  - src/net/netpbm/Model/NetpbmImage.cs (FillRegion API, R92-GOVERNED-DOTNET-NETPBM-FILLREGION-001)
- dotnet_fods_tests: 207 (199 baseline + 8 new GetSheetNames)
- dotnet_fodt_tests: 193 (184 baseline + 8 new GetHeadingParagraphs + 1 other)
- dotnet_netpbm_tests: 112 (104 baseline + 8 new FillRegion)
- dotnet_total: 512
- python_tests: 2467 (tests/python/) or 2570 (including supervisor/evidence)
- product_ledger_entries: 5 governed changes (3 R92 + 2 R91 + prior backfills)
- commercial_product_ready: false
- gate_11_approved: false
- publication_authorized: false
```

---
END OF SUPERVISOR-GENERATED NEXT SPRINT PROMPT
