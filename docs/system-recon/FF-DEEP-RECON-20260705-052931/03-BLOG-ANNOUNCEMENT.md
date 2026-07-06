# Format Factory: Building File-Format Libraries from Specifications with AI-Governed Automation

## Summary

Format Factory is an open-source system that converts file-format specifications into tested, legally vetted software libraries. In 65 days of development, it has produced 20 Python and 10 .NET format libraries, verified by nearly 40,000 tests, governed by 161 automated validators, and developed through 840+ AI-supervised sprint cycles. This post explains what it does, how it works, and what it has achieved so far.

---

## The Problem: Format Libraries Are Tedious to Build Correctly

Every software application that reads or writes a file format — spreadsheets, documents, images, configuration files, compressed archives — depends on a format library. Building one correctly is difficult:

- **Specifications are dense.** The OpenDocument Format specification alone runs hundreds of pages. Developers must translate abstract XML schema definitions into concrete parsing, writing, and editing code.
- **Legal compliance matters.** Some format specifications carry patent obligations, licensing restrictions, or usage constraints. Using a format without understanding its legal posture can create liability.
- **Testing is hard to ground.** Without deterministic test oracles derived from the specification itself, tests often verify only what the developer expected rather than what the specification requires.
- **Maintenance scales poorly.** Supporting a second language (.NET alongside Python, or vice versa) traditionally means duplicating work. Traceability from specification elements to source code is rarely maintained.

Most format libraries are built by reading the spec once, writing a parser, and hoping the tests cover enough. Format Factory tries a different approach.

---

## What Format Factory Is

Format Factory is a system with two distinct halves:

**Products** are deterministic, spec-aligned libraries that parse, write, validate, and convert file formats. They are what users install. There are no AI calls at runtime — products are conventional, dependency-light code.

**Machinery** is an autonomous development pipeline that plans work, executes sprints, validates evidence, grades outcomes, and generates the next sprint's tasks. The machinery governs the development process but is never shipped to end users.

Products are the deliverables. Machinery is the factory that builds, tests, and certifies them.

---

## How the Pipeline Works

Adding a new format follows a governed pipeline with 11 gates:

1. **Scoring.** A 7-factor model evaluates the format on legal safety, specification availability, structural complexity, community demand, strategic value, implementation complexity, and family overlap. The model produces a score out of 100.

2. **Legal review.** The format's specification license is classified. OASIS royalty-free formats (like ODF) are Category 1. Formats requiring patent licenses or carrying usage restrictions are scored lower or rejected outright.

3. **Specification acquisition.** The specification document is downloaded, cached, and hash-verified.

4. **Prototype development.** A minimal parser is built to validate that the format can be processed.

5. **Fact extraction.** The Specification Authority Layer (SAL) extracts structured, machine-readable facts from the specification. For the Flat OpenDocument Spreadsheet format, this produced approximately 4,988 facts covering XML element definitions, attribute constraints, namespace bindings, and structural rules.

6. **QName mapping.** Each specification-qualified name (like `table:table-cell`) is mapped to a canonical class name (like `Table.TableCell`) in a registry. This mapping is shared across languages — the same QName maps to the same conceptual class in both Python and .NET.

7. **Capability modeling.** The system tracks what each format implementation can and cannot do. A gap ledger records missing capabilities — for example, "FODS parse supports cells but not conditional formatting." Gaps drive future work prioritization.

8. **Source implementation.** Assistants governed by skills write the actual parser, writer, analytics, and model code. Each format follows a consistent structure: a core codec module, spec-aligned domain classes (with `spec_qname` declarations linking back to the specification), format-prefixed facade classes for ergonomic API access, and analytics functions backed by specification facts.

9. **Oracle verification.** Deterministic test cases derived from the specification verify that the parser handles each element correctly. FODS has 8 oracle cases covering document structure, table elements, cell types, and value attributes. All 20 Python formats pass their oracle suites (73 out of 73 cases pass).

10. **Testing.** The test suite contains 39,864 collected tests across unit, integration, roundtrip, oracle, security, and governance categories. Tests run in layered tiers — fast structural tests first, then focused single-format tests, then integration and cross-format tests.

11. **Release gating.** Gate 11 is the commercial release gate. It is currently not approved — publication to PyPI and NuGet requires a business decision by the project owner.

---

## Specification Facts and Capability Modeling

The specification-to-code traceability chain is one of the system's distinguishing features. Here is how it works in practice for the FODS (Flat OpenDocument Spreadsheet) format:

- The ODF 1.3 specification defines an element `table:table-cell` with attributes like `office:value-type`, `table:formula`, and child elements like `text:p`.
- SAL extracts this as a structured fact: the element's namespace, local name, attributes, constraints, and parent/child relationships.
- The QName registry maps `table:table-cell` to the canonical class `Table.TableCell`.
- In Python, `src/python/fods/spec/table/table_cell.py` implements this class with `spec_qname: ClassVar[str] = "table:table-cell"`.
- In the `Compat/` directory, `fods_cell.py` provides a format-prefixed facade `FodsCell` that wraps `Table.TableCell`.
- The parser (`parser.py`) uses the ODF namespace URIs to identify `table:table-cell` elements during streaming XML parsing and populates the model accordingly.
- An oracle case (`fods-valid-003`) verifies that parsing a sample file with typed cell values produces the correct model structure.

This traceability chain — specification element to fact to QName to class to parser to oracle — is maintained for 21 formats across 21 QName registry files.

---

## Source Code and Object Models

Each Python format package exposes a straightforward API. For FODS:

```python
from fods import parse_fods, write_fods

# Parse a spreadsheet
model = parse_fods("data.fods")
print(f"Sheets: {len(model['sheets'])}")

# Access cell data
for row in model['sheets'][0]['rows']:
    for cell in row['cells']:
        print(cell.get('value'), cell.get('type'))

# Write back (round-trip)
write_fods(model, "output.fods")
```

For ZST (Zstandard compression):

```python
from zst import compress_bytes, decompress_bytes, validate_roundtrip

data = b"example data " * 1000
compressed = compress_bytes(data)   # 13,000 -> ~50 bytes
original = decompress_bytes(compressed)
assert original == data
result = validate_roundtrip(data)   # {'valid': True, 'compression_ratio': 0.003}
```

The .NET libraries follow a class-based pattern. FODS .NET (10,197 lines of C#) provides `FodsDocument` with parse, edit, save, and export operations — including export to CSV, HTML, JSON, ODS, PDF, and PNG.

---

## Tests, Oracle Cases, and Traceability

The project currently maintains:

- **39,864 tests** collected by pytest across Python and machinery categories
- **73 oracle cases** across 20 formats, all passing
- **161 governance validators** enforcing code quality, spec alignment, naming conventions, and structural constraints
- **6 test layers** from fast structural checks through full cross-format suites

A representative test run during this reconnaissance: FODS parser tests ran 1,571 tests in 10 seconds (all pass). ZST tests ran 1,316 tests in 9 seconds (all pass). Both suites include roundtrip verification — parse, modify, write, re-parse — confirming that the format libraries preserve data integrity through edit cycles.

Security testing includes XXE protection (using `defusedxml`), file-size limits, and fuzz testing with malformed inputs (18 FODS malformed fixtures at Gate 7).

---

## Agentic Work Through Skills and Commands

Development is driven by AI agents (primarily Claude Code) operating under strict governance:

- **123 registered skills** define what the agent can do — from `/new-format-kickstart` (scaffold a new format package) to `/add-python-api` (add a public API function) to `/run-oracle` (execute oracle verification).
- **124 Claude commands** provide executable prompts for specific operations.
- **120 active capabilities** are tracked in a capability registry, each mapping to specific product tracks (FOSS Python, .NET, governance, planning, etc.).

The agent does not operate freely. Every source mutation must go through a registered skill. Every sprint's output is declared as evidence, validated by the sprint executor, graded by the autonomous cycle, and checked by governance validators before the next sprint begins.

---

## Supervisor, Governance, and Rework

The supervisor system orchestrates the autonomous development loop:

1. The agent reads the current sprint prompt (`next-sprint.md`).
2. It executes the sprint — writing code, running tests, producing evidence.
3. It submits an evidence declaration describing what was done.
4. The supervisor validates the declaration against 161 governance validators.
5. The autonomous cycle grades each work item (accepted, rework, rejected).
6. The continuation checker decides whether to proceed or stop.
7. If continuing, a new `next-sprint.md` is generated and the loop repeats.

Over 840 autonomous sprint cycles have been completed through this loop. The sprint history is preserved in the `reports/` directory (402 MB of structured reports).

Governance validators check concerns ranging from code structure (file size caps, function count limits) to specification alignment (QName coverage, spec_qname declarations) to process compliance (evidence formatting, skill attribution). When a validator fails, the system generates rework items that must be addressed before product deepening resumes.

---

## Current Format and Platform Coverage

**20 Python FOSS libraries** cover spreadsheets (FODS, ODS, CSV, TSV, DIF, SYLK, Gnumeric), documents (FODT, ODT, ABW), presentations (FODP), drawings (FODG), images (XCF, QOI, PBM, PGM, PPM), data interchange (NDJSON, TOML), and compression (ZST).

**10 .NET libraries** cover a subset with deeper functionality: FODS .NET includes cell editing, style editing, and export to six output formats.

All 20 Python formats pass oracle verification. Parse functionality works across all formats. Write/save support is available for 17 of 20 Python formats (3 are read-only: QOI, XCF, ZST). Export capability is concentrated in FODS and ODS (CSV export) and the .NET track (CSV, HTML, JSON, ODS, PDF, PNG).

---

## What Has Been Proven

- **Specification-grounded parsing works.** 73 oracle cases derived from specifications pass, confirming that parsers implement what the specs define — not just what the developer expected.
- **Round-trip fidelity is achievable.** FODS parse-write-parse cycles produce identical model structures.
- **Automated governance scales.** 161 validators enforce quality rules that would be impossible to check manually across 39,864 tests and 77,000 lines of product code.
- **The pipeline is repeatable.** 20 formats have been brought through the same pipeline. Adding format 21 follows the same governed process.

---

## What Remains Incomplete

- **No public packages.** Neither Python packages (PyPI) nor .NET packages (NuGet) have been published. Gate 11 commercial release requires a business decision.
- **Write support is nearly complete but 3 formats remain read-only.** QOI, XCF, and ZST lack same-format save.
- **Export is narrow.** Cross-format export is concentrated in FODS and ODS (CSV). Most formats support parse and write but not export to other formats.
- **SAL extraction involves AI.** Fact extraction from specifications is not fully deterministic — it involves AI-assisted analysis steps.
- **.NET lags Python.** 10 .NET formats versus 20 Python formats.
- **The machinery is large.** 85,000 lines of supervisor code govern 77,000 lines of product code. This ratio is intentional (the factory is bigger than any single product) but creates maintenance cost.

---

## Technical and Business Relevance

Format Factory demonstrates that specification-driven development of format libraries, combined with AI-governed automation, can produce traceable, tested, legally vetted code at a pace that would be difficult to achieve manually. In 65 days, the system produced 30 format libraries across two languages with nearly 40,000 tests — a throughput that reflects the value of structured automation.

The approach is relevant to:
- **Document processing platforms** needing to add format support without building from scratch.
- **Enterprise software** requiring legal traceability for format implementations.
- **Standards bodies** wanting reference implementations aligned to their specifications.
- **Developer tools** that need lightweight, dependency-free format parsers.

---

## Near-Term Direction

Based on active plans and gap ledgers:
- Closing the remaining 3 write-support gaps (QOI, XCF, ZST)
- Completing .NET parity for high-priority formats
- Addressing monolithic analytics files that exceed governance size limits
- Preparing Gate 11 submission for FODS and FODT
- Adding SAL facts for the four remaining zero-fact formats (ORA, PAM, XPM, ZPAQ)

---

## A Restrained Conclusion

Format Factory is a working system, not a finished product. It proves that a governed, specification-driven, AI-assisted pipeline can produce file-format libraries with strong traceability and test coverage. The machinery is elaborate — perhaps more elaborate than it needs to be at this stage. The product libraries are functional but not yet published. The gap between "working locally" and "available to users" is real and is gated by a business decision rather than a technical blocker.

What exists today is a foundation: 20 tested Python libraries, 10 tested .NET libraries, a governed pipeline that can add more, and a body of evidence showing that the approach works. Whether it scales to 50 or 100 formats — and whether the publication gate opens — remains to be seen.

---

## Verification Basis

- **Inspected commits**: `94dd5308` (initial, 2026-07-05), `0e47f12f` (refresh, 2026-07-06) on branch `main`
- **Inspection dates**: 2026-07-05 (initial), 2026-07-06 (refresh)
- **Evidence categories**: Source code inspection, runtime execution (parse, write, roundtrip), test execution (2,887 tests run, 39,864 collected), file system analysis, git history review, governance validator counts, schema inspection
- **Runtime verification scope**: FODS (parse + roundtrip), FODT (parse), ZST (compress + decompress + roundtrip), TOML (load). Representative, not exhaustive.
- **Limitations**: Full test suite (39,864 tests) was collected but not run in its entirety during this reconnaissance. .NET compilation was not executed. CI workflows were inspected but not triggered. SAL fact counts are from `.local/sal-output/` consolidation. Sprint count (840+) is from README documentation, not independently verified against report directory count.
