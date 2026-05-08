# format-factory

A File Format Acquisition System that produces legal parsers, converters, importers, exporters, validators, and compatibility tools for structured file formats.

---

## What This Project Does

format-factory builds production-quality, legally vetted format support libraries for common file formats. Every format supported by this project has passed a formal acquisition pipeline: legal review, evidence gathering, sample validation, prototype development, security testing, and product mapping. Nothing ships without passing all applicable gates.

The project never engages in unauthorized binary reverse engineering, bypasses access controls, or violates intellectual property rights.

---

## Products

| Track | Technology | License | Status |
|---|---|---|---|
| Python open-source library | Python 3.11+ | Apache 2.0 | No release yet — source not created (Phase 4+) |
| .NET product library | net8.0, net10.0 | Proprietary (FOSS packaging deferred — DEC-033) | No release yet — source not created (Phase 4+) |

Source layout (Phase 4+): `src/python/{format}/` for Python FOSS; `src/net/{format}/` for .NET product.

---

## First Pilot: FODS

**Gate 1 passed — 2026-05-04. Gate 2 passed — 2026-05-05. Gate 3 passed — 2026-05-05. Gate 4 passed — 2026-05-06. Gate 5 passed — 2026-05-06. Gate 6 passed — 2026-05-08. Gate 7 passed — 2026-05-08. Approved by: Babar Raza. FODS score: 93/100 (Accept band).**

**FODS** — Flat OpenDocument Spreadsheet — is the active pilot format. It is a flat XML variant of the ODF spreadsheet format, published by OASIS under royalty-free terms as part of ODF 1.3. Single-file XML, well-documented specification, no ZIP complexity, permissive license.

Gate 6 (Oracle Comparison) PASSED (Babar Raza, 2026-05-08, run044). ORACLE_COMPARE: PASS 3/4, WARN 1/4 (multi-sheet CSV export limitation — expected, not a parser defect). Gate 7 (Fuzz Testing) PASSED (Babar Raza, 2026-05-08, run045). GATE7_FUZZ_TEST PASS 18/18 CRASH 0/18. Gate 8 (Security Review) PASSED (Babar Raza, 2026-05-08, run046). GATE8_SECURITY_REVIEW: PASS. TC-0038 DEC-034 PASS 20/20. FODT Gates 1-5 ALL PASSED (Babar Raza): Gates 1-4 run041/043/044/045; Gate 5 run046 (FODT_NEUTRAL_MODEL_VALIDATION PASS 4/4). FODT Gates 1-6 ALL PASSED (Babar Raza, run041-run047). FODS Gate 9 PASSED (Babar Raza, 2026-05-08, run047; tier-map.yaml v1.0). FODS Gate 10 PASSED (Babar Raza, 2026-05-08, run048). FODT Gate 7 PASSED (Babar Raza, 2026-05-08, run048; FODT_GATE7_FUZZ_TEST PASS 18/18). FODT Gate 8 PASSED (Babar Raza, 2026-05-08, run048). FODT Gate 9 product-mapping planning_ready. ODF reuse strategy: docs/odf-flat-family-reuse-strategy.md.

---

## Supported Format Families

The project is organized around six format families:

| Family | Description | Examples |
|---|---|---|
| Cells | Spreadsheets and tabular data | FODS, ODS, XLSX |
| Words | Word processing documents | FODT, ODT, DOCX |
| Slides | Presentations | FODP, ODP, PPTX |
| Imaging | Raster and vector images | SVG, PNG (with metadata) |
| Diagram/CAD | Diagrams and technical drawings | DrawingML, DXF |
| Archive | Container and archive formats | ZIP, TAR (when format-relevant) |

---

## Acquisition Pipeline

Every format passes through 11 mandatory gates before any product code is written:

1. **Gate 1** — Candidate Accepted (scoring, legal classification)
2. **Gate 2** — Evidence Complete (spec analysis, legal notes)
3. **Gate 3** — Sample Corpus Ready (licensed samples with confirmed provenance)
4. **Gate 4** — Prototype Complete (working parser, security baseline)
5. **Gate 5** — Neutral Model Defined (format-family data schema)
6. **Gate 6** — Oracle Comparison Complete (discrepancy analysis)
7. **Gate 7** — Fuzz Testing Complete (minimum 10,000 iterations for XML)
8. **Gate 8** — Security Review Complete (human sign-off required)
9. **Gate 9** — Product Mapping Complete (tier assignment, delivery plan)
10. **Gate 10** — OSS Readiness Complete (production source, release manifest)
11. **Gate 11** — Commercial Readiness Complete (commercial tier, proprietary manifest)

---

## Project Status

**Current phase:** Phase 3 — FODS Gates 1-10 ALL PASSED; Gate 11 planning_ready. FODT Gates 1-8 ALL PASSED; Gate 9 product-mapping planning_ready.

- Phase 0 (Foundation): Complete — accepted 2026-05-04
- Phase 1A (Scoring): Complete — FODS scored 93/100, Accept band
- Phase 1B (Gate 1): Complete — Gate 1 passed, approved by Babar Raza, 2026-05-04
- Phase 2 (Spec + Legal Evidence): Complete — Gate 2 passed, approved by Babar Raza, 2026-05-05
- Phase 3 (Sample Corpus): Complete — Gate 3 passed, approved by Babar Raza, 2026-05-05; 4 samples validated 4/4 PASS
- Phase 3 (Parser Prototype): Complete — Gate 4 passed, approved by Babar Raza, 2026-05-06
- Phase 3 (Neutral Model): Complete — Gate 5 passed, approved by Babar Raza, 2026-05-06
- Phase 3 (Oracle Comparison): Complete — Gate 6 passed, approved by Babar Raza, 2026-05-08; ORACLE_COMPARE PASS 3/4 WARN 1/4
- Phase 3 (Fuzz Testing): Complete — Gate 7 passed, approved by Babar Raza, 2026-05-08; GATE7_FUZZ_TEST PASS 18/18 CRASH 0/18; 18 malformed fixtures
- Phase 3 (Security Review): Complete — Gate 8 passed, approved by Babar Raza, 2026-05-08; GATE8_SECURITY_REVIEW: PASS
- Phase 3 (Product Mapping): Complete — Gate 9 passed, approved by Babar Raza, 2026-05-08; tier-map.yaml v1.0; Tiers 0-2 first OSS release
- Phase 3/4 (OSS Readiness): Complete — Gate 10 passed, approved by Babar Raza, 2026-05-08; product-source readiness confirmed; Gate 11 planning_ready
- FODT Gates 1-9: Complete (Gate 9 PASSED run050) — Gates 1-8 all passed (run041-run048, Babar Raza); Gate 9 product-mapping planning_ready
- Format Understanding Layer (run049): FUL-001 schemas created, FUL-002 FODS 6 files compiled, FUL-003 FODT 6 files compiled (product-readiness partial, Gate 9 required)

For current status, active work, and decisions, see [plans/master-plan.md](plans/master-plan.md).

---

## Repository Structure

```
docs/         Architecture, policy, and process documentation
plans/        Living master plan (single operational authority)
taskcards/    Atomic work units (TC-NNNN-*.md)
registry/     Format registry and scoring model
acquisition-packs/  Per-format evidence, legal notes, samples, parser notes
samples/      Licensed sample corpus with provenance records
schemas/      Neutral-model schemas (format-family level)
prototypes/   Reference prototype parsers (internal only)
src/          Production source code (Phase 4+)
tests/        Test fixtures, oracle outputs, fuzz seeds (Phase 3+)
tools/        Acquisition, scoring, validation, and LLM tools
reports/      Security and legal reports
.claude/      Claude Code project configuration and commands
```

---

## Agent Methodology and Fresh Chat Start

Agents must start from the methodology index when producing plans or prompts.
Fresh chat sessions should read the continuity brief before any planning work.
Evidence bundle review must precede next prompt generation when a bundle exists.
The local methodology is part of repo governance -- not optional guidance.
Product work remains governed by gates and the master plan.

| Resource | Purpose |
|----------|---------|
| [docs/agent-methodology-index.md](docs/agent-methodology-index.md) | Start here for all plan and prompt work |
| [docs/planning-methodology.md](docs/planning-methodology.md) | Core planning principles and prompt anatomy |
| [docs/agent-execution-handoff-standard.md](docs/agent-execution-handoff-standard.md) | Execution handoff standard |
| [docs/plan-hardening-checklist.md](docs/plan-hardening-checklist.md) | 22-item plan hardening checklist |
| [docs/fresh-chat-continuity-brief.md](docs/fresh-chat-continuity-brief.md) | Fresh session orientation guide |
| [docs/prompts/README.md](docs/prompts/README.md) | Prompt template index |
| [memory/00-index.md](memory/00-index.md) | Memory package index |

---

## Contributing

See [GOVERNANCE.md](GOVERNANCE.md) for human contributor rules and gate approval processes. See [AGENTS.md](AGENTS.md) for agent operating rules. See [docs/legal-and-licensing.md](docs/legal-and-licensing.md) before working on any format.

All samples must have confirmed open-source licenses before being committed. All format work must pass Gate 2 (legal review) before prototype development begins.

---

## License

Open-source components: Apache 2.0 (see individual source files once they exist).
Commercial components: Proprietary (deferred to Gate 11).
Acquisition evidence and governance documents: Internal only — not released.
