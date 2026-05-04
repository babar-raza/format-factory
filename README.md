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
| Python open-source library | Python 3.11+ | Apache 2.0 | Phase 0 — no formats released yet |
| .NET product library | net8.0, net10.0 | Proprietary (FOSS packaging deferred — DEC-033) | Phase 0 — no formats released yet |

Source layout (Phase 4+): `src/python/{format}/` for Python FOSS; `src/net/{format}/` for .NET product.

---

## First Pilot: FODS

The first format to be acquired is **FODS** — Flat OpenDocument Spreadsheet — a flat XML variant of the ODF spreadsheet format. FODS is published by OASIS under royalty-free terms as part of ODF 1.3. It is a suitable pilot format: single-file XML, well-documented specification, no ZIP complexity, permissive license.

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

**Current phase:** Phase 0 — Foundation

Phase 0 creates governance, policy, folder structure, and templates. No format-specific content exists yet. No product code exists yet.

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

## Contributing

See [GOVERNANCE.md](GOVERNANCE.md) for human contributor rules and gate approval processes. See [AGENTS.md](AGENTS.md) for agent operating rules. See [docs/legal-and-licensing.md](docs/legal-and-licensing.md) before working on any format.

All samples must have confirmed open-source licenses before being committed. All format work must pass Gate 2 (legal review) before prototype development begins.

---

## License

Open-source components: Apache 2.0 (see individual source files once they exist).
Commercial components: Proprietary (deferred to Gate 11).
Acquisition evidence and governance documents: Internal only — not released.
