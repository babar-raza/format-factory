# format-factory

A File Format Acquisition System that produces legal parsers, converters, importers, exporters, validators, and compatibility tools for structured file formats.

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

## Products

| Track | Technology | License | Status |
|---|---|---|---|
| Python open-source library | Python 3.11+ | Apache 2.0 | Source created for FODS and FODT; no public release yet |
| .NET product library | net8.0, net10.0 | Proprietary (FOSS packaging deferred, DEC-033) | C4-C6 vertical slice created for FODS and FODT; not commercial-ready; Gate 11 NOT approved |

Source layout: `src/python/{format}/` for Python FOSS; `src/net/{format}/` for .NET product.

---

## First Pilots: FODS and FODT

**FODS Gates 1-10 passed. FODT Gates 1-10 passed. Approved gate decisions are recorded in `registry/format-registry.yaml`.**

**FODS**, Flat OpenDocument Spreadsheet, is the first pilot format. It is a flat XML variant of the ODF spreadsheet format, published by OASIS under royalty-free terms as part of ODF 1.3. It is a single XML file, so it avoids ZIP container complexity.

**FODT**, Flat OpenDocument Text, is the second pilot format. It reuses the ODF flat-XML acquisition strategy while proving the pipeline can handle a different product family: word-processing documents.

Current implementation status:

- FODS Python source exists in `src/python/fods/`; Gate 11 commercial_readiness_in_progress (NOT approved).
- FODT Python source exists in `src/python/fodt/`; Gate 10 approved by Babar Raza 2026-05-11; Gate 11 commercial_readiness_in_progress (NOT approved).
- .NET C4-C6 vertical slice exists for both formats in `src/net/fods/` and `src/net/fodt/`; not commercial-ready; Gate 11 NOT approved; commercial_product_ready: false.
- ODF reuse strategy: [docs/odf-flat-family-reuse-strategy.md](docs/odf-flat-family-reuse-strategy.md).

---

## Supported Format Families

The project is organized around six format families:

| Family | Description | Examples |
|---|---|---|
| Cells | Spreadsheets and tabular data | FODS, ODS, XLSX |
| Words | Word processing documents | FODT, ODT, DOCX |
| Slides | Presentations | FODP, ODP, PPTX |
| Imaging | Raster and vector images | SVG, PNG with metadata |
| Diagram/CAD | Diagrams and technical drawings | DrawingML, DXF |
| Archive | Container and archive formats | ZIP, TAR when format-relevant |

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

Agents may prepare evidence, but only a human can approve a gate.

---

## Project Status

**Current phase:** Phase 3/4. FODS Gates 1-10 are passed and Gate 11 is `commercial_readiness_in_progress` (NOT approved). FODT Gates 1-10 are passed, Gate 11 is `commercial_readiness_in_progress` (NOT approved). DEC-033 resolved as Option B (.NET Commercial Only). commercial_product_ready: false. ZST Gates 1-3 PASSED (R13B/R14/R16, 2026-05-15, delegated). ZST Gate 4 planning taskcard created (R17).

- Phase 0 Foundation: Complete, accepted 2026-05-04.
- FODS Gates 1-10: Complete, approved by Babar Raza across run017 through run048.
- FODS Python Phase 4 source: Created under `src/python/fods/` in run051, TC-0050 completed.
- FODT Gates 1-10: Complete, approved by Babar Raza across run041 through TC-0052 (Gate 10 approved 2026-05-11).
- FODT Gate 11: commercial_readiness_in_progress; DEC-033 resolved Option B; NOT approved.
- FODT Python Phase 4 source: Created under `src/python/fodt/` with 115/115 tests passing (TC-0052 completed).
- Format Understanding Layer: FUL-001 schemas created, FUL-002 FODS completed, FUL-003 FODT completed.
- .NET C4-C6 vertical slice: Created for FODS (src/net/fods/) and FODT (src/net/fodt/); DEC-033 resolved Option B; commercial_product_ready: false.
- ZST (Zstandard): Gate 1 APPROVED (R13B, 2026-05-15, delegated). Gate 2 PASSED (R14, 2026-05-15). **Gate 3 PASSED (R16, 2026-05-15, delegated):** 11-file corpus acquired (8 valid + 3 invalid); 57 corpus tests PASS; DEC-034 IV PASS. Gate 4 planning taskcard created (ZST-R17-GATE4-PARSER-PROTOTYPE-PLANNING.md).

For current status, active work, and decisions, see [plans/master-plan.md](plans/master-plan.md). The master plan and [registry/format-registry.yaml](registry/format-registry.yaml) are the authoritative status sources.

---

## Repository Structure

```text
docs/         Architecture, policy, and process documentation
plans/        Living master plan, single operational authority
taskcards/    Atomic work units
registry/     Format registry and scoring model
acquisition-packs/  Per-format evidence, legal notes, samples, parser notes
samples/      Licensed sample corpus with provenance records
schemas/      Neutral-model and format-understanding schemas
prototypes/   Reference prototype parsers, internal only
src/          Production source code
tests/        Test fixtures, oracle outputs, fuzz seeds, product tests
tools/        Acquisition, scoring, validation, evidence, and oracle tools
reports/      Security and legal reports
.claude/      Claude Code project configuration and commands
```

---

## Agent Methodology and Fresh Chat Start

Agents must start from the methodology index when producing plans or prompts. Fresh chat sessions should read the continuity brief before planning work. Evidence bundle review must precede next prompt generation when a bundle exists.

| Resource | Purpose |
|---|---|
| [docs/agent-methodology-index.md](docs/agent-methodology-index.md) | Start here for plan and prompt work |
| [docs/planning-methodology.md](docs/planning-methodology.md) | Core planning principles and prompt anatomy |
| [docs/agent-execution-handoff-standard.md](docs/agent-execution-handoff-standard.md) | Execution handoff standard |
| [docs/plan-hardening-checklist.md](docs/plan-hardening-checklist.md) | 22-item plan hardening checklist |
| [docs/fresh-chat-continuity-brief.md](docs/fresh-chat-continuity-brief.md) | Fresh session orientation guide |
| [docs/prompts/README.md](docs/prompts/README.md) | Prompt template index |
| [memory/00-index.md](memory/00-index.md) | Memory package index |

---

## Contributing

See [GOVERNANCE.md](GOVERNANCE.md) for human contributor rules and gate approval processes. See [AGENTS.md](AGENTS.md) for agent operating rules. See [docs/legal-and-licensing.md](docs/legal-and-licensing.md) before working on any format.

All samples must have confirmed open-source licenses before being committed. All format work must pass the required gates before moving to later phases.

---

## License

Open-source components: Apache 2.0, see individual source files.
Commercial components: Proprietary, deferred to Gate 11.
Acquisition evidence and governance documents: Internal only, not released.
