# RECON-MANIFEST.md

## Run Identification

| Field | Value |
|---|---|
| Run ID | `FF-DEEP-RECON-20260705-052931` |
| Start Time | 2026-07-05 10:22:56 +0500 (05:22 UTC) |
| Branch | `main` |
| Commit | `94dd5308120693702e77191b409ce11aaf660e11` |
| Platform | Windows 11 Pro 10.0.26200 |
| Shell | bash (Git Bash on Windows) |
| Python | 3.13 (system), 3.13 (.venv) |
| .NET SDK | 10.0.204 (net10.0 target) |
| Investigator | Claude Opus 4.6 (autonomous deep recon) |

## Repository Identity

| Field | Value |
|---|---|
| Root | `format-factory` |
| Remotes | GitHub (`github.com/babar-raza/format-factory.git`), GitLab (`gitlab.recruitize.ai/sialkot/cantt-smallize/format-factory.git`) |
| Total commits | 1,810 |
| First commit | 2026-05-02 |
| Latest commit | 2026-07-05 |
| Commits: May 2026 | 547 |
| Commits: June 2026 | 945 |
| Commits: July 2026 | 318 |

## Working-Tree State at Scan Start

| Category | Files |
|---|---|
| Modified (staged) | `plans/.claude/streamed-jumping-oasis.md` |
| Modified (unstaged) | `plans/master-plan.md` |
| Untracked | `.runner_system_id` |

Pre-existing changes were preserved; no files were modified, stashed, or reset during this reconnaissance.

## Repository Scale

| Metric | Count | Method |
|---|---|---|
| Tracked files | 15,728 | `git ls-files \| wc -l` |
| `.py` files | 4,164 | Extension count from `git ls-files` |
| `.cs` files | 2,676 | Extension count from `git ls-files` |
| `.md` files | 4,797 | Extension count from `git ls-files` |
| `.json` files | 1,982 | Extension count from `git ls-files` |
| `.yaml` files | 1,250 | Extension count from `git ls-files` |
| Python source LOC (src/) | ~49,375 | Sum of per-format LOC counts |
| .NET source LOC (src/) | ~22,557 | Sum of per-format LOC counts |
| Python test files | ~2,300+ | `find tests/ -name "test_*.py"` |
| Tests collected (pytest) | 39,863 | `pytest --collect-only` |
| Supervisor .py files | 262 | `find tools/supervisor -name "*.py"` |
| Supervisor LOC | ~81,241 | `wc -l tools/supervisor/*.py` |
| Governance validators | 153 | `grep -c "def validate_"` across 18 modules |
| Registered skills | 123 | `grep -c "skill_id:"` in skill-registry.yaml |
| Claude commands | 124 | `.claude/commands/*.md` count |

## Top-Level Directory Classification

| Directory | Purpose | Primary Language |
|---|---|---|
| `src/python/` | Python product libraries (20 formats) | Python |
| `src/net/` | .NET product libraries (10 formats) | C# |
| `tools/` | Development machinery, supervisor, governance, AI, oracle | Python |
| `tests/` | Test suite (unit, integration, oracle, governance) | Python, C# |
| `docs/` | Documentation, guides, plans summaries | Markdown |
| `plans/` | Master plan, strategic plans, per-chat plan files | Markdown |
| `reports/` | Sprint reports, audits, evidence reviews (402 MB) | Markdown, JSON |
| `registry/` | Format registry, QName registry refs, baselines | YAML, JSON |
| `schemas/` | JSON/YAML schemas for evidence, capabilities, requirements | JSON, YAML |
| `samples/` | Sample files per format for testing | Various |
| `oracle/` | Oracle test cases per format | YAML |
| `shared/` | QName registry (cross-language) | YAML |
| `acquisition-packs/` | Gate evidence per format (legal, scoring, prototypes) | Markdown, YAML |
| `examples/` | Usage examples per format/language | Python, C# |
| `packaging/` | Package build scripts and templates | Python |
| `templates/` | Code generation templates | Various |
| `scripts/` | Utility scripts | Shell, Python |
| `drivers/` | Format conversion drivers | Python |
| `prototypes/` | Prototype implementations | Various |
| `evidence-bundles/` | Compiled evidence bundles | Various |
| `gate-readiness/` | Gate readiness matrices | YAML |
| `reviews/` | Code review artifacts | Various |
| `playbooks/` | Acquisition and process playbooks | Markdown |
| `.supervisor/` | Skill registry, policies, state config | YAML |
| `.governance/` | Capability registry, governance config | YAML |
| `.claude/` | Claude Code commands and plan files | Markdown |
| `.kilo/` | Kilo AI agent configuration | JSON |
| `.github/` | CI workflows | YAML |

## Package Manifests Found

| File | Type |
|---|---|
| `pyproject.toml` | Python dev umbrella package |
| `src/net/fods/FormatFactory.Fods.csproj` | .NET FODS library |
| `src/net/fodt/FormatFactory.Fodt.csproj` | .NET FODT library |
| `src/net/csv/FormatFactory.Csv.csproj` | .NET CSV library |
| (+ 8 more .csproj files) | .NET format libraries |
| `packaging/python/pyproject.template.toml` | Python package template |
| `.kilo/package.json` | Kilo agent config |

## CI Workflows

| File | Purpose |
|---|---|
| `.github/workflows/ci.yml` | Lint (ruff), security (bandit), fast tests (L0-L3), skill attribution |
| `.github/workflows/release.yml` | Release workflow |

## Directories Excluded from Exhaustive Inspection

| Directory | Reason | Sampling Strategy |
|---|---|---|
| `reports/` (402 MB) | Historical sprint reports; too large for file-by-file | Sampled `supervisor/`, structure-only scan |
| `.local/` | Gitignored local state; ephemeral | Sampled evidence declarations |
| `build/` | Build artifacts | Structure only |
| `__pycache__/` | Bytecode cache | Excluded |
| `.venv/` | Virtual environment | Excluded |

## Tests and Validators Run

| Command | Result | Duration |
|---|---|---|
| `pytest tests/python/fods/ -x -q` | 1,571 passed, 8 skipped | 10.35s |
| `pytest tests/python/zst/ -x -q` | 1,316 passed | 8.84s |
| FODS parse runtime | `parse_fods()` returned 1 sheet | <1s |
| FODS roundtrip runtime | `parse_fods → write_fods → parse_fods` | <1s |
| ZST compress/decompress | 2300→41 bytes, roundtrip match | <1s |
| FODT parse runtime | `parse_fodt()` returned `format_id: fodt` | <1s |
| TOML load runtime | `load_toml()` returned dict | <1s |
| `pytest --collect-only` (full) | 39,863 tests collected | 100s |

## Generated Files

| File | Description |
|---|---|
| `RECON-MANIFEST.md` | This file |
| `01-SYSTEM-OVERVIEW.md` | Comprehensive technical overview |
| `02-SYSTEM-ARCHITECTURE-AND-DIAGRAMS.md` | Architecture diagrams (Mermaid) |
| `03-BLOG-ANNOUNCEMENT.md` | Publication-ready blog announcement |
| `04-CLAIM-EVIDENCE-LEDGER.md` | Structured claim-evidence ledger |
| `05-GAPS-CONTRADICTIONS-AND-OPEN-QUESTIONS.md` | Gaps and open questions |
| `RECON-COMPLETION-REPORT.md` | Acceptance checklist and verdict |
