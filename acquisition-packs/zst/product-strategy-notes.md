# ZST Product Strategy Notes
Format: Zstandard (.zst)
Gate: 1
Date: 2026-05-15
Sprint: FORMAT-FACTORY-R13B-DELEGATED-ZST-GATE1-REAL-SUPPORT-AUDIT-AND-GOVERNANCE-NORMALIZATION-SWARM-001

---

## Product Value Proposition

ZST is a codec/compression format, not a rich document object model. The format-factory commercial
product value for ZST is different from document formats (FODS, FODT).

### Commercial .NET Track Value

| Use Case | Product Value |
|----------|--------------|
| .zst decompression | HIGH — API for programmatic decompression of Zstandard files |
| .tar.zst extraction | HIGH — common Linux package/distribution format |
| .zst compression | HIGH — create compressed archives from document output |
| Package/artifact handling | MEDIUM — extract data from .zst-compressed packages |

**Primary commercial value:** Archive handler (compress + decompress), not document format converter.
The commercial .NET implementation will use Aspose.ZIP's ZstandardArchive and TarArchive.SaveZstandard APIs.

### Python FOSS Track Value

| Use Case | Product Value |
|----------|--------------|
| python-zstandard integration | HIGH — pure BSD-3-Clause; no Aspose dependency |
| Oracle/fixture pipeline | HIGH — SHA-256 round-trip is deterministic and automatable |
| Cross-platform compression utility | HIGH — Zstandard is widely used in Linux/data pipelines |

---

## Alignment Assessment

**PRODUCT_ALIGNMENT_PASS_WITH_LIMITATIONS**

The limitation is explicitly noted:
- ZST has no document DOM (no cells, paragraphs, slides)
- Commercial readiness gate (Gate 11) criteria will differ from FODS/FODT
- "load-edit-save-convert" for ZST means: load compressed bytes → decompress → expose content → recompress
- The commercial product is an archive handling API, not a document conversion API for this format

This is an acceptable and consistent use case. Aspose.ZIP itself positions ZST as an archive format, not a document format.

---

## Oracle Strategy

Oracle type: ROUND_TRIP
Implementation: compress file → decompress → compare SHA-256 of original and decompressed
Deterministic: YES (Zstandard decompression is deterministic given same dictionary)
Dependencies: python-zstandard (Python), Aspose.ZIP (C#)

---

## Next Steps (Gates 2+)

| Gate | Action | Authorization Needed |
|------|--------|---------------------|
| Gate 2 | Retrieve RFC 8878 + cache | Separate R14 authorization prompt |
| Gate 3 | Identify sample .zst files | After Gate 2 |
| Gate 4 | Prototype parser/decompressor | After Gate 3 |
| Gate 6 | Oracle comparison | SHA-256 round-trip |
| Gate 11 | Commercial product readiness | After Gate 10; commercial product criteria to be defined for archive track |

---

## Commercial Product Criteria (Future Gate 11 Planning)

For ZST, Gate 11 commercial readiness will require different criteria than FODS/FODT.
Proposed future Gate 11 criteria for archive formats:
1. Decompress .zst to output stream/file
2. Compress input to .zst
3. Extract .tar.zst to directory
4. Create .tar.zst from directory
5. Streaming decompression (progress events)
6. Error handling for corrupted/invalid .zst
7. API documented and tested

**Note:** Gate 11 criteria for archive formats must be formally defined by Babar Raza before Gate 11 work begins. This is a future planning note only.
