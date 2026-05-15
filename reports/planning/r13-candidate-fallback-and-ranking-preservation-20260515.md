# R13 Candidate Fallback and Ranking Preservation
Sprint: FORMAT-FACTORY-R13-ZST-SUPPORT-MATRIX-AUDIT-SIMULATION-AND-GATE1-PACKET-SWARM-001
Lane: F (Candidate Fallback and Ranking Preservation)
Date: 2026-05-15

## SIMULATION ONLY — No Acquisition Authorized — All Rankings Are Planning Estimates

---

## 1. Why ZST Is First

ZST (Zstandard, .zst) ranked #1 with score 8.95 / 10.

| Score Advantage | Explanation |
|---|---|
| spec_availability: 10/10 | IETF RFC 8878 — highest possible spec quality tier |
| legal_clarity: 9/10 | IETF public domain + BSD+patent grant — clear IP path |
| parser_feasibility: 10/10 | OSS reference impl (python-zstandard); public spec complete enough to implement |
| spec_completeness: 9/10 | Single authoritative RFC; complete bitstream spec |
| sample_availability: 8/10 | Any file can be ZST-compressed; constructible samples |
| oracle_feasibility: 7/10 | Round-trip oracle (compress → decompress → SHA256 compare) |
| complexity: 7/10 | Moderate: LZ77+ANS (FSE) + Huffman, but fully documented |
| req_gen_readiness: 9/10 | Full public spec + legal clarity = AI requirements gen ready |

No other format in the backlog combines an IETF RFC, BSD+patent grant, and a fully
documented compression algorithm in the archive/codec category.

---

## 2. Why ORA is Second (Score 8.85)

ORA (OpenRaster, .ora) is the next-highest Tier A candidate.

| Field | Value |
|-------|-------|
| format_id | ora |
| score | 8.85 |
| tier | ACQUISITION_READY |
| spec_type | full_public |
| category | image |
| spec source | freedesktop.org OpenRaster specification |
| legal | Open standard; permissive license |

Score advantage over Gnumeric/ABW (8.75):
- ORA's spec_completeness slightly higher than Gnumeric (format is newer, better-documented)
- Image category complexity (6) lower than archive (7), yielding a slight score lift
- open_source_reference=True (Krita, GIMP, MyPaint all implement ORA)

ORA becomes the natural first alternative if ZST is deferred.

**Strategic note on ORA:** ORA is a ZIP-based XML package (like OOXML/ODF), which means
the acquisition strategy would have strong reuse from the FODS/FODT XML pipeline work.
This is strategically attractive — it leverages existing parser/neutral-model infrastructure.

---

## 3. Gnumeric and ABW as Equally-Ranked Third (Score 8.75)

Both Gnumeric (.gnumeric) and AbiWord (.abw) score 8.75.

| Field | Gnumeric | ABW |
|-------|----------|-----|
| format_id | gnumeric | abw |
| category | spreadsheet | word_processing |
| spec_type | full_public | full_public |
| open_source | YES (GNOME Gnumeric) | YES (AbiWord) |
| oracle | Reference diff against Gnumeric binary | Reference diff against AbiWord binary |

**Tiebreak criteria** (if one must be chosen before the other):
- Gnumeric covers the Cells product family (same as FODS) — higher format-family reuse
- ABW covers the Words product family (same as FODT) — equally valid reuse path
- Decision can be made by human at Gate 1 time based on commercial priority
- Neither may be acquired before Gate 1 approval

---

## 4. ZPAQ (Score 8.70) and QOI (Score 8.60)

| Format | Score | Notes |
|--------|-------|-------|
| zpaq | 8.70 | Archive format; ZPAQ standard; fewer implementations |
| qoi | 8.60 | Image format; QOI spec (GitHub); very simple; non-blocking calibration opportunity |

**QOI calibration note (non-blocking):**
R12 validation noted that QOI's `open_source_reference=True` value could be reconsidered
depending on how the scorer distinguishes "reference implementation available" from
"Aspose-backed". If recalibrated, QOI's score could vary by ±0.1. This does not
affect the ZST/ORA/Gnumeric/ABW rankings above it.

---

## 5. Lower-Ranked Formats (Not Selected)

| Format | Score | Tier | Reason Not Selected |
|--------|-------|------|---------------------|
| egg | 5.55 | CANDIDATE_READY | Partial spec; Korean archive; legal uncertain |
| hwpx | 5.35 | CANDIDATE_READY | Korean document; partial spec; binary complexity |
| xar | 5.15 | CANDIDATE_READY | macOS archive; partial spec; no open samples |
| alz | 3.25 | NEEDS_INVESTIGATION | Reverse engineering required; binary; legal risk |
| hwp | 3.05 | NEEDS_INVESTIGATION | Reverse engineering required; binary; legal risk |

These candidates remain visible but are not selected for the current acquisition queue.
They must NOT be advanced without a validated ranking re-run AND human authorization.

---

## 6. What Evidence Would Change the Ordering

| Event | Effect |
|-------|--------|
| RFC 8878 retrieval finds IP encumbrance | ZST score drops; ORA would become #1 |
| Aspose already supports ZST fully | Acquisition priority recalculated (DEC-033 path shift) |
| ORA real audit reveals spec gaps | ORA score may drop below 8.85 |
| QOI recalibration | QOI ±0.1; no effect on top 4 |
| New IETF RFC in the archive space | Could add new candidate above ZST |
| Commercial strategy shifts to image formats | ORA or QOI prioritization possible |

---

## 7. What Must Not Change Without a Validated Re-Run

The following MUST NOT change unless the acquisition_planning_runtime.py produces a
new validated bundle with human authorization:

1. The ranking order (zst > ora > gnumeric/abw > zpaq > qoi)
2. The ACQUISITION_READY threshold (7.01)
3. The tier definitions (ACQUISITION_READY, CANDIDATE_READY, NEEDS_INVESTIGATION)
4. The score weights (spec_availability 0.20, spec_completeness 0.15, etc.)
5. The unsupported_by_aspose status for any candidate (all remain needs_audit)

---

## 8. How to Avoid Stale Candidate Decisions

Staleness rules:
- Any ranking re-run that changes the top 3 order requires a new planning bundle + IV
- The planning bundle is governed by dry_run_only=True; production use requires explicit human authorization
- Any format where aspose_supported transitions from None to a real value triggers a re-rank
- Candidate rankings expire if the acquisition_planning_runtime.py governance config changes

Current staleness status: CURRENT (ranking last validated R12 Lane C, 2026-05-14)

---

## 9. Fallback Decision Tree (for human use)

```
If Babar approves ZST Gate 1:
  → R13B: ZST real support-matrix audit
  ORA, Gnumeric, ABW remain in queue

If Babar defers ZST:
  → If Babar selects ORA: R13B targets ORA (ZIP+XML pipeline reuse)
  → If Babar selects Gnumeric: R13B targets Gnumeric (Cells family reuse)
  → If Babar selects ABW: R13B targets ABW (Words family reuse)
  → If Babar requests investigation: no acquisition sprint authorized

If ZST Gate 1 approved but support-matrix audit finds Aspose supports it:
  → DEC-033 path: commercial track uses Aspose; OSS track uses python-zstandard
  → Ranking may be recalculated to deprioritize ZST (if commercial value reduced)

If ZST Gate 1 approved but support-matrix audit contradicts legal assumptions:
  → ZST moved to BLOCKED; ORA becomes default next candidate
```

## Verdict
FALLBACK_PATHS_DEFINED: YES
RANKING_PRESERVED: YES
STALE_GUARD_DOCUMENTED: YES
NO_ACQUISITION_AUTHORIZED: CONFIRMED (all formats remain CANDIDATE_ONLY)
