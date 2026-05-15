# ZST Product Strategy Alignment Audit
Sprint: FORMAT-FACTORY-R13B-DELEGATED-ZST-GATE1-REAL-SUPPORT-AUDIT-AND-GOVERNANCE-NORMALIZATION-SWARM-001
Gate: 6 (Lane G)
Date: 2026-05-15

---

## Purpose

Evaluate whether ZST (Zstandard, .zst) is an appropriate candidate for the format-factory acquisition pipeline, given that ZST is a codec/compression format rather than a rich document object model format.

---

## Evidence Reviewed

- docs/format-expansion-roadmap.md
- docs/product-tracks.md
- docs/commercial-product-capability-model.md
- ROADMAP.md
- plans/master-plan.md
- reports/planning/r13-candidate-fallback-and-ranking-preservation-20260515.md (R13 Gate 5)

---

## Question 1: Does the project allow archive/compression/codec formats?

**YES.**

`docs/format-expansion-roadmap.md` explicitly lists ZST in the backlog:

> `| .zst | Compression | Full public | Zstandard — RFC |`

Section 3 (Long-Term Plan) states:

> "The system must not be limited to formats currently supported by Aspose."

The document explicitly includes "Archive/package formats" in the strategic future backlog. ZST is a compression-codec format, which falls within the "Archive/package formats" category.

The R12 candidate scoring model (`acquisition_planning_runtime.py`) already includes `archive` as a valid `category` field, with ZST explicitly classified as `category=archive`.

---

## Question 2: Does the existing candidate ranking intentionally include archive/codec candidates?

**YES.**

The R12 cross-category validation (ranked 8.95 #1) evaluated ZST alongside:
- gnumeric (spreadsheet), abw (word processing), zpaq (archive), qoi (image), ora (image)

The ranking model intentionally includes multiple categories. ZST was the top scorer across all categories, not just within the archive category.

---

## Question 3: Does ZST create product value?

| Use Case | Product Value |
|----------|--------------|
| .zst single-file decompression | HIGH — common in Linux/server environments; log files, data exports, packages |
| .tar.zst archive handling | HIGH — standard Linux package format (Arch Linux, rpm); Aspose confirms TarArchive.SaveZstandard support |
| Round-trip compression/decompression | HIGH — deterministic oracle (SHA-256 round-trip); easiest oracle type in the pipeline |
| Package/container extraction | MEDIUM — .tar.zst used in npm, rpm, package management |
| Fixture/oracle pipeline validation | HIGH — ZST proves the acquisition pipeline works for codec/container formats, not just XML |
| Non-Aspose format acquisition proof | HIGH — Python track uses python-zstandard (BSD-3-Clause); validates FOSS pipeline for non-XML formats |
| Document conversion use case | LOW — ZST is not a document format; no DOM; no cell/paragraph structure to convert |

**Assessment:** ZST's primary value is in decompression/extraction and pipeline validation, not document conversion. This is a deliberate and valid use case for the archive track.

---

## Question 4: Is ZST an appropriate first post-ODF candidate?

**YES, WITH LIMITATIONS.**

Arguments FOR ZST as first post-ODF candidate:
1. Highest score (8.95) in the acquisition-ready band
2. Proves the pipeline can handle archive/codec formats, not just XML document formats
3. Simple oracle model (compress → decompress → compare SHA-256) is ideal for testing the acquisition pipeline
4. IETF RFC + BSD license = cleanest legal path in the Tier A backlog
5. Aspose.ZIP supports ZST fully, validating the Aspose integration model for the .NET track
6. Python FOSS track uses pure python-zstandard (BSD-3-Clause) — no Aspose dependency for FOSS

Arguments AGAINST / Limitations:
1. ZST has no document object model → no "load-edit-save-convert" in the traditional sense
2. The commercial product capability model (docs/commercial-product-capability-model.md) defines commercial readiness as "load-edit-save-convert" for document entities — for ZST, the "entities" are raw byte streams, not cells/paragraphs/slides
3. ZST may have limited commercial product positioning if users expect a format converter (not a compressor/decompressor)

**Conclusion:** ZST fits the acquisition pipeline but requires a clarified commercial value proposition. The `.NET` commercial track use case is decompression/extraction functionality, not document conversion. This is a legitimate use case for an archive library product.

---

## Question 5: Should ORA become the next candidate instead?

**ORA IS THE RECOMMENDED FALLBACK, but ZST remains appropriate as FIRST candidate.**

Reasoning:
- ZST at 8.95 outscores ORA at 8.85
- ZST's archive category is explicitly in scope
- ORA reuses XML pipeline infrastructure (ZIP+XML) which is a secondary advantage, not a reason to skip ZST
- If ZST audit passes, proceed with ZST; ORA becomes R14-equivalent candidate

If ZST had failed the audit: ORA would be the clear next choice. Since the audit passes, ZST proceeds.

---

## Decision Outcome

**PRODUCT_ALIGNMENT_PASS_WITH_LIMITATIONS**

| Factor | Assessment |
|--------|-----------|
| Format in scope | YES — archive category explicitly included |
| Acquisition ranking justifies selection | YES — #1 at 8.95 |
| Aspose support confirmed | YES — Aspose.ZIP full round-trip + .tar.zst |
| Legal path clear | YES — BSD + patent grant |
| Oracle model valid | YES — SHA-256 round-trip (compress → decompress) |
| FOSS Python track | YES — python-zstandard (BSD-3-Clause) |
| Document conversion commercial value | LIMITED — codec/container, not document object model |
| Commercial value clarification required | YES — value is decompression/extraction, not format conversion |

The limitation (no document DOM) is KNOWN and acceptable. ZST provides archive handling value and pipeline validation. The commercial product value is decompression/extraction functionality (API-level), comparable to how Aspose.ZIP itself positions ZST support.

---

## Audit Result

ZST_PRODUCT_STRATEGY_ALIGNMENT: PRODUCT_ALIGNMENT_PASS_WITH_LIMITATIONS
ZST proceeds to Gate 1 execution. Limitation on commercial DOM value noted in product-strategy-notes.md.
ORA (8.85) preserved as next-in-line candidate after ZST.
