# format-factory

A File Format Acquisition System that produces legal parsers, converters, importers, exporters, validators, and compatibility tools for structured file formats.

**Current state (2026-06-25):** 20 formats supported across Python FOSS and .NET commercial tracks. 14,498+ tests passing. 53 governance validators. 16 installable Python packages. Gate 11 G11-G sub-gate approved by Babar Raza 2026-06-05 (FODS, FODT, Netpbm). Product deepening mission COMPLETE: all 14 Python FOSS formats at PROOF_LEVEL_4+.

---

## What This Project Does

format-factory builds production-quality, legally vetted format support libraries for common file formats. Every format supported by this project passes a formal acquisition pipeline: legal review, evidence gathering, sample validation, prototype development, security testing, product mapping, and human approval.

The project never engages in unauthorized binary reverse engineering, bypasses access controls, or violates intellectual property rights.

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

## Products

### Python FOSS Track (16 installable packages, local only)

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
| CSV | Comma-separated values | `aspose-format-factory-csv` | PASS |
| ZST | Zstandard compression | `aspose-format-factory-zst` | PASS |
| PBM/PGM/PPM | Netpbm image formats | `aspose-format-factory-pbm/pgm/ppm` | PASS |

All packages: `publish_status: local_only_not_published`, `publication_authorized: false`. See `packaging/python/package-matrix.yaml`.

### .NET Commercial Track (3 products)

| Format | .NET Project | Gate 11 G11-G | Status |
|--------|-------------|---------------|--------|
| FODS | `src/net/fods/` | APPROVED 2026-06-05 (Babar Raza) | 618 tests, not commercially released |
| FODT | `src/net/fodt/` | APPROVED 2026-06-05 (Babar Raza) | 568 tests, not commercially released |
| Netpbm | `src/net/netpbm/` | APPROVED 2026-06-05 (Babar Raza) | 423 tests, not commercially released |

`commercial_product_ready: false` for all entries — requires Gate 11 G11-G EXECUTION approval (Babar Raza only) and full spec-parity verification.

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

- **Test Suite:** 14,498+ tests passing, 0 failures (as of product-deepening-mission-complete sprint 2026-06-25). Tests span unit, integration, roundtrip, analytics, spec-fact traceability, and installed-package workflow proofs.
- **Test Framework:** pytest with `--import-mode=importlib` and 120-second per-test timeout. Dual conftest pattern handles stdlib module shadowing (`csv`, `html`).
- **Quality Gates:** 53 programmatic governance validators (V1-V53) block sprints on policy violations (`tools/supervisor/governance_validators.py`). Validators enforce: declaration schema compliance, evidence artifact existence, anti-skip checks, skill-first execution, spec-fact references, QName compliance, architecture stub detection, analytics separation, lane enforcement, and package manifest completeness.
- **Source Size Policy:** Maximum 800 LOC and 60 functions per production file, tracked in `registry/source-structure-baseline.json`. Violations are frozen at `baseline_loc_cap` (write-once).
- **Security:** Gate 8 requires security review before any format reaches product. Parser threat model covers XXE, billion laughs, zip bombs, path traversal, malformed input handling, memory limits, recursion limits, and binary parser safety (`docs/security.md`).
- **QName Compliance:** Every exported Python class carries a `spec_qname` class attribute mapping to its canonical ODF/format specification element (enforced by V51-V53). Spec authority classes live in `{format}/spec/`; Compat/ facades expose simplified names.

---

## Autonomous Supervision Architecture

format-factory uses an autonomous supervisor pipeline that manages multi-sprint execution with bounded repair and evidence materialization. Over 585 autonomous sprint cycles have been completed.

- **State Management:** Session state persisted in `reports/supervisor/session-resume.md` and `.local/supervisor/continuation-signal.json`. Cross-window recovery restores full operational context without requiring prior conversation history.
- **Flow Orchestration:** 4-stream architecture (Mainstream Product, Acceleration, Skills/Governed Execution, Supervisor/Autonomous Continuation) with a 15-state taskcard machine governing work item lifecycle. Pipeline: sprint start → execute work items → write evidence declaration → validate with 53 governance validators → grade work items → generate next sprint → check continuation signal.
- **Boundary Enforcement:** `AGENTS.md` (~60KB operating contract) defines non-negotiable rules for all automated executors. 53 governance validators programmatically block sprints on policy violations. Gate 11 G11-G approval requires explicit human business authority.
- **Adaptive Repair:** `tools/supervisor/bounded_repair_engine.py` classifies test and build failures into 6 categories (IMPORT, SYNTAX, ATTRIBUTE, NAME, ASSERTION, TIMEOUT) and applies targeted repairs with automatic rollback on failure.
- **CCI (Cross-Chat Continuation Isolation):** `session_id` field in continuation signals prevents cross-chat state contamination. SESSION_MISMATCH is a non-overridable hard stop.

Key implementation files:

- `tools/supervisor/autonomous_cycle.py` — Sprint execution and evidence pipeline
- `tools/supervisor/governance_validators.py` — 53 programmatic quality gates (V1-V53)
- `tools/supervisor/lane_enforcement_validator.py` — Cross-lane file ownership enforcement
- `tools/supervisor/bounded_repair_engine.py` — Error classification and bounded repair
- `tools/supervisor/check_continuation.py` — Autonomous loop continuation gate
- `packaging/python/build-local-packages.py` — Local Python wheel builder for all 16 formats

---

## Project Status

| Item | Status |
|------|--------|
| Python FOSS formats | 20 formats in source; 16 installable packages; all local only |
| .NET commercial formats | FODS, FODT, Netpbm; G11-G sub-gate approved; not commercially released |
| Gate 11 G11-G | APPROVED by Babar Raza 2026-06-05 (sub-gate); G11-G EXECUTION pending |
| commercial_product_ready | false (all entries) |
| Tests passing | 14,498+ Python + .NET (0 failures) |
| Governance validators | 53 (V1-V53) |
| Product deepening | COMPLETE — all 14 Python FOSS formats at PROOF_LEVEL_4+ |
| Spec parity (FODS) | PARTIAL — 3/12 qnames have Compat/ facades |
| Spec parity (FODT) | BLOCKED — SAL cache missing FODT ODF 1.3 facts |
| Autonomous loop | ACTIVE — MODE 4 (MCP active), AUTONOMOUS_CONTINUE: YES |

For canonical per-format status, see:
- `product-capability-matrix/poc-targets.yaml` — product targets and gate status
- `registry/parity-matrix.yaml` — Python/.NET parity tracking
- `reports/supervisor/session-resume.md` — last sprint outcome and next action
- `reports/supervisor/approval-gates.md` — current continuation authorization

---

## Repository Structure

```text
docs/                 Architecture, policy, process, and governance documentation
plans/                Living master plan (master-plan.md) and per-chat plan files
registry/             Format registry, parity matrix, scoring model, source baseline
shared/qname-registry/  Canonical QName registry YAMLs for all 20 formats
acquisition-packs/    Per-format evidence, legal notes, samples, parser notes
samples/              Licensed sample corpus with provenance records
schemas/              Neutral-model and format-understanding schemas
src/python/           Python FOSS production source (one package per format)
src/net/              .NET commercial production source (one project per format)
tests/python/         Python format tests
tests/net/            .NET format tests
tests/supervisor/     Governance and supervisor infrastructure tests
tools/supervisor/     Autonomous cycle, governance validators, sprint tools
tools/spec/           SAL (Specification Authority Layer) tools
packaging/python/     Local Python wheel builder and package matrix
examples/python/      Consumer roundtrip proof scripts (one per format)
reports/              Sprint reviews, capability maps, gap ledger, audit reports
.supervisor/          Supervisor knowledge base, skill registry, context packs
.claude/              Claude Code project configuration and slash commands
```

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
| [docs/automation/supervisor-worker-contract.md](docs/automation/supervisor-worker-contract.md) | Evidence declaration schema |

---

## Contributing

See [GOVERNANCE.md](GOVERNANCE.md) for human contributor rules and gate approval processes. See [AGENTS.md](AGENTS.md) for agent operating rules. See [docs/legal-and-licensing.md](docs/legal-and-licensing.md) before working on any format.

All samples must have confirmed open-source licenses before being committed. All format work must pass the required gates before moving to later phases.

---

## License

Open-source components: Apache 2.0, see individual source files.
Commercial components: Proprietary, deferred to Gate 11.
Acquisition evidence and governance documents: Internal only, not released.
