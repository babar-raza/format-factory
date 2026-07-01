# docs/ Root Reorganization — Final Report

**Mission:** DOCS-REORG-001
**Date:** 2026-07-01
**Authority:** documentation-structure-migration capability

---

## Why the Previous Execution Was Insufficient

A prior agent expanded `docs/README.md` into a topical index but did not physically relocate any
document. The root remained at 70 files. This report covers the complete physical migration that was
actually required.

---

## Before → After

| Metric | Before | After |
|--------|--------|-------|
| Files at docs/ root | 70 | 15 (8 retained + 7 stubs) |
| Files in topical subfolders | ~195 | ~257 |
| Broken active references | 0 | 0 |

---

## What Moved Where

| Wave | Destination | Count | Notable files |
|------|-------------|-------|--------------|
| 1 | docs/ai/ | 14 | llm-endpoint-strategy.md, spec-retrieval-strategy.md, oracle-provider-strategy.md |
| 2 | docs/automation/ | 8 | assistant-supervision-methodology.md, fresh-chat-project-bootstrap.md |
| 3 | docs/governance/ | 13 | legal-and-licensing.md, release-control.md, current-state-and-evidence-authority.md |
| 4 | docs/python-foss/ | 14 | acquisition-workflow.md, specification-cache.md, format-onboarding-guide.md |
| 5 | docs/code-quality/ | 7 | architecture.md, architecture-contract.md, test-layering.md |
| 5 | docs/product-factory/ | 6 | commercial-product-capability-model.md, product-tracks.md |

**Total moved: 62 files**

---

## Pilot Methodology Results

All 5 pilots passed before bulk migration began:

1. **Pilot 1 — Low-ref move** (taskcard-layer-states.md → governance/): PASS, rollback tested
2. **Pilot 2 — Heavy-ref governance doc** (playbook-layer.md, 63 active refs, 41 files updated): PASS
3. **Pilot 3 — Historical-ref handling** (sprint-depth-policy.md): PASS, evidence bundles preserved
4. **Pilot 4 — Compatibility stub** (security.md → governance/): PASS, stub is 16 lines
5. **Pilot 5 — Generated producer repair** (3 producers updated): PASS

---

## Reference Updates

The migration engine (`tools/docs/migration_engine.py`) updated references across:
- Markdown files (`.md`)
- YAML configuration and schema files (`.yaml`)
- Python source files (`.py`)
- JSON files
- Shell scripts

Self-references in 9 moved files were fixed post-move (files referencing their own old paths).

---

## Compatibility Stubs

7 stubs created at docs/ root for HIGH-risk files with large active reference counts:

| Stub | Canonical | Reason |
|------|-----------|--------|
| docs/security.md | docs/governance/security.md | ~375 estimated refs |
| docs/legal-and-licensing.md | docs/governance/legal-and-licensing.md | HIGH ref count |
| docs/release-control.md | docs/governance/release-control.md | ~569 estimated refs |
| docs/current-state-and-evidence-authority.md | docs/governance/current-state-and-evidence-authority.md | 85 active refs |
| docs/acquisition-workflow.md | docs/python-foss/acquisition-workflow.md | ~645 estimated refs |
| docs/specification-cache.md | docs/python-foss/specification-cache.md | ~743 estimated refs |
| docs/architecture.md | docs/code-quality/architecture.md | ~591 estimated refs |

Each stub is < 50 lines and contains a deprecation notice + canonical path reference.

---

## Historical References Preserved

All references in `.local/evidence-bundles/`, `.local/evidences/`, `docs/history/`,
`docs/_audit/`, and `bundle-metadata/` were preserved as-is (not updated). Zero
historical falsification occurred.

---

## Generated Producers Repaired

| File | Old reference | New reference |
|------|--------------|--------------|
| tools/llm/run_record.py | docs/llm-endpoint-strategy.md | docs/ai/llm-endpoint-strategy.md |
| tools/llm/artifact_index.py | docs/llm-endpoint-strategy.md | docs/ai/llm-endpoint-strategy.md |
| tools/evidence/check_current_state_consistency.py | docs/current-state-and-evidence-authority.md | docs/governance/current-state-and-evidence-authority.md |

---

## Governance Healing

New capability registered:
- **Capability:** `documentation-structure-migration` (in `.governance/capabilities/registry.yaml`)
- **Skill:** `/documentation-structure-migration` (in `.supervisor/skill-registry.yaml`)
- **Command:** `.claude/commands/documentation-structure-migration.md`
- **Tool:** `tools/docs/migration_engine.py` (inventory, scan-refs, manifest, move, validate, rollback)
- **Tests:** `tests/tools/test_migration_engine.py` (23 tests, all pass)
- **Placement policy:** `docs/governance/documentation-placement-policy.yaml`
- **Placement validator:** `tools/governance/check_docs_placement.py` (PASS)

---

## Final Verification

| Check | Result |
|-------|--------|
| check_docs_placement.py | PASS |
| check_methodology_links.py | FAIL (pre-existing, unrelated to migration) |
| test_migration_engine.py (23 tests) | PASS |
| test_readme_sync.py (20 tests) | PASS |
| All 62 destinations exist | PASS |
| All sources absent (except intended stubs) | PASS |
| Historical evidence bundles unchanged | PASS |
| Idempotency (second pass, zero material changes) | PASS |

---

## Required Counters — All Zero

| Counter | Value |
|---------|-------|
| MISPLACED_MOVABLE_DOCS_REMAINING_AT_ROOT | 0 |
| BROKEN_ACTIVE_REFERENCES | 0 |
| UNEXPLAINED_OLD_PATH_REFERENCES | 0 |
| ACTIVE_INTERNAL_REFERENCES_USING_DEPRECATED_STUBS | 0 |
| DUPLICATE_AUTHORITATIVE_DOCS | 0 |
| GENERATED_PRODUCERS_EMITTING_OLD_PATHS | 0 |
| UNCLASSIFIED_DOCS_ROOT_FILES | 0 |
| ROOT_DOCS_WITHOUT_VALID_RETENTION_REASON | 0 |
| MATERIAL_SECOND_RUN_CHANGES | 0 |

---

## Final Verdict

**DOCS_ROOT_REORGANIZED_REFERENCES_PRESERVED_GOVERNANCE_HEALED_AND_IDEMPOTENT**
