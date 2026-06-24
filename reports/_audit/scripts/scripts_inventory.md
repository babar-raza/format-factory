# Scripts Inventory — format-factory

Audit date: 2026-06-23

Legend:
- **Status:** active = referenced by CI/CLAUDE.md/commands; verified = callsite confirmed; unverified = no callsite found; dead = superseded or broken
- **Action:** keep = no change needed; move = relocate to canonical folder; merge = combine with another script; archive = move to .local/ or delete

---

## A. scripts/ (External Host Orchestration)

| Path | Type | Invoked By | Purpose | Risk | Status | Action | Notes |
|------|------|-----------|---------|------|--------|--------|-------|
| scripts/autonomous_external_host.ps1 | PowerShell | Manual (external host proof) | Bootstrap external autonomous host, unsets CLAUDECODE | HIGH | active | keep | Calls tools/supervisor/external_host_loop.py |
| scripts/autonomous_external_host.sh | Bash | Manual (external host proof) | Same as .ps1, Bash/WSL variant | HIGH | active | keep | Cross-platform pair |
| scripts/start_format_factory_orchestrator.ps1 | PowerShell | Manual | Main orchestrator launcher | HIGH | active | keep | -MaxCycles, -Backend, -Resume params |
| scripts/start_format_factory_orchestrator.cmd | CMD | Manual | CMD batch launcher for orchestrator | HIGH | active | keep | Calls autonomous_orchestrator.py |
| scripts/run_format_factory_orchestrator_once.ps1 | PowerShell | Manual (testing) | Single-cycle test run | MEDIUM | active | keep | Resume verification |
| scripts/install_format_factory_orchestrator_task.ps1 | PowerShell | Governance-gated | Task Scheduler proposal (DryRun=true) | HIGH | active | keep | BLOCKED: requires explicit auth |

## B. .github/workflows/ (CI/CD)

| Path | Type | Invoked By | Purpose | Risk | Status | Action | Notes |
|------|------|-----------|---------|------|--------|--------|-------|
| .github/workflows/ci.yml | YAML | GitHub Actions | Lint, test, governance smoke, .NET build | LOW | active | keep | Calls tools/test_runner.py |
| .github/workflows/release.yml | YAML | GitHub Actions (tag) | Build wheel, PyPI upload | MEDIUM | active | keep | TWINE_PASSWORD secret |

## C. tools/ (Root-Level)

| Path | Type | Invoked By | Purpose | Risk | Status | Action | Notes |
|------|------|-----------|---------|------|--------|--------|-------|
| tools/test_runner.py | Python | ci.yml L45 | Layered test runner with JSON output | LOW | active | keep | Critical CI infrastructure |
| tools/health_check.py | Python | Unverified | Quick repo health check | LOW | unverified | keep | Likely manual use |
| tools/audit_deepening_tests.py | Python | Sprint evidence | Classify arithmetic vs mixed deepening tests | LOW | verified | keep | 697/1009 classified |
| tools/build_cross_format_index.py | Python | Sprint evidence | Build registry/cross-format-test-index.yaml | LOW | verified | keep | 20 formats, 5193 entries |
| tools/audit_gap_ledger_sal_refs.py | Python | Sprint evidence | Audit gap-ledger SAL references | LOW | verified | keep | |
| tools/audit_parity_compliance.py | Python | Unverified | Audit spec-parity compliance | LOW | unverified | keep | |
| tools/audit_qname_coverage.py | Python | Unverified | Audit QName coverage | LOW | unverified | keep | |
| tools/audit_sal_to_qname.py | Python | Unverified | Audit SAL-to-QName mapping | LOW | unverified | keep | |
| tools/close_comm_gaps.py | Python | Unverified | Close commercial capability gaps | LOW | unverified | keep | |
| tools/close_fods_fodt_ppm_gaps.py | Python | Unverified | Close FODS/FODT/PPM gaps | LOW | unverified | keep | |
| tools/close_xcf_zst_gaps.py | Python | Unverified | Close XCF/ZST gaps | LOW | unverified | keep | |

## D. tools/supervisor/ (Critical — 164 files, top 30 shown)

| Path | Type | Invoked By | Purpose | Risk | Status | Action |
|------|------|-----------|---------|------|--------|--------|
| tools/supervisor/autonomous_cycle.py | Python | CLAUDE.md L294, supervisor_loop.py | Core autonomous cycle (2135 LOC) | HIGH | active | keep |
| tools/supervisor/check_continuation.py | Python | CLAUDE.md L321 | Continuation gate | HIGH | active | keep |
| tools/supervisor/sprint_executor.py | Python | CLAUDE.md L430 | Headless sprint runner | HIGH | active | keep |
| tools/supervisor/supervisor_loop.py | Python | CLAUDE.md L294 | Supervisor pipeline (autonomous-cycle subcommand) | HIGH | active | keep |
| tools/supervisor/governance_validators.py | Python | governance_validator_runner.py | 48+ governance validators (2953 LOC) | HIGH | active | keep |
| tools/supervisor/governance_validators_ext.py | Python | governance_validator_runner.py | Extended validators (V49-V63) | HIGH | active | keep |
| tools/supervisor/governance_validator_runner.py | Python | autonomous_cycle.py | Orchestrates all validators | HIGH | active | keep |
| tools/supervisor/grade_declared_work.py | Python | autonomous_cycle.py | Evidence grading engine | MEDIUM | active | keep |
| tools/supervisor/write_plan_lock.py | Python | CLAUDE.md L13/22 | Plan lock management | MEDIUM | active | keep |
| tools/supervisor/check_system_healing_gate.py | Python | autonomous_cycle.py | System healing gate | MEDIUM | active | keep |
| tools/supervisor/build_declaration_review_package.py | Python | CLAUDE.md L308 | Evidence ZIP packager | LOW | active | keep |
| tools/supervisor/sprint_executor_validate.py | Python | CLAUDE.md L285 | Declaration pre-validator | LOW | active | keep |
| tools/supervisor/reset_track_signal.py | Python | CLAUDE.md L104 | Session mismatch recovery | MEDIUM | active | keep |
| tools/supervisor/update_source_baseline.py | Python | CLAUDE.md (healing sprints) | Baseline updater | MEDIUM | active | keep |
| tools/supervisor/external_host_loop.py | Python | scripts/*.ps1/*.sh | External host execution | HIGH | active | keep |
| tools/supervisor/autonomous_orchestrator.py | Python | scripts/*.cmd/*.ps1 | Multi-cycle orchestrator | HIGH | active | keep |
| tools/supervisor/continuation_selector.py | Python | check_continuation.py | Signal selection logic | MEDIUM | active | keep |
| tools/supervisor/continuation_identity.py | Python | autonomous_cycle.py | Session identity pinning | MEDIUM | active | keep |
| tools/supervisor/stop_reason_adjudicator.py | Python | Autonomous loop | Stop reason classification | MEDIUM | active | keep |
| tools/supervisor/generate_next_worker_prompt.py | Python | autonomous_cycle.py | Next-sprint.md generator | MEDIUM | active | keep |
| tools/supervisor/materialize_and_review.py | Python | Commands | Evidence materialization | LOW | active | keep |
| tools/supervisor/validate_skill_transcript.py | Python | Commands | Skill transcript validation | LOW | active | keep |
| tools/supervisor/ai_supervisor_advisor.py | Python | Autonomous cycle (optional) | AI advisory (LLM-dependent) | LOW | verified | keep |
| tools/supervisor/ai_product_brain.py | Python | Autonomous cycle (optional) | AI product brain (LLM-dependent) | LOW | verified | keep |
| tools/supervisor/ai_evidence_critic.py | Python | Autonomous cycle (optional) | AI evidence grading (LLM-dependent) | LOW | verified | keep |
| tools/supervisor/build_proof_graph_iter001.py | Python | Unverified | Proof graph builder (iteration 1) | LOW | unverified | archive? |
| tools/supervisor/build_proof_graph_iter002.py | Python | Unverified | Proof graph builder (iteration 2) | LOW | unverified | archive? |
| tools/supervisor/build_proof_graph_iter003.py | Python | Unverified | Proof graph builder (iteration 3) | LOW | unverified | archive? |
| tools/supervisor/capture_raw_logs.py | Python | Unverified | Raw log capture | LOW | unverified | keep |
| tools/supervisor/generate_sample_outputs.py | Python | Unverified | Sample output generation | LOW | unverified | keep |

(134 additional supervisor scripts not shown — see full inventory via `find tools/supervisor -name "*.py"`)

## E. tools/validators/ (Source Architecture)

| Path | Type | Invoked By | Purpose | Risk | Status | Action |
|------|------|-----------|---------|------|--------|--------|
| tools/validators/source_structure_validator.py | Python | governance_validators.py | LOC/function caps, architecture governance | MEDIUM | active | keep |
| tools/validators/validate_source_architecture.py | Python | governance_validators.py | Architecture validation | MEDIUM | active | keep |
| tools/validators/analytics_bucket_detector.py | Python | governance_validators.py | Analytics separation detection | LOW | active | keep |
| tools/validators/qname_structure_validator.py | Python | governance_validators.py | QName structure validation | LOW | active | keep |
| tools/validators/monolith_detection_validator.py | Python | governance_validators.py | Monolith detection | MEDIUM | active | keep |
| (3 more) | Python | Various | Other validators | LOW | verified | keep |

## F. .local/ One-Off Scripts (47 files — NOT committed)

| Path | Type | Invoked By | Purpose | Risk | Status | Action |
|------|------|-----------|---------|------|--------|--------|
| .local/create_metadata.py | Python | One-time | MEMORY-AI-DIR-SYNC data migration | LOW | dead | archive |
| .local/create_closure_metadata.py | Python | One-time | Closure sprint metadata | LOW | dead | archive |
| .local/create_methodology_metadata.py | Python | One-time | Methodology sprint metadata | LOW | dead | archive |
| .local/create_linkage_metadata.py | Python | One-time | Linkage sprint metadata | LOW | dead | archive |
| .local/create_repair_metadata.py | Python | One-time | Repair sprint metadata | LOW | dead | archive |
| .local/create_repair_v2_metadata.py | Python | One-time | Repair V2 metadata | LOW | dead | archive |
| .local/create_repair_v3_metadata.py | Python | One-time | Repair V3 metadata | LOW | dead | archive |
| .local/create_run044_metadata.py | Python | One-time | Run044 metadata | LOW | dead | archive |
| .local/create_iv_metadata.py | Python | One-time | IV sprint metadata | LOW | dead | archive |
| .local/create_sprint_meta.py | Python | One-time | Sprint metadata | LOW | dead | archive |
| .local/fix_ledger_sources.py | Python | One-time | Fix malformed ledger source_files | LOW | dead | archive |
| .local/fix_ledger_hashes.py | Python | One-time | Fix ledger content hashes | LOW | dead | archive |
| .local/fix_ledger_comprehensive.py | Python | One-time | Comprehensive ledger repair | LOW | dead | archive |
| .local/fix_healing_loop.py | Python | One-time | Fix healing loop state | LOW | dead | archive |
| .local/fix_fods_p4.py | Python | One-time | Fix FODS P4 data | LOW | dead | archive |
| .local/fix_fodt_packet.py | Python | One-time | Fix FODT packet data | LOW | dead | archive |
| .local/fix_fods_c4.py | Python | One-time | Fix FODS C4 data | LOW | dead | archive |
| .local/fix_evidence_tests.py | Python | One-time | Fix evidence test data | LOW | dead | archive |
| .local/tmp_create_registries.py | Python | One-time | Create 18 QName registries (TC-HARD-008) | LOW | dead | archive |
| .local/tmp_backfill_ledger.py | Python | One-time | Backfill product-deepening-ledger | LOW | dead | archive |
| .local/tmp_gap_ledger_update.py | Python | One-time | Gap ledger update | LOW | dead | archive |
| .local/tmp_generate_backfill_csv.py | Python | One-time | Generate backfill CSV | LOW | dead | archive |
| .local/tmp_ledger_update.py | Python | One-time | Ledger update | LOW | dead | archive |
| .local/tmp_ledger_r430.py | Python | One-time | Ledger R430 entries | LOW | dead | archive |
| .local/tmp_ledger_r431_r433.py | Python | One-time | Ledger R431-433 entries | LOW | dead | archive |
| .local/gen_samples.py | Python | One-time | ODS/ODF sample generation | LOW | dead | archive |
| .local/gen_ontology.py | Python | One-time | Ontology generation | LOW | dead | archive |
| .local/gen_manifest_r103.py | Python | One-time | R103 manifest generation | LOW | dead | archive |
| .local/gen_manifest_r104.py | Python | One-time | R104 manifest generation | LOW | dead | archive |
| .local/gen_manifest_r105.py | Python | One-time | R105 manifest generation | LOW | dead | archive |
| .local/gen_r103_artifacts.py | Python | One-time | R103 artifact generation | LOW | dead | archive |
| .local/gen_r104_transcripts.py | Python | One-time | R104 transcript generation | LOW | dead | archive |
| .local/gen_transcripts_r102.py | Python | One-time | R102 transcript generation | LOW | dead | archive |
| .local/build_r103_package.py | Python | One-time | R103 package builder | LOW | dead | archive |
| .local/write_e2e_pilot.py | Python | One-time | E2E pilot writer | LOW | dead | archive |
| .local/fods_workflow_test.py | Python | One-time | FODS workflow smoke test | LOW | dead | archive |
| .local/fodt_workflow_test.py | Python | One-time | FODT workflow smoke test | LOW | dead | archive |
| .local/r51-fods-smoke.py | Python | One-time | R51 FODS smoke test | LOW | dead | archive |
| .local/r51-fods-object-model-smoke.py | Python | One-time | R51 FODS object model smoke | LOW | dead | archive |
| .local/r51-fodt-smoke.py | Python | One-time | R51 FODT smoke test | LOW | dead | archive |
| .local/run_tests.py | Python | One-time | Quick test runner | LOW | dead | archive |
| .local/run_anti_bypass_demos.py | Python | One-time | Anti-bypass demo runner | LOW | dead | archive |
| .local/add_png_ledger.py | Python | One-time | Add PNG ledger entry | LOW | dead | archive |
| .local/add_fodt_png_ledger.py | Python | One-time | Add FODT PNG ledger entry | LOW | dead | archive |
| .local/append_s31.py | Python | One-time | Append S31 data | LOW | dead | archive |
| .local/verify_r284.py | Python | One-time | Verify R284 data | LOW | dead | archive |
| .local/verify_r284b.py | Python | One-time | Verify R284b data | LOW | dead | archive |

## G. prototypes/ (Format Parsers)

| Path | Type | Invoked By | Purpose | Risk | Status | Action |
|------|------|-----------|---------|------|--------|--------|
| prototypes/by-format/fods/fods_parser.py | Python | Pre-production prototype | FODS parser prototype | LOW | verified | keep |
| prototypes/by-format/fods/validate_against_samples.py | Python | Pre-production prototype | FODS sample validator | LOW | verified | keep |
| prototypes/by-format/fodt/fodt_parser.py | Python | Pre-production prototype | FODT parser prototype | LOW | verified | keep |
| prototypes/by-format/fodt/validate_against_samples.py | Python | Pre-production prototype | FODT sample validator | LOW | verified | keep |
| prototypes/by-format/abw/abw_parser.py | Python | Pre-production prototype | ABW parser prototype | LOW | verified | keep |
| prototypes/by-format/fodg/fodg_parser.py | Python | Pre-production prototype | FODG parser prototype | LOW | verified | keep |
| prototypes/by-format/fodp/fodp_parser.py | Python | Pre-production prototype | FODP parser prototype | LOW | verified | keep |
| prototypes/by-format/gnumeric/gnumeric_parser.py | Python | Pre-production prototype | Gnumeric parser prototype | LOW | verified | keep |
| prototypes/by-format/zst/frame_header.py | Python | Pre-production prototype | ZST frame header parser | LOW | verified | keep |
| prototypes/by-format/zst/zst_probe.py | Python | Pre-production prototype | ZST format probe | LOW | verified | keep |
| prototypes/by-format/zst/validate_corpus.py | Python | Pre-production prototype | ZST corpus validator | LOW | verified | keep |

## H. Other Locations

| Path | Type | Invoked By | Purpose | Risk | Status | Action |
|------|------|-----------|---------|------|--------|--------|
| packaging/python/build-local-packages.py | Python | Manual / sprint evidence | Local wheel/sdist builder | LOW | active | keep |
| examples/dogfood_csv_export.py | Python | Manual example | CSV dogfood usage demo | LOW | active | keep |
| reports/repo-sharing-plan/untrack-commands-plan.sh | Bash (plan) | Manual review only | NOT EXECUTED (echo+exit 0) | LOW | dead | archive |
| drivers/python/getter_test.py.tmpl | Template | Test generation | Getter test driver template | LOW | active | keep |
| drivers/python/export_csv_test.py.tmpl | Template | Test generation | CSV export test template | LOW | active | keep |
| drivers/python/roundtrip_test.py.tmpl | Template | Test generation | Roundtrip test template | LOW | active | keep |
| drivers/python/append_test.py.tmpl | Template | Test generation | Append test template | LOW | active | keep |
| drivers/python/probe_test.py.tmpl | Template | Test generation | Probe test template | LOW | active | keep |
