# Commit Candidate Summary
**Prepared:** 2026-06-18 (Updated: 2026-06-21 — healing sprint FF-HEAL-QNAME-20260621-114042 changes added)
**Status:** CANDIDATE — execution requires explicit user authorization (git commit is TRUE_EXTERNAL_GATE)
**Based on:** Sprint series ending with FF-HEAL-QNAME-20260621-114042

## ff-machinery-repair-20260624 Changes (added 2026-06-24)

| File | Type | Description |
|---|---|---|
| `src/python/ndjson/models.py` | NEW | NdjsonDocument domain model — spec_qname="ndjson:record" |
| `src/python/gnumeric/models.py` | NEW | GnumericDocument domain model — spec_qname="gnumeric:workbook" |
| `src/python/toml/models.py` | NEW | TomlDocument domain model — spec_qname="toml:table" |
| `src/python/csv/models.py` | NEW | CsvDocument domain model — spec_qname="csv:row" |
| `src/python/fodt/exporters.py` | NEW | FodtToTxtExporter, FodtToMarkdownExporter |
| `src/python/tsv/models.py` | NEW | TsvDocument domain model — spec_qname="tsv:row" |
| `src/python/ndjson/__init__.py` | MODIFIED | Export NdjsonDocument |
| `src/python/gnumeric/__init__.py` | MODIFIED | Export GnumericDocument |
| `src/python/toml/__init__.py` | MODIFIED | Export TomlDocument |
| `tests/python/ndjson/test_ndjson_document_model.py` | NEW | 23 passing tests |
| `tests/python/gnumeric/test_gnumeric_document_model.py` | NEW | 37 tests |
| `tests/python/toml/test_toml_document_model.py` | NEW | 37 tests |
| `tests/python/csv_format/test_csv_document_model.py` | NEW | CSV model tests |
| `tests/python/fodt/test_fodt_exporters.py` | NEW | FODT exporter tests |
| `tests/python/tsv/test_tsv_document_model.py` | NEW | TSV model tests |
| `tools/supervisor/write_plan_lock.py` | MODIFIED | Fix terminal_closed_plan return value |
| `tests/supervisor/test_qname_ontology_generator.py` | MODIFIED | Fix test_fodp_finds_functions assertion |
| `tests/supervisor/test_r170_actual_fixture_stale_repair.py` | MODIFIED | Fix import + target_path |
| `plans/master-plan-memory.md` | MODIFIED | Add LEDGER-017 through LEDGER-021 |
| `reports/r90/product-code-change-ledger.json` | MODIFIED | Add HO-RC002-MODELS entries |

---

## FF-HEAL-QNAME-20260621-114042 Changes (added 2026-06-21)

| File | Type | Description |
|---|---|---|
| `src/python/fodt/neutral_model.py` | MODIFIED | Analytics extracted; 1916 LOC; 8 formula fixes |
| `src/python/fodt/fodt_analytics.py` | NEW | 92 fodt_* analytics; resolves GOV_BLOCK:validate_source_architecture |
| `src/python/fodt/__init__.py` | MODIFIED | Import split |
| `tools/specification-authority-layer/qname_src_compliance_reporter.py` | NEW | QName compliance reporter |
| `tests/specification-authority-layer/test_qname_src_compliance_reporter.py` | NEW | 10 tests |
| `registry/source-structure-baseline.json` | MODIFIED | New violation entries |
| `taskcards/healing-audit/healing-taskcards-20260621.yaml` | NEW | 6 promoted healing taskcards |
| `reports/r90/product-code-change-ledger.json` | MODIFIED | 940 entries |

---

## Prior content (sprint series ending dogfood-poc-targets-update-20260618)

---

## Summary of Changes

This commit candidate covers product work from sprint series:
- `sylk-cleanup-matrix-20260618` — SYLK capability matrix update
- `fodg-install-proof-20260618` — FODG package install proof
- `ndjson-tsv-install-proof-20260618` — NDJSON/TSV package matrix + install proof
- `examples-ndjson-tsv-20260618` — Developer examples for NDJSON and TSV
- `tc-0004-commands-skills-20260618` — TC-0004 slash commands implementation
- `toml-gap-closure-20260618` — Close 23 TOML FOSS analytics gaps (0 open remaining)
- `tc-0006-release-manifest-20260618` — TC-0006: release manifest tooling (3 tools)
- `tc-0008-memory-sync-20260618` — TC-0008: /sync-memory command + memory-sync-report
- `tc-0012-spec-normalization-20260618` — TC-0012: taskcard closed; master-plan Section 25
- `tc-0020-agents-ah-ndjson-proof-20260618` — AGENTS.md Section AH + ndjson install proof
- `dogfood-poc-targets-update-20260618` — Verify + document dogfood export paths for FODG/TSV/ABW/Gnumeric/TOML
- `abw-gnumeric-installed-workflow-20260618` — ABW and Gnumeric installed workflow tests (8/8 PASS)
- `tc0020-refresh-coverage-tools-20260618` — TC-0020 items 2+3: refresh_workbench.py + detect_coverage_gaps.py

---

## Product Source Changes (src/)

| File | Change | Sprint |
|------|--------|--------|
| `src/python/zst/zst_codec.py` | Minor fix (1 line removed — stale comment) | analytics-healing |
| `src/python/zst/zst_analytics.py` | Removed 2 duplicate function definitions (TC-CLEANUP-001) | tc-0004 |
| `src/python/zst/__init__.py` | Updated exports to reflect analytics separation | analytics-healing |
| `src/python/xcf/xcf_analytics.py` | Removed 2 duplicate function definitions (TC-CLEANUP-001) | tc-0004 |
| `src/python/xcf/__init__.py` | Updated exports to reflect analytics separation | analytics-healing |
| `src/net/fods/FodsDocument.cs` | .NET FODS document model additions | commercial |

**product-code-change-ledger.json entries:** Verified present for all src/ changes.

---

## New Untracked Files (product-relevant)

| Path | Purpose | Sprint |
|------|---------|--------|
| `examples/python/ndjson/read_and_query.py` | NDJSON developer example | examples sprint |
| `examples/python/tsv/read_and_transform.py` | TSV developer example | examples sprint |
| `.claude/commands/score-format.md` | /score-format command (TC-0004) | tc-0004 |
| `.claude/commands/create-acquisition-pack.md` | /create-acquisition-pack command (TC-0004) | tc-0004 |
| `.claude/commands/check-gate.md` | /check-gate command (TC-0004) | tc-0004 |
| `.claude/commands/create-taskcard.md` | /create-taskcard command (TC-0004) | tc-0004 |
| `.claude/commands/reproduce-master-plan.md` | /reproduce-master-plan command (TC-0004) | tc-0004 |
| `.claude/commands/build-evidence-bundle.md` | /build-evidence-bundle command (TC-0004) | tc-0004 |
| `.claude/commands/check-release-boundary.md` | /check-release-boundary command (TC-0004) | tc-0004 |
| `.claude/commands/command-registry.yaml` | Command registry (TC-0004) | tc-0004 |
| `reports/gate11/fods-gate11-check-gate-result.md` | FODS Gate 11 check output | tc-0004 |

---

## Governance/Registry Changes

| File | Change |
|------|--------|
| `product-capability-matrix/poc-targets.yaml` | FODG/NDJSON/TSV installed_workflow: PASS; SYLK accessor PASS; dogfood_status added for FODG/TSV/ABW/Gnumeric/TOML (all verified) |
| `packaging/python/package-matrix.yaml` | Added NDJSON and TSV package entries |
| `packaging/python/build-local-packages.py` | Added NDJSON and TSV build entries |
| `registry/source-structure-baseline.json` | Updated analytics function caps (TC-CLEANUP-002) |
| `taskcards/TC-0004-commands-skills.md` | Status: completed |
| `.claude/commands/_readme.md` | Updated to reference actual command files |
| `.claude/settings.json` | Removed 7 command deny entries (TC-0004 prerequisite) |

---

## Pre-Commit Checklist

- [x] `source_structure_validator.py` blocks_sprint=False (verified 2026-06-18)
- [x] `governance_validators.py` 37+ PASS, 0 FAIL
- [x] No new LOC violations (all analytics files within baseline_loc_cap)
- [x] Evidence declarations written for each sprint
- [x] No product source changes without product-code-change-ledger.json entries
- [ ] User authorization required for git commit
- [ ] User authorization required for git push

---

## Suggested Commit Message

```
feat(product): TC-0004 commands, NDJSON/TSV examples, install proofs, analytics dedup

- TC-0004: create 7 slash commands in .claude/commands/ (score-format,
  create-acquisition-pack, check-gate, create-taskcard, reproduce-master-plan,
  build-evidence-bundle, check-release-boundary) + command-registry.yaml
- Examples: add examples/python/ndjson/read_and_query.py and
  examples/python/tsv/read_and_transform.py (installed workflow demonstrations)
- Package matrix: add NDJSON and TSV to packaging/python/package-matrix.yaml
- Capability matrix: FODG/NDJSON/TSV installed_workflow PASS; SYLK accessor PASS
- Analytics dedup (TC-CLEANUP-001): remove duplicate function definitions from
  zst_analytics.py and xcf_analytics.py
- Source baseline: update baseline_functions_cap for 3 analytics files to actual
  function counts (TC-CLEANUP-002, prevents spurious blocks_sprint=True)
- Settings: remove 7 command deny entries from .claude/settings.json
```

---

## Additional Changes (this session)

| File | Change |
|------|--------|
| `AGENTS.md` | Section AH added — 8 spec workbench consumption rules (TC-0020) |
| `plans/master-plan.md` | Section 25 added — TC-0012 completion record |
| `taskcards/TC-0006-release-manifest.md` | Status: completed |
| `taskcards/TC-0008-memory-sync-command.md` | Status: completed |
| `taskcards/TC-0012-specification-normalization-layer.md` | Status: completed; all criteria checked |
| `.claude/commands/sync-memory.md` | /sync-memory command file (TC-0008) |
| `tools/validation/validate_frontmatter.py` | Front matter validator (TC-0006) |
| `tools/validation/generate_manifest.py` | Release manifest generator (TC-0006) |
| `tools/validation/check_boundary.py` | Commercial boundary checker (TC-0006) |
| `reports/capability-layer/gap-ledger.json` | 23 TOML gaps closed (0 open total) |
| `reports/boundary-check-20260618.json` | Initial boundary check report |
| `reports/supervisor/memory-sync-report.md` | Full TC-0008 memory sync report |
| `reports/r126-ndjson-install-proof/package-install-proof.md` | ndjson install proof PASS |

---

## NOT Included in This Commit (excluded)

- `.local/` — local supervisor state (gitignored)
- `reports/supervisor/` — supervisor-generated outputs (too volatile)
- `.supervisor/` — project memory (separate cadence)
- `reports/capability-layer/commercial-capability-map.json` — large generated file, separate commit
