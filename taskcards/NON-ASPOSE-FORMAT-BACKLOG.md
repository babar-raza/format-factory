---
taskcard_id: NON-ASPOSE-FORMAT-BACKLOG
title: "Non-Aspose Format Candidate Backlog"
type: backlog_governance
sprint: FORMAT-FACTORY-ROADMAP-MEMORY-SYNC-001
created_at: "2026-05-14"
status: backlog
visibility: internal
publish_allowed: false
authority: plans/master-plan.md Section 38
---

# Taskcard: NON-ASPOSE-FORMAT-BACKLOG

## Purpose

This taskcard governs the non-Aspose format candidate backlog for Format Factory.
It ensures that candidate formats are properly tracked, audited, and classified
before any acquisition planning begins.

---

## Critical Disclaimer

**All candidates in this backlog are marked `unsupported_by_aspose: needs_audit`.**

This means:
- Aspose support has NOT been verified for these formats
- Some candidates may already be supported by Aspose (partially or fully)
- Every candidate MUST pass a support-matrix audit before acquisition planning
- "Not in this backlog" does not mean "supported by Aspose"

---

## Current Backlog Status

| Category | Count | Audit Status |
|----------|-------|--------------|
| Word processing / text documents | ~18 | needs_audit |
| Spreadsheets | ~15 | needs_audit |
| Presentations | ~8 | needs_audit |
| Archives / compression | ~25 | needs_audit |
| Images / raster / vector / RAW | ~40 | needs_audit |
| CAD / technical drawing / BIM | ~18 | needs_audit |
| 3D / mesh / scene / game assets | ~18 | needs_audit |
| GIS / map / geospatial | ~15 | needs_audit |
| Email / messaging / PIM | ~12 | needs_audit |
| Page layout / publishing / eBook / help | ~20 | needs_audit |
| Project / task / mind-map | ~10 | needs_audit |
| OCR / barcode / document AI adjacent | ~15 | needs_audit |
| Audio/video/container metadata/subtitles | ~20 | needs_audit |
| **TOTAL** | **~234** | **ALL needs_audit** |

Full list: `memory/26-format-expansion-roadmap-and-non-aspose-backlog-20260514.md`

---

## Tier Priorities

### Tier A — Near-Term (After XML/Package Proof Stable)
Priority candidates for first post-FODS/FODT expansion.
Requires Conway R9 complete first.

Examples: .hwpx, .hwp, .hwt, .alz, .egg, .numbers, .key, .pages, .gnumeric, .abw,
.xar, .lha, .arj, .zpaq, .zst, .qoi, .ora, .xcf

### Tier B — Medium-Term (After Archive/Package Workflows Mature)
Examples: .idml, .indd, .qxp, .sla, .wpd, .123, .qpw, .skp, .3dm, .fcstd,
.mbtiles, .pmtiles, .osm, .pbf

### Tier C — Long-Term Advanced/Commercial
Vendor CAD binaries, BIM, camera RAW, proprietary DTP, game/3D scene, email PIM.

---

## Required Steps Before Any Candidate Can Advance

1. **Support-matrix audit** — check current Aspose support status
2. **Spec availability audit** — find public spec, documentation, or open reverse-engineering
3. **Legal classification** — Apache-2.0/MIT samples? Spec license? Reverse-engineering safe?
4. **Local spec normalization** — per AGENTS.md Section T (spec-cache)
5. **Generated requirements** — AI synthesis + schema validation + verifier review + DEC-034 IV
6. **Implementation planning** — taskcards, sprint design, lane assignment
7. **Full 11-gate progression** — human approval at each gate

---

## Governance Rules

1. No candidate advances to acquisition without human authorization.
2. Support-matrix audit must complete and be recorded before acquisition planning.
3. Audit result must be committed to the format registry before any sprint begins.
4. Proprietary formats require legal classification before any work.
5. AI can assist with classification and spec research — cannot be authority.
6. New candidates may be added to this backlog by recording them in:
   - `memory/26-format-expansion-roadmap-and-non-aspose-backlog-20260514.md`
   - `docs/python-foss/format-expansion-roadmap.md` Section 7
   - `docs/python-foss/format-expansion-roadmap.yaml` tier lists

---

## Related Files

| File | Purpose |
|------|---------|
| memory/26-format-expansion-roadmap-and-non-aspose-backlog-20260514.md | Full backlog by category |
| docs/python-foss/format-expansion-roadmap.md | Tier A/B/C candidates with notes |
| docs/python-foss/format-expansion-roadmap.yaml | Machine-readable candidate list |
| plans/master-plan.md Section 38 | Authority |
| taskcards/FORMAT-EXPANSION-ROADMAP.md | Roadmap governance |
| taskcards/PUBLIC-SPEC-FORMAT-EXPANSION.md | Public-spec expansion planning |
| taskcards/NAC-001-non-aspose-format-candidate-registry.md | Registry plan (existing) |
