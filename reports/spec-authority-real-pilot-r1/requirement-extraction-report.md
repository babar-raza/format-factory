# Requirement Extraction Report — SAL Real Pilot R1
Sprint: FORMAT-FACTORY-SPECIFICATION-AUTHORITY-LAYER-REAL-PILOT-R1-001
Lane: D

---

## Extraction Summary

Total candidate requirements extracted: **46**
Extraction method: RFC-2119 keyword scan (MUST, SHALL, SHOULD, MAY, REQUIRED, OPTIONAL, supports, requires)

| Source | Format | Requirements | Verified | Unverifiable | Rejected |
|---|---|---|---|---|---|
| src-zst-rfc8878 | zst | 17 | 17 | 0 | 0 |
| src-netpbm-docs | netpbm | 13 | 13 | 0 | 0 |
| src-dif-softarts | dif | 8 | 8 | 0 | 0 |
| src-fods-oasis | fods (stretch) | 8 | 8 | 0 | 0 |
| **TOTAL** | | **46** | **46** | **0** | **0** |

---

## Authority Classification by Source

### ZST (src-zst-rfc8878) — ACCEPTED_SPEC (with fetch caveat)
- Source type: rfc (IETF RFC 8878)
- 17 requirements extracted from 6 sections
- Representative requirements:
  - "Files MUST begin with a magic number of 0xFD2FB528 stored in little-endian byte order." (MUST, frame-format)
  - "The Frame Header MUST include the FHD (Frame Header Descriptor) byte." (MUST, frame-format)
  - "A block MUST be one of: Raw_Block, RLE_Block, Compressed_Block, or Reserved." (MUST, block-types)
  - "A decoder MUST reject a frame containing a Reserved block type." (MUST, block-types)
  - "When present, it SHALL be a 4-byte xxHash32 checksum of the decompressed content." (SHALL, checksums)
- Authority status: **ACCEPTED_SPEC** (fixture represents normative RFC content; real fetch deferred)
- No overclaiming — fixture caveat documented

### Netpbm (src-netpbm-docs) — ACCEPTED_WITH_CAVEAT
- Source type: public_domain_spec (de facto)
- 13 requirements extracted from 5 sections
- Representative requirements:
  - "PBM files MUST start with a magic number: P1 for ASCII, P4 for binary format." (MUST, pbm)
  - "Maxval MUST be in the range 1 to 65535 inclusive." (MUST, pgm)
  - "Binary PPM (P6) stores pixel values in big-endian byte order when maxval exceeds 255." (stores, ppm)
- Authority status: **ACCEPTED_WITH_CAVEAT** (de facto standard; no formal ISO/IETF standard)
- Family split: PBM/PGM/PPM requirements are identifiable by section heading

### DIF (src-dif-softarts) — EMPIRICAL_ONLY
- Source type: empirical_observation
- 8 requirements extracted from 5 sections
- Representative requirements:
  - "The DIF file MUST begin with the TABLE identifier." (MUST, header)
  - "String values MUST be enclosed in double quotes." (MUST, data-blocks)
  - "The ENDOFDATA keyword SHALL terminate the file." (SHALL, data-blocks)
- Authority status: **EMPIRICAL_ONLY** (historical document; no current standards body)
- DIF ambiguity visible — authority_status is clearly not ACCEPTED_SPEC

### FODS/FODT (src-fods-oasis) — ACCEPTED_WITH_CAVEAT (partial scope, stretch)
- Source type: odf_standard
- 8 requirements extracted from 5 sections (structural only)
- Authority status: **ACCEPTED_WITH_CAVEAT** (scoped summary only; not full ODF 1.3 compliance)
- Noted: Full ODF 1.3 extraction would yield hundreds of requirements

---

## Requirement Graph Results

| Source | Nodes | Edges | Graph Path |
|---|---|---|---|
| src-zst-rfc8878 | 18 | 17 | `.../src-zst-rfc8878-req-graph.json` |
| src-netpbm-docs | 14 | 13 | `.../src-netpbm-docs-req-graph.json` |
| src-dif-softarts | 9 | 8 | `.../src-dif-softarts-req-graph.json` |
| src-fods-oasis | 9 | 8 | `.../src-fods-oasis-req-graph.json` |

Graph structure: 1 SpecSource node + N SpecRequirementRef nodes + N sourced_from edges per source.

---

## Anti-Bypass Verification

All 46 requirements:
- Have valid `source_id` (no memory-only requirements)
- Source IDs are in the registered source list
- Text fragments found in normalized artifact sections (VERIFIED status for all 46)
- No `raw_ai_summary_only` flag set

**Anti-bypass: PASS for all 46 requirements.**
