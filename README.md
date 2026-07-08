# format-factory

A File Format Acquisition System that produces legal parsers, converters, importers, exporters, validators, and compatibility tools for structured file formats.

**Target users:** Developers building file-format support, document processing tool builders, and teams evaluating format libraries for their products.

**Current state (as of July 2026):** 20 formats supported across Python FOSS and .NET commercial tracks. 20 installable Python packages. 162 governance validators across 20 modules. 840+ autonomous sprint cycles completed through the formal pipeline. Gate 11 G11-G sub-gate approved by Babar Raza 2026-06-05 (FODS, FODT, Netpbm). All 20 Python FOSS formats oracle-verified (73/73 PASS). PYREL release gates G1+G2 operational. See [PROJECT_STATUS.md](PROJECT_STATUS.md) for the full auto-generated status.

---

## What This Project Does

format-factory builds production-quality, legally vetted format support libraries for common file formats. Every format supported by this project passes a formal acquisition pipeline: legal review, evidence gathering, sample validation, prototype development, security testing, product mapping, and human approval.

The project never engages in unauthorized binary reverse engineering, bypasses access controls, or violates intellectual property rights.

---

## Machinery vs. Products

format-factory has two distinct halves:

- **Products** (`src/python/`, `src/net/`) — the shipped libraries that parse, write, validate, and convert file formats. These are deterministic, spec-aligned code with no LLM calls at runtime. Products are what users install and consume.
- **Machinery** (`tools/`, `.supervisor/`, `plans/`, `reports/`, `oracle/`) — the autonomous supervision system that plans work, executes sprints, validates evidence, grades outcomes, and generates next actions. Machinery governs the development process but is never shipped to end users. See [`tools/docs/`](tools/docs/) for auto-generated project status and inventory tools.

Products are the deliverables. Machinery is the factory that builds, tests, and certifies them.

---

## Layer Architecture

The system is organized into 11 independent layers, each with defined boundaries and contracts:

| Layer | Name | Primary Paths | Purpose |
|---|---|---|---|
| L01 | SAL | `tools/spec/`, `shared/qname-registry/` | Specification fact extraction and QName registry |
| L02 | QName | `shared/qname-registry/*.yaml` | Canonical spec-element-to-class mapping |
| L03 | Capability | `reports/capability-layer/` | Feature and gap tracking |
| L05 | Oracle | `oracle/` | Deterministic spec-grounded test cases |
| L06 | Product Source | `src/python/`, `src/net/` | Parser, writer, and model implementations |
| L07 | Tests | `tests/` | Unit, integration, roundtrip, and oracle tests |
| L08 | Evidence | `.local/evidences/` | Sprint evidence declarations and proof bundles |
| L09 | State | `.local/supervisor/`, `reports/supervisor/` | Continuation signals, plan locks, session state |
| L11 | Supervisor | `tools/supervisor/` | Sprint orchestration, grading, next-work generation |
| L12 | Governance | `tools/supervisor/governance_validators*.py` | 162 programmatic validators |
| L13 | Skills | `.supervisor/skill-registry.yaml`, `.claude/commands/` | 123 registered skill definitions and routing |

Layer contracts and audit results: `reports/layer-audit-2026-06-26/`.

---

## Project Goals

format-factory aims to build a repeatable system for studying file formats and turning that knowledge into safe, legal, tested software tools.

The project goals are:

1. Understand file formats using official specifications and approved evidence.
2. Create verified format knowledge that can be reused across products.
3. Build open-source Python libraries for selected formats.
4. Prepare future .NET and commercial products under stricter approval rules.
5. Use gates, tests, security review, and evidence bundles to control quality.
6. Make the process repeatable so more formats can be added later.

---

## Quick Start

**Prerequisites:** Python 3.10+ and Git. Create a virtual environment before running commands:

```bash
git clone <repository-url>
cd format-factory
python -m venv .venv
.venv/Scripts/activate        # Windows
# source .venv/bin/activate   # Linux/macOS
pip install pytest pyyaml
```

```bash
# Check autonomous sprint loop status
python tools/supervisor/check_continuation.py

# Run all Python FOSS tests
.venv/Scripts/pytest tests/python/ -x

# Build a local installable package (e.g. fods)
python packaging/python/build-local-packages.py --format fods

# Run governance validators against the latest evidence declaration
python tools/supervisor/governance_validators.py --check
```

---

## Usage Example

After building a local package (e.g., `python packaging/python/build-local-packages.py --format toml`):

```python
from toml import load_toml, write_toml

# Parse a TOML file into a dict
result = load_toml("config.toml")
print(result["top_level_keys"])          # ['server', 'database', ...]
print(result["data"]["server"]["port"])  # 8080

# Mutate and write back
result["data"]["server"]["port"] = 9999
write_toml(result["data"], "config-updated.toml")
```

Each format follows a similar pattern. See `examples/python/` for consumer roundtrip scripts covering all 20 formats.

---

## Products

### Python FOSS Track (20 installable packages, local only)

| Format | Type | Package | Consumer Proof |
|--------|------|---------|----------------|
| FODS | Flat ODF Spreadsheet | `aspose-format-factory-fods` | PASS |
| FODT | Flat ODF Text | `aspose-format-factory-fodt` | PASS |
| ODS | ODF Spreadsheet | `aspose-format-factory-ods` | PASS |
| ODT | ODF Text | `aspose-format-factory-odt` | PASS |
| FODG | Flat ODF Drawing | `aspose-format-factory-fodg` | PASS |
| FODP | Flat ODF Presentation | `aspose-format-factory-fodp` | PASS |
| GNUMERIC | Gnumeric spreadsheet | `aspose-format-factory-gnumeric` | PASS |
| ABW | AbiWord | `aspose-format-factory-abw` | PASS |
| DIF | Data Interchange Format | `aspose-format-factory-dif` | PASS |
| SYLK | Symbolic Link | `aspose-format-factory-sylk` | PASS |
| TOML | Config/data format | `aspose-format-factory-toml` | PASS |
| NDJSON | Newline-delimited JSON | `aspose-format-factory-ndjson` | PASS |
| TSV | Tab-separated values | `aspose-format-factory-tsv` | PASS |
| CSV | Comma-separated values | `aspose-format-factory-csv` | PASS ⚠️ |
| ZST | Zstandard compression | `aspose-format-factory-zst` | PASS |
| QOI | Quite OK Image format | `aspose-format-factory-qoi` | PASS |
| XCF | GIMP native image | `aspose-format-factory-xcf` | PASS |
| PBM | Netpbm bitmap | `aspose-format-factory-pbm` | PASS |
| PGM | Netpbm graymap | `aspose-format-factory-pgm` | PASS |
| PPM | Netpbm pixmap | `aspose-format-factory-ppm` | PASS |

**Consumer Proof** means a runnable script that loads, inspects, mutates, writes, and reloads the format using only the installed package API — verifying the full workflow end-to-end. See `examples/python/` for all 20 scripts.

**⚠️ CSV namespace note:** The `csv` package name collides with Python's stdlib `csv` module. Plain `import csv` resolves to stdlib in all standard Python environments. Use submodule imports instead: `from csv.csv_parser import parse_csv`. The consumer proof script handles this with an explicit sys.path workaround. All other 19 packages import without collision.

All packages: `publish_status: local_only_not_published`, `publication_authorized: false`. See `packaging/python/package-matrix.yaml`.

### .NET Commercial Track (3 products)

| Format | .NET Project | Gate 11 G11-G | Status |
|--------|-------------|---------------|--------|
| FODS | `src/net/fods/` | APPROVED 2026-06-05 (Babar Raza) | Extensive test coverage, not commercially released |
| FODT | `src/net/fodt/` | APPROVED 2026-06-05 (Babar Raza) | Extensive test coverage, not commercially released |
| Netpbm | `src/net/netpbm/` | APPROVED 2026-06-05 (Babar Raza) | Extensive test coverage, not commercially released |

`commercial_product_ready: false` for all entries — requires Gate 11 G11-G EXECUTION approval (Babar Raza only) and full spec-parity verification.

> **Note:** 7 additional .NET source projects (CSV, HTML, Markdown, NDJSON, TSV, TXT, ZST) exist in `src/net/` at various implementation stages but are not on the commercial release track. See `registry/parity-matrix.yaml` for per-format parity status.

Source layout: `src/python/{format}/` for Python FOSS; `src/net/{format}/` for .NET product.

---

## Supported Format Families

The project is organized around six format families:

| Family | Description | Formats |
|---|---|---|
| Cells | Spreadsheets and tabular data | FODS, ODS, DIF, SYLK, GNUMERIC, CSV, TSV |
| Words | Word processing documents | FODT, ODT, ABW |
| Slides | Presentations | FODP |
| Drawing | Vector drawing | FODG |
| Imaging | Raster images | PBM, PGM, PPM, QOI, XCF |
| Data/Archive | Config, data, compression | TOML, NDJSON, ZST |

---

## Acquisition Pipeline

Every format passes through 11 mandatory gates:

1. **Gate 1**: Candidate Accepted, scoring and legal classification
2. **Gate 2**: Evidence Complete, spec analysis and legal notes
3. **Gate 3**: Sample Corpus Ready, licensed samples with confirmed provenance
4. **Gate 4**: Prototype Complete, working parser and security baseline
5. **Gate 5**: Neutral Model Defined, format-family data schema
6. **Gate 6**: Oracle Comparison Complete, discrepancy analysis
7. **Gate 7**: Fuzz Testing Complete
8. **Gate 8**: Security Review Complete
9. **Gate 9**: Product Mapping Complete, tier assignment and delivery plan
10. **Gate 10**: OSS Readiness Complete, production source and release manifest
11. **Gate 11**: Commercial Readiness Complete, commercial tier and proprietary manifest

Gates 1-10 are agent-owned policy gates with evidence, validators, and acceptance criteria. Gate 11 G11-G (commercial release EXECUTION) requires Babar Raza's business authority — the only TRUE_EXTERNAL_GATE.

---

## Engineering Practices

- **Test Suite:** 1,609+ tests passing (0 failures) across Python and .NET tracks as of last sprint 2026-06-25. Tests span unit, integration, roundtrip, analytics, spec-fact traceability, and installed-package workflow proofs. See `reports/supervisor/session-resume.md` for current counts.
- **Test Framework:** pytest with `--import-mode=importlib` and 120-second per-test timeout. Dual conftest pattern handles stdlib module shadowing (`csv`, `html`).
- **Quality Gates:** 162 programmatic governance validators across 20 modules (`tools/supervisor/governance_validators*.py`) block sprints on policy violations. Validators enforce: declaration schema compliance, evidence artifact existence, anti-skip checks, skill-first execution, spec-fact references, QName compliance, architecture stub detection, analytics separation, lane enforcement, package manifest completeness, oracle obligations, and README freshness.
- **Source Size Policy:** Maximum 800 LOC and 60 functions per production file, tracked in `registry/source-structure-baseline.json`. Violations are frozen at `baseline_loc_cap` (write-once).
- **Security:** Gate 8 requires security review before any format reaches product. Parser threat model covers XXE, billion laughs, zip bombs, path traversal, malformed input handling, memory limits, recursion limits, and binary parser safety (`docs/governance/security.md`).
- **QName Compliance:** Every exported Python class carries a `spec_qname` class attribute mapping to its canonical ODF/format specification element (enforced by V51-V53). Spec authority classes live in `{format}/spec/`; Compat/ facades expose simplified names.

---

## Oracle Layer

The oracle layer (`oracle/`) provides deterministic, specification-grounded test cases for all 20 Python FOSS formats. Each format directory contains YAML case definitions that verify parser behavior against expected outcomes derived from format specifications.

- **Coverage:** All 20 active Python FOSS formats have oracle cases at VERIFIED status (73/73 PASS as of 2026-06-26).
- **Execution:** `tools/oracle/execute_oracle.py` runs all cases deterministically — no LLM involvement.
- **Policy:** `oracle/oracle-authority-policy.md` defines case creation rules and expected-value provenance requirements.

---

## Specification Authority Layer (SAL)

The SAL (`tools/spec/`) extracts and indexes machine-readable facts from official format specifications. These facts serve as the ground truth for QName registries, oracle expected values, and spec-parity verification.

- **Scope:** 14,635+ indexed spec facts across all supported formats (see `shared/qname-registry/` for per-format registries).
- **Tools:** `tools/spec/merge_sal_facts.py` merges per-format SAL caches; `tools/spec/validate_spec_registry.py` validates registry consistency.
- **Integration:** Governance validators V51-V53 enforce that exported classes reference valid SAL-indexed spec QNames.

---

## Deterministic vs. Agent-Assisted Workflows

format-factory distinguishes between deterministic code and agent-assisted orchestration:

| Layer | Nature | Examples |
|---|---|---|
| **Production source** (`src/`) | Deterministic | Parsers, codecs, exporters, model classes — no LLM calls at runtime |
| **Test suites** (`tests/`) | Deterministic | All tests are repeatable with fixed inputs and expected outputs |
| **Oracle layer** (`oracle/`) | Deterministic | Spec-grounded expected values, deterministic execution |
| **SAL tools** (`tools/spec/`) | Deterministic | Fact extraction from specification documents |
| **Governance validators** | Deterministic | Policy checks run as pure functions on declaration data |
| **Sprint orchestration** (`tools/supervisor/`) | Agent-assisted | Sprint planning, evidence grading, next-work-item selection use LLM judgment |
| **Code generation** | Agent-assisted | Initial source file creation uses Claude Code; output is reviewed and tested |
| **Plan hardening** | Agent-assisted | Audit classification and taskcard creation involve LLM reasoning |

All shipped product code is deterministic with no LLM calls or AI runtime dependencies. The development pipeline itself is agent-orchestrated — AI agents perform sprint planning, code generation, test writing, and governance validation. Human oversight applies at defined gates, primarily commercial release authorization.

---

## Governance System

format-factory enforces quality through layered governance:

- **162 programmatic validators** across 20 modules (`tools/supervisor/governance_validators*.py`) — deterministic checks on every sprint declaration. They enforce declaration schema, evidence existence, spec-fact references, QName compliance, architecture rules, analytics separation, lane ownership, package manifests, oracle obligations, and README freshness.
- **Gate contracts** (`registry/gate-contract-registry.yaml`) — each of the 11 gates has formal acceptance criteria. Gates 1-10 are policy-based (agent can satisfy with evidence). Gate 11 G11-G requires human business authority (Babar Raza).
- **Source size policy** — maximum 800 LOC / 60 functions per production file, tracked in `registry/source-structure-baseline.json` with write-once `baseline_loc_cap` ceilings.
- **Skill-first execution** — all agent work must route through registered skills (`.supervisor/skill-registry.yaml`, 123 skills). Ad-hoc execution is detected and flagged.
- **Contradiction detection** — the supervisor pipeline detects contradictions between declared state and repository truth (`reports/supervisor/contradictions.json`). Critical contradictions block autonomous continuation.

See [GOVERNANCE.md](GOVERNANCE.md) for human contributor rules and [AGENTS.md](AGENTS.md) for agent operating contracts.

---

## Autonomous Supervision Architecture

format-factory uses an autonomous supervisor pipeline that manages multi-sprint execution with bounded repair and evidence materialization. 840 autonomous sprint cycles have been completed through the formal evidence pipeline (53% ACCEPTED first pass, 47% ACCEPTED_WITH_REWORK, average quality score 0.756).

- **State Management:** Session state persisted in `reports/supervisor/session-resume.md` and `.local/supervisor/continuation-signal.json`. Cross-window recovery restores full operational context without requiring prior conversation history.
- **Flow Orchestration:** 4-stream architecture (Mainstream Product, Acceleration, Skills/Governed Execution, Supervisor/Autonomous Continuation) with a 15-state taskcard machine governing work item lifecycle. Pipeline: sprint start → execute work items → write evidence declaration → validate with 162 governance validators → grade work items → generate next sprint → check continuation signal.
- **Boundary Enforcement:** `AGENTS.md` (~60KB operating contract) defines non-negotiable rules for all automated executors. 162 governance validators across 20 modules programmatically block sprints on policy violations. Gate 11 G11-G approval requires explicit human business authority.
- **Adaptive Repair:** `tools/supervisor/bounded_repair_engine.py` classifies test and build failures into 6 categories (IMPORT, SYNTAX, ATTRIBUTE, NAME, ASSERTION, TIMEOUT) and applies targeted repairs with automatic rollback on failure.
- **CCI (Cross-Chat Continuation Isolation):** `session_id` field in continuation signals prevents cross-chat state contamination. SESSION_MISMATCH is a non-overridable hard stop.

Key implementation files:

- `tools/supervisor/autonomous_cycle.py` — Sprint execution and evidence pipeline
- `tools/supervisor/governance_validators*.py` — 162 programmatic quality gates across 20 modules
- `tools/supervisor/lane_enforcement_validator.py` — Cross-lane file ownership enforcement
- `tools/supervisor/bounded_repair_engine.py` — Error classification and bounded repair
- `tools/supervisor/check_continuation.py` — Autonomous loop continuation gate
- `packaging/python/build-local-packages.py` — Local Python wheel builder for all 20 formats

---

## Project Status

| Item | Status |
|------|--------|
| Python FOSS formats | 20 formats in source; 20 installable packages; all local only |
| .NET commercial formats | FODS, FODT, Netpbm; G11-G sub-gate approved; not commercially released |
| Gate 11 G11-G | APPROVED by Babar Raza 2026-06-05 (sub-gate); G11-G EXECUTION pending |
| commercial_product_ready | false (all entries) |
| Tests | 1,609+ passing (0 failures) as of last sprint 2026-06-25. See `reports/supervisor/session-resume.md` |
| Governance validators | 162 across 20 modules |
| Oracle verification | All 20 Python FOSS formats VERIFIED (73/73 cases PASS) |
| Spec parity (FODS) | PARTIAL — 12/12 QName facades complete (TC-SP-002, 2026-06-25); behavioral parity partial (Python read-only; .NET has 23 mutation methods) |
| Spec parity (FODT) | VERIFIED — SAL cache repaired (4,936 facts), 8/8 behavioral QNames have Compat/ facades (TC-SP-004/005, 2026-06-25) |
| Autonomous loop | ACTIVE — fully autonomous sprint execution with tool integration |

For canonical per-format status, see:
- `product-capability-matrix/poc-targets.yaml` — product targets and gate status
- `registry/parity-matrix.yaml` — Python/.NET parity tracking
- `reports/supervisor/session-resume.md` — last sprint outcome and next action
- `reports/supervisor/approval-gates.md` — current continuation authorization

---

## Repository Structure

<!-- BEGIN:REPOSITORY-NAVIGATION generated=2026-06-29T00:00:00+00:00 source=registry/repository-root-folders.yaml -->

### Core Product

| Folder | Purpose | README |
|---|---|---|
| `src/` | Python and .NET product source code | [README.md](src/README.md) |
| `tests/` | All test suites (format, governance, supervisor) | [_readme.md](tests/_readme.md) |
| `samples/` | Test and reference sample files per format | [README.md](samples/README.md) |
| `oracle/` | Oracle test cases and spec-grounded verification | [README.md](oracle/README.md) |
| `examples/` | Code examples demonstrating library usage | [README.md](examples/README.md) |

### Governance Infrastructure

| Folder | Purpose | README |
|---|---|---|
| `.claude/` | Claude Code agent configuration and commands | [README.md](.claude/README.md) |
| `.github/` | CI/CD workflows and issue templates | [README.md](.github/README.md) |
| `.governance/` | Capability registry and parity reports | [README.md](.governance/README.md) |
| `.hooks/` | Pre-commit hooks (skill guard) | [README.md](.hooks/README.md) |
| `.supervisor/` | Supervisor config, policies, schemas, prompts | [README.md](.supervisor/README.md) |
| `plans/` | Master plan, layer plans, per-chat plans | [README.md](plans/README.md) |
| `registry/` | Format registry, source baselines, ledgers | [README.md](registry/README.md) |
| `reports/` | Sprint evidence, audit reports, certification | [_readme.md](reports/_readme.md) |
| `schemas/` | JSON and YAML schema definitions | [_readme.md](schemas/_readme.md) |
| `tools/` | All automation (supervisor, validators, oracle) | [_readme.md](tools/_readme.md) |

### Documentation

| Folder | Purpose | README |
|---|---|---|
| `docs/` | Architecture, policy, and governance docs | [README.md](docs/README.md) |
| `memory/` | Project decision history and memory files | [README.md](memory/README.md) |
| `taskcards/` | Sprint taskcard definitions | [README.md](taskcards/README.md) |
| `reviews/` | Portfolio assessment reviews | [_readme.md](reviews/_readme.md) |
| `templates/` | Evidence and onboarding templates | [_readme.md](templates/_readme.md) |
| `playbooks/` | Operational playbooks for format acquisition | [_readme.md](playbooks/_readme.md) |

### Pipeline Artifacts

| Folder | Purpose | README |
|---|---|---|
| `acquisition-packs/` | Format onboarding packs | [_readme.md](acquisition-packs/_readme.md) |
| `migration-maps/` | QName-to-source migration maps | [_readme.md](migration-maps/_readme.md) |
| `product-capability-matrix/` | POC capability tracking (system of record) | [_readme.md](product-capability-matrix/_readme.md) |
| `generated-requirements/` | Auto-generated requirements from specs | [_readme.md](generated-requirements/_readme.md) |
| `gate-readiness/` | Gate 8/11 readiness matrices | [_readme.md](gate-readiness/_readme.md) |
| `publication-readiness/` | Publication status tracking | [_readme.md](publication-readiness/_readme.md) |
| `release-manifests/` | Release manifest tracking | [_readme.md](release-manifests/_readme.md) |
| `packaging/` | Package definitions for Python/NET | [_readme.md](packaging/_readme.md) |
| `requirements-authority/` | Specification authority layer | [README.md](requirements-authority/README.md) |

### Shared Libraries

| Folder | Purpose | README |
|---|---|---|
| `shared/` | QName registry (active authority) | [_readme.md](shared/_readme.md) |
| `scripts/` | Orchestration scripts (PowerShell/Bash) | [_readme.md](scripts/_readme.md) |
| `drivers/` | Test generation templates (.py.tmpl) | [_readme.md](drivers/_readme.md) |

### Other

| Folder | Purpose | README |
|---|---|---|
| `dependency-artifacts/` | ZST dependency blocker docs | [README.md](dependency-artifacts/README.md) |
| `prototypes/` | Gate 4 proof-of-concept parsers | [_readme.md](prototypes/_readme.md) |

Canonical registry: [`registry/repository-root-folders.yaml`](registry/repository-root-folders.yaml) (51 entries).
Validated by V91 root structure validator on every sprint closeout.

<!-- END:REPOSITORY-NAVIGATION -->

---

## Agent Methodology and Fresh Chat Start

Agents must read `CLAUDE.md` and `AGENTS.md` before starting any work. Fresh chat sessions read `reports/supervisor/session-resume.md` to restore operational context.

| Resource | Purpose |
|---|---|
| [CLAUDE.md](CLAUDE.md) | Session start instructions and Supreme Directive |
| [AGENTS.md](AGENTS.md) | Operating contract for all executors (~60KB) |
| [plans/master-plan.md](plans/master-plan.md) | Single operational authority (42 sections) |
| [reports/supervisor/session-resume.md](reports/supervisor/session-resume.md) | Last sprint outcome and next action |
| [docs/agent-methodology-index.md](docs/agent-methodology-index.md) | Methodology index for plan and prompt work |
| [docs/fresh-chat-continuity-brief.md](docs/fresh-chat-continuity-brief.md) | Cross-chat continuity brief |
| [docs/prompts/README.md](docs/prompts/README.md) | Agent prompt templates |
| [docs/automation/supervisor-worker-contract.md](docs/automation/supervisor-worker-contract.md) | Evidence declaration schema |

---

## Known Limitations

- **Not commercially released:** All Python packages are `local_only_not_published`. All .NET products are `commercial_product_ready: false`. Gate 11 G11-G EXECUTION (commercial release) requires Babar Raza's business authority.
- **Spec parity incomplete (FODS):** FODS spec QName facades are complete (12/12 as of TC-SP-002, 2026-06-25); behavioral parity is partial — Python is read-only with CSV export; .NET provides a full mutation API (23 methods, 6 export formats). FODT spec parity is VERIFIED as of 2026-06-25 (TC-SP-004/005, SAL cache repaired with 4,936 ODF 1.3 facts).
- **No PyPI/NuGet publication:** Packages are installable locally via `packaging/python/build-local-packages.py` but not published to any public registry.
- **Four formats have no product code:** ORA, PAM, XPM, ZPAQ are at OBLIGATION_CREATED status with no source implementation.
- **Test counts fluctuate:** Per-sprint test counts vary as test files are added. There is no single stable cumulative count.
- **Supervisor autonomy limits:** Sprint orchestration requires an active LLM session. The autonomous loop does not run unattended as a background service.

---

## System Status Review

For a plain-English assessment of where the project stands — what works, what repeats, what scales, and what still needs work — see the full evidence-based review:

- **Full review:** [reports/system-status-review.md](reports/system-status-review.md)
- **Regenerate:** `python tools/readme_sync/generate_root_status.py`

<!-- BEGIN:SYSTEM-STATUS-SUMMARY generated=2026-07-01 source=reports/system-status-review.md -->
**Scorecard (out of 10):** Overall 7.5 | Repeatability 9 | Genericness 8 | Evidence 8 | Testability 8 | Future Readiness 7 | Production Readiness 4 | Source Quality 7 | Autonomy 8 | Governance 9

**Phase ratings:** 7 Green (governance, QName, product implementation, testing, evidence, autonomy, onboarding) | 7 Yellow (discovery, SAL, capability, feature planning, code generation, healing, docs) | 1 Orange (packaging/publication) | 0 Red

**Verdict:** Working, repeatable, well-governed system. Not commercially released. 20 formats prove the pipeline works. Strongest: governance enforcement (162 validators), repeatability (840 sprints, 3,187+ evidence bundles), oracle verification (73/73 PASS). Weakest: production readiness (no published packages, no external users). Pipeline is agent-orchestrated — AI agents perform the engineering work; human oversight applies only at commercial release gates.
<!-- END:SYSTEM-STATUS-SUMMARY -->

---

<!-- BEGIN:PROJECT-STATUS-REF generated=2026-07-02 source=PROJECT_STATUS.md -->
**Quick numbers (machinery):** 162 validators | 123 skills | 840 sprints

**Quick numbers (product):** 20 active formats | 73/73 oracle cases | 20/20 certified

For full auto-generated project status with per-format details and two-lane (machinery / product) breakdown, see [PROJECT_STATUS.md](PROJECT_STATUS.md#status-at-a-glance).
<!-- END:PROJECT-STATUS-REF -->

## Keeping This README Current

The root README contains values derived from canonical registries and reports. To detect drift and refresh:

| What drifts | Source of truth | Check command |
|---|---|---|
| Package count | `packaging/python/package-matrix.yaml` | `python -c "import yaml; d=yaml.safe_load(open('packaging/python/package-matrix.yaml')); print(len(d['packages']))"` |
| Validator count | `tools/supervisor/governance_validators*.py` | `grep -r "^def validate_" tools/supervisor/governance_validators*.py \| wc -l` |
| Sprint count | `reports/supervisor/maturity-trend.json` | `python -c "import json; print(json.load(open('reports/supervisor/maturity-trend.json'))['sprint_count'])"` |
| Oracle status | `oracle/formats/` | `ls oracle/formats/ \| wc -l` |
| Per-format READMEs | `tools/readme_sync/` | `python tools/readme_sync/run_sync.py --mode drift-only` |
| Project status | `PROJECT_STATUS.md` | `python tools/docs/generate_project_status.py` |
| Root README status | `tools/readme_sync/generate_root_status.py` | `python tools/readme_sync/generate_root_status.py --mode drift-only` |

**Autonomous trigger:** Root README drift is detected by `generate_root_status.py` during each autonomous cycle. The `/sync-readmes` skill refreshes per-format READMEs. The full system status review (`reports/system-status-review.md`) requires agent-assisted investigation.

**Manual trigger:** Re-run the root README investigation protocol as a Claude Code plan-mode task. The protocol is idempotent — a second unchanged run produces zero material changes.

---

## Contributing

See [GOVERNANCE.md](GOVERNANCE.md) for human contributor rules and gate approval processes. See [AGENTS.md](AGENTS.md) for agent operating rules. See [docs/governance/legal-and-licensing.md](docs/governance/legal-and-licensing.md) before working on any format.

All samples must have confirmed open-source licenses before being committed. All format work must pass the required gates before moving to later phases.

---

## License

Open-source components: Apache 2.0, see individual source files.
Commercial components: Proprietary, deferred to Gate 11.
Acquisition evidence and governance documents: Internal only, not released.
