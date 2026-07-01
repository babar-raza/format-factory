# /documentation-structure-migration

**Capability:** documentation-structure-migration
**Mission ID:** DOCS-REORG-001
**Status:** active
**Owner Layer:** layer_governance

## Purpose

Safely relocate docs/ root files into topical subfolders with:
- Complete reference graph scan (all file types: .md, .yaml, .json, .py, .sh, etc.)
- Active-reference rewriting (YAML, Python, Markdown, JSON, registries, plans, tests)
- Compatibility stubs where external consumers may depend on old paths
- Historical reference preservation (no evidence falsification)
- Migration manifest (frozen before any file moves)
- Post-move validation and idempotency proof

## CLI Entry Point

```bash
python tools/docs/migration_engine.py <subcommand> [options]
```

## Subcommands

| Subcommand | Purpose |
|---|---|
| `inventory` | List all docs/ root files with classification metadata |
| `scan-refs` | Scan entire repository for references to docs/ root files |
| `manifest` | Generate or validate the migration manifest YAML |
| `move` | Execute a single manifest item (git mv + reference updates) |
| `validate` | Post-move validation (destination exists, old active refs gone) |
| `rollback` | Restore a moved file from backup |

## Required Handoff Fields

- `source_path` — current docs/ root file path (e.g., `docs/governance/security.md`)
- `destination_path` — canonical destination (e.g., `docs/governance/security.md`)

## Mandatory Validations

1. `migration_manifest_frozen_before_moves` — manifest written + reviewed before any git mv
2. `all_active_references_updated` — scan-refs shows 0 ACTIVE_* refs to old path after move
3. `no_duplicate_authoritative_content` — stub is thin (notice only, no content duplication)
4. `idempotency_second_pass_clean` — second run produces zero material changes

## Evidence Contract

Evidence directory: `.local/evidences/docs-root-reorganization-001/`

Required artifacts:
- `baseline.yaml` — captured before any changes
- `pilot-results.yaml` — 5 pilot classes proven before bulk moves
- `idempotency-proof.yaml` — second-pass results
- `terminal-closeout.yaml` — final evidence record

Reports:
- `reports/documentation/docs-root-inventory.yaml`
- `reports/documentation/docs-root-retention-policy.yaml`
- `reports/documentation/docs-root-destination-map.yaml`
- `reports/documentation/docs-reference-graph.yaml`
- `reports/documentation/docs-root-migration-manifest.yaml`
- `reports/documentation/docs-root-post-migration-audit.yaml`
- `reports/documentation/docs-root-reorganization-report.md`

## Root Retention Policy

Only these documents may remain at docs/ root:
1. `README.md` — canonical entry point
2. `agent-methodology-index.md` — validator-enforced + cross-cutting
3. `planning-methodology.md` — enforced by check_methodology_links.py
4. `agent-execution-handoff-standard.md` — enforced by check_methodology_links.py
5. `plan-hardening-checklist.md` — enforced by check_methodology_links.py
6. `fresh-chat-continuity-brief.md` — enforced by check_methodology_links.py
7. `gates.md` — repository-wide cross-cutting gate authority
8. `spec-to-feature-correction-plan-summary.md` — CLAUDE.md mandatory pre-read

All other files must have a canonical destination in a topical subfolder.
