# Product Portfolio Maturity Matrix
## TC-D1, TC-D2, TC-D3, TC-D4, TC-D5 | Plan Hardening Sprint 2026-06-09

---

## TC-D1: Format Maturity Matrix (From Repo Truth)

### Python FOSS Formats

| Format | Functions | Write | Tests | Authority | Maturity | Track |
|---|---|---|---|---|---|---|
| **ABW** | 29 | write_abw(), create_abw() | 33 files | P1 (no public spec) | DEEP | FOSS |
| **FODS** | 27 | write_fods(), workbook_to_xml() | 37 files | P6 (partial) | DEEP | FOSS+Commercial |
| **FODT** | 21 | write_fodt(), document_to_xml() | 36 files | P4 (1 verified fact) | DEEP | FOSS+Commercial |
| **Gnumeric** | 28 | write_gnumeric(), create_gnumeric() | 29 files | P1 (schema only) | DEEP | FOSS |
| **TSV** | 31 | write_tsv(), append_row(), roundtrip() | 33 files | P1 (no public spec) | DEEP | FOSS |
| **NDJSON** | 32 | write_ndjson(), to_jsonl_str() | 32 files | P1 (no spec needed) | DEEP | FOSS |
| **FODG** | 26 | (no write yet) | 23 files | P1 | DEEP (read) | FOSS |
| **DIF** | 16 | (no write) | 22 files | P1 (no public spec) | MEDIUM | FOSS |
| **SYLK** | 14 | write (partial) | 33 files | P1 (no public spec) | MEDIUM | FOSS |
| **ODS** | 13 | (no write) | 14 files | P1 | MEDIUM | FOSS |
| **ZST** | 6 | compress/decompress | 26 files | P4 (2 verified facts) | MEDIUM | FOSS |
| **CSV** | 11 | (export only) | 12 files | P3 (RFC pending) | MEDIUM | FOSS |
| **PBM** | 10-12 | write_pbm() | 19 files | P1 | SHALLOW+ | FOSS |
| **PGM** | 10-12 | write_pgm() | 13 files | P1 | SHALLOW+ | FOSS |
| **PPM** | 10-12 | write_ppm() | 29 files | P1 | SHALLOW+ | FOSS |
| **ODT** | 8 | (no write) | 5 files | P1 | SHALLOW | FOSS |
| **QOI** | 8 | encode (proto) | 6 files | P1 | SHALLOW | FOSS |
| **XCF** | 6 | (no write) | 4 files | P1 | SHALLOW | FOSS |
| **TOML** | 11 | write_toml() | 4 files | P1 | SHALLOW | FOSS |
| **FODP** | ~5 | (no write) | 2 files | P1 | SKELETON | FOSS |

### .NET Commercial Formats

| Format | LOC | Tests | Operations | Gate 11 | Tier |
|---|---|---|---|---|---|
| **FODS** | 2,179 | 547 | Load/Parse/Edit/Save/Export(CSV/HTML/JSON) | NOT APPROVED | Tier 1+ |
| **FODT** | 2,035 | 145 | Load/Parse/Edit/Save/Export(TXT/MD/HTML/JSON) | NOT APPROVED | Tier 1+ |
| **Netpbm** | ~500 | ~423 | Parse P1-P6, probe | NOT APPROVED | Tier 0 |
| **CSV** | 105 | - | WriteRows, EscapeField | N/A (support library) | N/A |
| **HTML** | - | - | Output generator | N/A (support library) | N/A |
| **Markdown** | - | - | Output generator | N/A (support library) | N/A |
| **TXT** | - | - | Output generator | N/A (support library) | N/A |

---

## TC-D2: Priority Formats for Deepening

### Selection Criteria
1. Has write capability in Python (roundtrip possible)
2. High function count (deep enough to be useful)
3. Strong authority level OR permanent no_public_spec exemption
4. Existing test coverage sufficient to prevent regressions
5. .NET+Python symmetry (bonus for commercial track)

### Recommended Top 3

**1. FODS (Flat OpenDocument Spreadsheet)**
- Rationale: Strongest authority (P6 partial), write exists, .NET+Python dual-track, 547 .NET tests + 37 Python test files, Gate 10 PASSED
- Next action: Complete Python write testing, prepare Gate 11-G packet
- Publication candidate: YES (both tracks)

**2. Gnumeric**
- Rationale: 28 functions, write+create+roundtrip, 29 test files, gzip-compressed XML codec well-tested
- Next action: Add Python roundtrip export tests, prepare package metadata
- Publication candidate: YES (Python FOSS)

**3. ABW (AbiWord)**
- Rationale: 29 functions, 5 export targets (txt/html/csv/json/markdown), write+create, 33 test files
- Next action: Verify roundtrip integrity, add install-test
- Publication candidate: YES (Python FOSS)

### Honorable Mentions
- **TSV:** 31 functions with write+roundtrip, strong candidate but limited commercial interest
- **NDJSON:** 32 functions, most function-rich format, but new/untracked module

---

## TC-D3: Publishable FOSS Criteria

A Python FOSS format package is publishable when ALL of:

| Criterion | Description |
|---|---|
| **Read** | Parse source format into neutral model or structured dict |
| **Write** | Write neutral model back to source format |
| **Export** | Export to at least 1 common format (CSV, JSON, or TXT) |
| **Roundtrip** | Load→Edit→Save→Reload produces consistent output |
| **Roundtrip test** | At least 1 test proving roundtrip integrity |
| **Output test** | At least 5 tests producing real outputs (not import-only) |
| **Install test** | Package installs in clean venv and imports successfully |
| **Package metadata** | pyproject.toml with name, version, author, description, license |
| **Version strategy** | Semantic versioning (0.x.y for pre-release, 1.x.y for stable) |
| **API docs stub** | README or docstrings for public functions |
| **Security** | No eval(), no DTD processing, input size guards |

### Current Status by Priority Format

| Format | Read | Write | Export | Roundtrip | RT Test | Output Tests | Install | Metadata | Version | Docs | Security |
|---|---|---|---|---|---|---|---|---|---|---|---|
| FODS | Y | Y | Y (CSV) | Y | Y | Y (37 files) | LOCAL | PARTIAL | NO | PARTIAL | Y (defusedxml) |
| Gnumeric | Y | Y | Y (CSV) | Y | Y | Y (29 files) | LOCAL | NO | NO | NO | Y |
| ABW | Y | Y | Y (5 fmts) | PARTIAL | PARTIAL | Y (33 files) | LOCAL | NO | NO | NO | Y |

---

## TC-D4: Product-First Sprint Policy

### Proposed Policy

**Constraint:** At least 60% of sprint work items must be of type PRODUCT_SOURCE or TEST.

**Measurement:** Count work items in evidence-declaration.yaml by item_type:
- PRODUCT_SOURCE: source code additions/modifications to src/python/ or src/net/
- TEST: test additions/modifications
- GOVERNANCE_DOC: governance documents, schemas, policies
- INFRASTRUCTURE: supervisor tools, automation, packaging

**Enforcement:** Anti-skip detector should flag sprints where PRODUCT_SOURCE + TEST < 60% of total items.

**Exemptions:** Planning sprints (like this one) and governance closure sprints are exempt but must be explicitly declared.

**Rationale:** Prevents the W10 pattern where governance infrastructure improvement displaces product maturity indefinitely.

---

## TC-D5: Shallow Format Classification

| Format | Classification | Rationale |
|---|---|---|
| **FODP** | PAUSE | 2 test files, skeleton codec, no clear demand, no write capability |
| **QOI** | PAUSE | Prototype encoder only, limited Python ecosystem interest |
| **XCF** | PAUSE | Header-only parser, no layer/channel extraction, limited demand |
| **ODT** | DEEPEN (later) | ODF family member, shares spec with FODT, paragraph-only currently |
| **TOML** | DEFER | stdlib tomllib covers read; limited value-add over existing tools |
| **ODS** | DEEPEN | ODF family member, has CSV exporter, useful format, 14 test files |
| **DIF** | MAINTAIN | Legacy format, 16 functions adequate, 22 test files |
| **CSV** | DEEPEN | Ubiquitous format, RFC 4180 authority pending, 11 functions insufficient |
| **PBM/PGM/PPM** | MAINTAIN | Netpbm family, has write+convert, adequate depth for imaging niche |
