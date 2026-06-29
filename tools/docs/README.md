# Documentation Generators — tools/docs/

Auto-generate project status documents from repository evidence. Every number in the output is traced to a canonical registry, oracle result, or test artifact.

## Quick Start

```bash
# Generate the full PROJECT_STATUS.md (single source of truth)
python tools/docs/generate_project_status.py

# Also inject a summary into README.md
python tools/docs/generate_project_status.py --update-readme

# Preview without writing files
python tools/docs/generate_project_status.py --dry-run

# Export raw collected data as JSON
python tools/docs/generate_project_status.py --json
```

## Scripts

| Script | Purpose | Standalone |
|---|---|---|
| `generate_project_status.py` | Master orchestrator — assembles all sections into `PROJECT_STATUS.md` | `python tools/docs/generate_project_status.py` |
| `generate_statistics.py` | Counts formats, tests, validators, skills, sprints, etc. | `python tools/docs/generate_statistics.py [--json]` |
| `generate_product_inventory.py` | Per-format table: family, Python/.NET, oracle, certification, gates | `python tools/docs/generate_product_inventory.py [--json]` |
| `generate_architecture_inventory.py` | 11-layer architecture, validators, capabilities, skills, gate pipeline | `python tools/docs/generate_architecture_inventory.py [--json]` |
| `generate_agent_inventory.py` | Agent ecosystem: Claude/Codex/Kilo, decision boundaries, policies | `python tools/docs/generate_agent_inventory.py [--json]` |

## Evidence Sources

Each script reads from canonical registries — never from hardcoded values:

| Source | Path | What it provides |
|---|---|---|
| Format registry | `registry/format-registry.yaml` | Format metadata, families, gates |
| Capability registry | `.governance/capabilities/registry.yaml` | Capability count and parity |
| Skill registry | `.supervisor/skill-registry.yaml` | Registered skills |
| Oracle results | `oracle/formats/*/reports/oracle-run-summary.json` | Per-format pass/fail |
| Certification matrix | `reports/certification/portfolio-certification-matrix.json` | Per-format certification |
| Maturity trend | `reports/supervisor/maturity-trend.json` | Sprint count and quality |
| Governance validators | `tools/supervisor/governance_validators*.py` | Validator definitions |
| Policies | `.supervisor/policies.yaml` | Autonomous execution constraints |
| AGENTS.md | `AGENTS.md` | Agent governance sections |
| Source tree | `src/python/`, `src/net/` | File counts per format |
| Test tree | `tests/python/`, `tests/net/` | Test counts per format |
| Commands | `.claude/commands/*.md` | Command file count |

## Output

- **`PROJECT_STATUS.md`** (repo root) — the canonical status document. Any blog post, README section, or presentation should reference this file.
- **README.md injection** — when run with `--update-readme`, injects a summary block between `<!-- BEGIN:PROJECT-STATUS-REF -->` and `<!-- END:PROJECT-STATUS-REF -->` markers.

## Design Principles

- **Idempotent**: Re-running on an unchanged repo produces identical output (except timestamps).
- **No hardcoded counts**: Every number is computed from evidence at generation time.
- **Graceful degradation**: Missing files are skipped, not errors.
- **Composable**: Each sub-generator has `collect_*()` (returns dict) and `render_*()` (returns markdown) functions that can be imported independently.

## Dependencies

- Python 3.10+
- PyYAML (already in project venv)
- No other external dependencies
