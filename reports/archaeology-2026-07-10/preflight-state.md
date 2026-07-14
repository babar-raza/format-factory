# Generation Archaeology Preflight State Report
# TC-ARCH-001 (fuzzy-conjuring-lobster — MCP-W3-001)
# Generated: 2026-07-12

## Repository State

- **Branch:** main
- **HEAD:** `3fdaf841ed8941616dbe5e19d43af618c317d57b`
- **HEAD message:** `feat(portfolio): complete MCP-W1-007 and MCP-W2-002 portfolio execution`
- **Recent commits (3):**
  - `3fdaf841` feat(portfolio): complete MCP-W1-007 and MCP-W2-002 portfolio execution
  - `bc2b3c1c` feat(governance): FIOP-FULL-001 found-issue ownership protocol complete
  - `8192b723` feat(fods): add 6 analytics functions to fods_file_analytics (ext2)

## Dirty File Summary

| Classification | Count |
|---|---|
| M (modified tracked) | 148 |
| ?? (untracked) | 137 |
| **Total dirty** | **285** |

### Dirty File Categories

**Modified (148):** Includes supervisor reports, governance config, capability layer files,
.supervisor/prompts/ (provenance map, registry, index from MCP-W2-005), tools/supervisor/
(sprint_executor_validate.py Phase 17, validate_prompt_registry.py, espanso_staleness_checker.py),
CLAUDE.md (EP-1 through EP-5 rules), .governance/capabilities/registry.yaml,
plans/.claude/production-portfolio-master-plan.md, tests/supervisor/ (new test files),
oracle/ reports, reports/capability-layer/.

**Untracked (137):** Includes .governance/backfill/, .governance/lanes/, .portfolio/,
.runner_system_id, .supervisor/schemas/ (new schema files), goofy-orbiting-scroll-portfolio.zip,
plans/.claude/goofy-orbiting-scroll.md, registry/gate-states.yaml, registry/governance-binding.yaml,
reports/canary/, reports/product-quality/fods-govheal/, reports/skills-r90/, tests/machinery/,
tools/backfill/, tools/canary/, tools/supervisor/ (new tools: dom_maturity_gap_generator.py,
plan_importer.py, skill_receipt_writer.py, validate_governance_binding.py,
validate_governance_schemas.py, governance_validators_sgov.py).

## Plan Directory Structure

- `plans/.claude/`: **77 files** (in-repo plan files, authoritative execution copies)
- `plans/source-portfolios/ff-portfolio-41-prod-001/`: 41 source plans (read-only)
- `plans/strategic/`: Multi-lane correction plans
- `plans/master-plan.md`: Project master plan
- `plans/layers/`: Layer governance plans

## Source Tree Inventory

### Python FOSS Formats (20 product directories)

| Format | Directory | Status |
|---|---|---|
| ABW | src/python/abw/ | Installed (non-editable) |
| CSV | src/python/csv/ | Product source |
| DIF | src/python/dif/ | Installed (non-editable) |
| FODG | src/python/fodg/ | Product source |
| FODP | src/python/fodp/ | Product source |
| FODS | src/python/fods/ | Product source |
| FODT | src/python/fodt/ | Product source |
| GNUMERIC | src/python/gnumeric/ | Product source |
| NDJSON | src/python/ndjson/ | Product source |
| ODS | src/python/ods/ | Product source |
| ODT | src/python/odt/ | Product source |
| PBM | src/python/pbm/ | Product source |
| PGM | src/python/pgm/ | Product source |
| PPM | src/python/ppm/ | Product source |
| QOI | src/python/qoi/ | Product source |
| SYLK | src/python/sylk/ | Installed (non-editable) |
| TOML | src/python/toml/ | Product source |
| TSV | src/python/tsv/ | Product source |
| XCF | src/python/xcf/ | Product source |
| ZST | src/python/zst/ | Product source |

**Build artifacts in Python src:** `format_factory_abw.egg-info/` (tracked in known_violations)

### .NET Commercial Formats (10 directories)

| Format | Directory |
|---|---|
| CSV | src/net/csv/ |
| FODS | src/net/fods/ |
| FODT | src/net/fodt/ |
| HTML | src/net/html/ |
| MARKDOWN | src/net/markdown/ |
| NDJSON | src/net/ndjson/ |
| NETPBM | src/net/netpbm/ |
| TSV | src/net/tsv/ |
| TXT | src/net/txt/ |
| ZST | src/net/zst/ |

## State Files (`.local/supervisor/`)

Key state files present:
- `active-plan-lock.json` — plan lock state
- `active-continuation.json` — continuation signal
- `action-queue.jsonl` — pending actions
- `assigned-gaps.json` — gap assignments
- Plan locks in `plan-locks/` (session-keyed)

## Last Sprint Evidence

**Last closed plan:** `glimmering-hopping-kazoo.md` (FF-AGENTS-PARITY-001, TERMINAL_CLOSED)
**Portfolio authority:** `production-portfolio-master-plan.md`
**Current wave:** W3 (generation archaeology + audits)
**Wave 2 completion:** All 5 W2 taskcards closed (2 ALREADY_SATISFIED, 3 CLOSED)

## Governance Baseline

- Governance validators: **170 total**, exit 0 confirmed (post-MCP-W2-005)
- Pytest: **29/29 pass** for supervisor tests (post-MCP-W2-005)
- CLAUDE.md: **678 lines** (EP-1 through EP-5 added in MCP-W2-005)
- Prompt registry: **11 ESP prompts** (ESP-PROMPT-1 through ESP-PROMPT-11)
- Capability parity: **123:123:123** (capability:skill:command)

## Acceptance Criteria Verification

- [x] preflight-state.md exists and is non-empty
- [x] Every dirty file category classified (M=148 modified, ??=137 untracked)
- [x] Branch, HEAD, and last sprint recorded
- [x] All plan directories listed
