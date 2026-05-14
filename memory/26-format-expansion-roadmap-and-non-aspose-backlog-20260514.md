---
memory_file: 26-format-expansion-roadmap-and-non-aspose-backlog-20260514.md
sprint: FORMAT-FACTORY-ROADMAP-MEMORY-SYNC-001
date: "2026-05-14"
visibility: internal
publish_allowed: false
---

# 26 — Format Expansion Roadmap and Non-Aspose Backlog (2026-05-14)

## Sprint
FORMAT-FACTORY-ROADMAP-MEMORY-SYNC-001 (2026-05-14)

---

## Purpose

This memory file records the strategic format expansion direction, immediate/short-term/long-term roadmap,
and the non-Aspose candidate backlog as directed by Babar Raza in the 2026-05-14 roadmap memory sync session.

---

## Strategic Direction Summary

Format Factory is the **top-priority project**. Speed is required — but never by skipping:
- Evidence review and bundle validation
- Governance and authority-chain checks
- Taskcards and gate discipline
- Tests, source inspection, and independent verification (DEC-034)
- No-stash/reset/restore/clean safety
- No push/publish safety
- No commercial-readiness overclaim

Preferred execution style: **broader controlled swarm** — more agents, more parallel lanes, bigger sprints,
dependency-aware, coordinator integration, exact-path staging, lane ownership, no uncontrolled overlap.

Human/orchestrator review is delegated to the agent **except for non-delegable actions**:
- push, publish, package release
- external credential use
- Gate 11 approval
- commercial_product_ready = true

---

## Immediate Plan (XML-Based Proof First)

1. Finish the XML-based proof system cleanly on FODS/FODT.
2. Prove the system works perfectly on active XML-style formats.
3. Keep FODS/FODT as current proof formats — do not add new formats until proof is stable.
4. Preserve generated requirements as authoritative only after verifier review + DEC-034 IV.
5. Continue Conway orchestration infrastructure:
   - Prompt generator (Phase R4)
   - Prompt quality gate (Phase R4)
   - Evidence contract integration (Phase R5)
   - Dry-run orchestration (Phase R7)
   - Command architecture (Phase R6)
   - Deterministic replay (Phase R7 dry-runs)
   - Safe planning automation
6. Do not move to autonomous implementation execution until the planning/dry-run orchestration layer is proven.

Conway phase dependency chain:
```
R0 (COMPLETE) → R1 (schemas) → R2 (context resolver) → R3 (lane library)
  → R4 (prompt generator + quality gate) → R5 (evidence contract template)
  → R6 (commands) → R7 (dry-runs) → R8 (IV) → R9 (first new format)
```

---

## Short-Term Plan (After XML Proof Stable)

1. Expand to additional XML/package-based or public-spec formats.
2. Prefer formats with:
   - Public specifications
   - Public structural knowledge
   - Open test material
   - Reverse-engineering-safe documentation
3. Continue to build repeatable skills/playbooks so new formats require minimal custom engineering.
4. Support both:
   - Deterministic/manual-repeatable process through skills
   - Governed autonomous process using llm.professionalize.com models
5. AI is acceleration layer, not authority.
6. Every format must pass the full 10-step pipeline:
   - Support-matrix audit
   - Specification/source audit
   - Legal/provenance classification
   - Local spec normalization
   - Generated requirements (AI + schema validation + verifier review + DEC-034 IV)
   - Implementation planning
   - Evidence bundle validation
   - Tests PASS
   - Gate approvals (human, all 11 gates)
   - Evidence bundle validation

---

## Long-Term Plan (Beyond XML-Family)

Once XML-based formats are proven, enhance the system for many other format families where
specifications or sufficient public technical information are available — regardless of original
source or vendor ecosystem.

**The system must not be limited to formats currently supported by Aspose.**

---

## Format Expansion Priorities

### Tier A — Near-term (after XML/package proof stable)
Strong fit for the current system architecture.

| Format | Category | Notes |
|--------|----------|-------|
| .hwpx | Word processing (XML/package) | Hancom Hangul XML package format |
| .hwp | Word processing (binary) | Hancom Hangul binary |
| .hwt | Word processing (template) | Hancom Hangul template |
| .alz | Archive/compression | ALZip archive |
| .egg | Archive/compression | ESTsoft EGG archive |
| .numbers | Spreadsheet | Apple Numbers |
| .key | Presentation | Apple Keynote |
| .pages | Word processing | Apple Pages |
| .gnumeric | Spreadsheet | Gnumeric (XML-based) |
| .abw | Word processing | AbiWord (XML-based) |
| .xar | Archive/compression | XAR archive |
| .lha / .lzh | Archive/compression | LHA/LZH archive |
| .arj | Archive/compression | ARJ archive |
| .zpaq | Archive/compression | ZPAQ archive |
| .zst | Archive/compression | Zstandard compression |
| .qoi | Image | Quite OK Image (simple, public spec) |
| .ora | Image | OpenRaster (ZIP-based XML) |
| .xcf | Image | GIMP native (public spec) |

### Tier B — Medium-term (after archive/package workflows mature)
Useful after the Tier A expansion stabilizes.

| Format | Category | Notes |
|--------|----------|-------|
| .indd | Page layout | InDesign (via IDML) |
| .idml | Page layout | InDesign Markup Language (XML) |
| .qxp / .qxd | Page layout | QuarkXPress |
| .sla | Page layout | Scribus (XML-based, FOSS) |
| .wpd | Word processing | WordPerfect |
| .123 | Spreadsheet | Lotus 1-2-3 |
| .qpw | Spreadsheet | Quattro Pro |
| .skp | CAD | SketchUp |
| .3dm | CAD | Rhino |
| .fcstd | CAD | FreeCAD (XML ZIP) |
| .mbtiles | GIS | MBTiles (SQLite-based) |
| .pmtiles | GIS | PMTiles (cloud-optimized) |
| .osm | GIS | OpenStreetMap XML |
| .pbf | GIS | Protobuf binary |

### Tier C — Long-term/advanced commercial targets
Future advanced or commercial-only targets after Tier A/B maturity.

- Vendor CAD binaries (SolidWorks, CATIA, Inventor)
- BIM formats (RVT, IFC)
- Camera RAW families (CR3, RAF, ORF, etc.)
- Proprietary DTP formats (InDesign binary, QuarkXPress binary)
- Game/3D scene formats (GLTF, USD, FBX)
- Email PIM formats (NSF, OLM)
- Advanced geospatial (RVT, SHP variants)

---

## Candidate Format Universe (Full Backlog)

**CRITICAL DISCLAIMER:** All candidates below are marked `unsupported_by_aspose: needs_audit`.
Every candidate must pass a support-matrix audit before acquisition planning begins.
Public-spec availability must be recorded before implementation.
Proprietary or reverse-engineered formats must be carefully classified.

### Category 1 — Word Processing / Text Documents
- .hwp, .hwpx, .hwt — Hancom Hangul family
- .pages — Apple Pages
- .abw — AbiWord
- .zabw — compressed AbiWord
- .lwp — Lotus Word Pro
- .wri — Windows Write
- .wpd — WordPerfect
- .wpg — WordPerfect graphics
- .sam — Ami Pro
- .sdw, .sgl, .sxw, .stw — legacy StarOffice/OpenOffice
- .602 — T602 document
- .pwi — Pocket Word
- .jtd, .jtt — Ichitaro

### Category 2 — Spreadsheets
- .numbers — Apple Numbers
- .gnumeric — Gnumeric
- .123, .wk1, .wk3, .wk4, .wks — Lotus 1-2-3 family
- .qpw — Quattro Pro
- .aws, .ab2, .ab3 — Ability Spreadsheet
- .sdc, .sxc, .stc — StarOffice/OpenOffice Calc
- .pmvx, .pmdx — SoftMaker PlanMaker
- .cell — Hancom spreadsheet

### Category 3 — Presentations
- .key — Apple Keynote
- .shw — Corel Presentations
- .prz — Lotus Freelance
- .sda, .sdd, .sdp, .sxi, .sti — StarOffice/OpenOffice Impress
- .hpt — Hancom presentation

### Category 4 — Archives / Compression
- .alz — ALZip archive
- .egg — ESTsoft EGG archive
- .ace, .arc, .arj, .lha, .lzh, .sit, .sitx
- .xar, .zoo, .sqx, .zpaq, .pea, .bh, .gca
- .pak, .paq8, .lpaq
- .zst, .br, .lz4, .lzo, .lzma, .rzip
- .shar, .warc, .cpio, .rpm, .deb, .pkg

### Category 5 — Images / Raster / Vector / RAW
- .xcf — GIMP
- .kra — Krita
- .ora — OpenRaster
- .afphoto — Affinity Photo
- .clip — Clip Studio Paint
- .sai, .sai2 — SAI
- .cpt — Corel PHOTO-PAINT
- .qoi — Quite OK Image
- .farbfeld
- .jxl — JPEG XL
- .bpg, .flif
- .heif, .heic, .avif
- .dds, .ktx, .ktx2, .basis
- .icns, .ani, .cur, .iff, .lbm, .pcx, .sgi, .rgb, .sun, .ras, .xpm, .xbm
- RAW camera: .cr3, .raf, .orf, .rw2, .pef, .srw, .x3f, .erf, .mrw, .mos, .fff

### Category 6 — CAD / Technical Drawing / BIM
- .skp — SketchUp
- .3dm — Rhino
- .fcstd — FreeCAD
- .blend — Blender
- .sldprt, .sldasm, .slddrw — SolidWorks
- .prt, .asm, .catpart, .catproduct, .catdrawing — PTC/CATIA
- .iam, .ipt, .idw — Inventor
- .pln — ArchiCAD
- .rvt, .rfa — Revit/BIM
- .ifcxml, .stepzip, .easm, .edrw, .eprt

### Category 7 — 3D / Mesh / Scene / Game Assets
- .gltf, .glb, .usd, .usda, .usdc, .usdz
- .fbx, .dae, .ply, .stl, .3mf, .x3d, .wrl
- .md2, .md3, .md5mesh, .iqm, .vox
- .bvh, .pmx, .pmd, .mqo

### Category 8 — GIS / Map / Geospatial
- .mbtiles, .pmtiles
- .osm, .pbf
- .gpkg, .kml, .kmz, .gpx, .fit, .tcx
- .e00, .mif, .mid, .tab, .adf, .img, .hgt
- .las, .laz

### Category 9 — Email / Messaging / PIM
- .mbox, .maildir, .dbx, .nsf, .emlx, .olm
- .tnef, .dat, .ics, .vcs, .contact, .wab, .abbu

### Category 10 — Page Layout / Publishing / eBook / Help
- .indd, .idml, .qxp, .qxd
- .sla, .pub, .fm, .mif
- .chm, .lit, .azw, .azw3, .kfx
- .fb2, .djvu
- .cbr, .cbz, .cb7, .cba
- .xps, .oxps

### Category 11 — Project / Task / Mind-Map
- .mpp, .xer, .gan, .mpx, .planner
- .mm, .xmind, .mind, .mmap

### Category 12 — OCR / Barcode / Document AI Adjacent
- .box, .hocr, .alto, .PAGE.xml, .abbyy, .djvu.xml
- .pbm, .pgm, .pnm
- .btw, .lbl, .zpl, .epl, .ipl

### Category 13 — Audio/Video/Container Metadata and Subtitles
- .mkv, .webm, .flv, .ogg, .ogv, .oga
- .m4a, .m4v, .ape, .wv, .tta
- .cue, .m3u, .pls
- .srt, .ass, .ssa, .vtt
- .mxf, .braw, .r3d

---

## Governance Rules for New Format Candidates

1. Every candidate is marked `unsupported_by_aspose: needs_audit` until verified.
2. Support-matrix audit must complete before acquisition planning.
3. Public-spec availability must be recorded before implementation.
4. Proprietary/reverse-engineered formats must be legally classified.
5. AI can assist with discovery, classification, requirements extraction, planning, and implementation
   drafting — but authority comes from specs, evidence, validation, verifier review, DEC-034 IV,
   taskcards, and delegated gate decisions.
6. Speed is required, but not at the expense of governance, correctness, evidence, or safety.
7. Every new format must complete all 11 gates with human approval at each gate.

---

## Key Files for Format Expansion

| File | Purpose |
|------|---------|
| docs/format-expansion-roadmap.md | Full format expansion roadmap (human-readable) |
| docs/format-expansion-roadmap.yaml | Machine-readable format expansion roadmap |
| taskcards/FORMAT-EXPANSION-ROADMAP.md | Roadmap governance taskcard |
| taskcards/NON-ASPOSE-FORMAT-BACKLOG.md | Non-Aspose candidate backlog taskcard |
| taskcards/PUBLIC-SPEC-FORMAT-EXPANSION.md | Public-spec expansion taskcard |
| registry/non-aspose-format-candidates.yaml | Future: candidate registry (NAC-001 taskcard) |

---

## Authority Note

This memory file records strategic direction only. No acquisition, no implementation, no Gate 11 approval,
no commercial readiness claim is made or authorized by this file.
All format expansion work requires explicit human authorization and must follow the full 11-gate pipeline.

**Next agent checklist:**
- [ ] Read plans/master-plan.md Section 38 (format expansion roadmap)
- [ ] Read docs/format-expansion-roadmap.md for full roadmap
- [ ] Check taskcards/FORMAT-EXPANSION-ROADMAP.md for status
- [ ] Check taskcards/NON-ASPOSE-FORMAT-BACKLOG.md for backlog status
- [ ] Confirm Conway Phase R1-R9 completion before adding new formats
- [ ] Confirm XML/package-style proof complete before expanding to new format families
