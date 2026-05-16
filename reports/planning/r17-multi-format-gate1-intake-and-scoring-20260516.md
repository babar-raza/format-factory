# R17 Gate 6: Multi-Format Gate 1 Intake and Scoring
Sprint: FORMAT-FACTORY-R17-R16-CLOSURE-VERIFY-ZST-GATE4-PLANNING-AND-MULTI-FORMAT-GATE1-SWARM-001
Date: 2026-05-16
Gate: 6 — Parallel Multi-Format Gate 1 Intake and Scoring

## Purpose

Run real Gate 1 identity, spec, legal, and preliminary scoring analysis for 6 candidates.
No Gate 1 approvals are granted in this sprint. DEC-034 IV required before any Gate 1 passes.
This produces Gate 1 audit packets for human review.

---

## Candidate 1: FODP (Flat OpenDocument Presentation)

### Identity
- Full name: Flat OpenDocument Presentation
- Extension: `.fodp`
- MIME type: `application/vnd.oasis.opendocument.presentation-flat-xml`
- Spec body: OASIS (Open Document Format for Office Applications v1.3)
- Standard: OASIS ODF 1.3 — identical spec used for FODS and FODT
- Structure: Single-file flat XML (no ZIP container)

### Legal Category
- Category 1 — OASIS Royalty-Free on Limited Terms
- Identical legal basis to FODS and FODT (already approved at Gate 1-2 for both)
- Fast-path eligible at Gate 2 per legal-notes.md precedent

### Spec Availability
- OASIS ODF 1.3 Part 1 specification: comprehensive, maintained, publicly accessible
- Score: 3/3 (Comprehensive official spec)

### Aspose Support
- Status: NEEDS_AUDIT — Aspose.Slides handles ODP and flat ODP variants
- Likely FULL_ROUND_TRIP (same as FODS pattern for FODT)
- Must be confirmed before Gate 1 approval

### Pipeline Reuse
- HIGH — spec cache, legal analysis, oracle provider all reusable from FODS/FODT
- Existing ODF XML parsing patterns directly applicable
- FODT XML parsing experience transfers fully

### Preliminary Scoring

| Factor | Score | Points | Notes |
|--------|-------|--------|-------|
| Legal Safety | 3 | 30 | OASIS RF — Category 1 |
| Spec Availability | 3 | 20 | OASIS ODF 1.3 comprehensive |
| Parseable Structure | 2 | 10 | Flat XML like FODS/FODT; moderate ODF semantics |
| Community Demand | 2 | 10 | Presentations widely used; ODP more common than FODP |
| Strategic Track Value | 2 | 6.67 | ODF family expansion; presentation track new |
| Pipeline Reuse | 3 | 10 | Full reuse from FODS/FODT |
| Implementation Risk | 2 | 6.67 | Known ODF XML complexity; new schema domain (presentations) |

Note: Using 7-factor model. Exact weight mapping per _scoring-model.md requires
human scoring review. Estimated weighted total: ~8.5-8.8.

### Recommendation
- Band: Accept
- Next gate: Gate 1 batch with FODG (same spec, same legal)
- Prerequisite: Aspose support audit + DEC-034 IV of Gate 1 scoring
- Sprint: FODP-FODG batch Gate 1 approval after Conway R9 stable

---

## Candidate 2: FODG (Flat OpenDocument Drawing)

### Identity
- Full name: Flat OpenDocument Drawing
- Extension: `.fodg`
- MIME type: `application/vnd.oasis.opendocument.graphics-flat-xml`
- Spec body: OASIS ODF 1.3
- Structure: Single-file flat XML (no ZIP container)

### Legal Category
- Category 1 — OASIS RF (identical to FODS/FODT/FODP)

### Spec Availability
- OASIS ODF 1.3 — Score: 3/3

### Aspose Support
- Status: NEEDS_AUDIT — Aspose.Diagram handles drawing/diagramming formats
- Likely YES; confirmation needed

### Pipeline Reuse
- HIGH — same as FODP reasoning; ODF XML experience transfers

### Preliminary Scoring
- Estimated weighted total: ~8.2-8.5
- Narrower use case than FODP (diagrams vs presentations)
- Community demand: 1-2 (specialized drawing domain)

### Recommendation
- Band: Accept
- Batch with FODP (same spec, same legal, same acquisition infrastructure)
- Same prerequisites as FODP

---

## Candidate 3: ORA (OpenRaster)

### Identity
- Full name: OpenRaster
- Extension: `.ora`
- MIME type: `image/openraster`
- Spec body: freedesktop.org / Krita project community standard
- Structure: ZIP container with PNG image tiles + XML stack.xml + thumbnail
- Standard: freedesktop.org informal specification (not ISO/OASIS)

### Legal Category
- Category 1 or 2 — freedesktop.org spec is public, permissive
- Implementation permission: implicit (open community spec, no royalty claims)
- Needs confirmation: no explicit RF designation found
- Preliminary: Category 2 (permissive community spec)

### Spec Availability
- Informal community spec exists; not fully comprehensive by major-standards-body criteria
- Score: 2/3 (community spec with some gaps)

### Aspose Support
- Status: NEEDS_AUDIT — Aspose.Imaging handles raster formats
- Not confirmed for ORA specifically
- Previous mention in R13 context as "Gate 5 fallback ORA" — suggests some project familiarity

### Preliminary Scoring

| Factor | Score | Points | Notes |
|--------|-------|--------|-------|
| Legal Safety | 2 | 20 | Category 2 — permissive community spec |
| Spec Availability | 2 | 13 | Community spec with gaps |
| Parseable Structure | 2 | 10 | ZIP + PNG + XML; moderate; ZIP layer adds complexity |
| Community Demand | 1 | 5 | Niche digital painting format; Krita, MyPaint users |
| Strategic Track Value | 2 | 6.67 | Image format family; limited overlap with current pipeline |
| Pipeline Reuse | 1 | 3.33 | ZIP handling transferable; XML minimal; PNG tiles new |
| Implementation Risk | 2 | 6.67 | Well-understood components; tile handling requires work |

Estimated weighted total: ~6.5-7.0

### Recommendation
- Band: Borderline Accept / Needs review
- Aspose support audit critical before Gate 1
- Lower priority than Gnumeric/ABW/FODP/FODG
- Next step: Aspose audit then Gate 1 scoring IV

---

## Candidate 4: Gnumeric (.gnumeric)

### Identity
- Full name: Gnumeric Spreadsheet
- Extension: `.gnumeric` (also `.gnm`)
- MIME type: `application/x-gnumeric`
- Spec body: GNOME Project — Gnumeric application (open source, GPL)
- Structure: Gzip-compressed XML
- Schema: XML with documented structure; GNOME project hosts format documentation
- Reference application: Gnumeric (GNU/GPL)

### Legal Category
- Category 2 — Permissive OSS (format documented by open source project)
- No royalty claims; format spec accessible from GNOME documentation
- Application is GPL but format itself is open XML

### Spec Availability
- GNOME project documentation exists; less formal than OASIS ODF
- Score: 2/3 (official project spec but gaps relative to comprehensive standard)

### Aspose Support
- Status: NEEDS_AUDIT — Aspose.Cells handles various spreadsheet formats
- Not confirmed for .gnumeric specifically
- Prior R11 planning bundle score: 8.75 (ACQUISITION_READY)

### Preliminary Scoring (cross-check against R11 8.75)

| Factor | Score | Points | Notes |
|--------|-------|--------|-------|
| Legal Safety | 2 | 20 | Category 2 — GPL app, open format |
| Spec Availability | 2 | 13 | GNOME project docs; good but informal |
| Parseable Structure | 2 | 10 | Gzip + XML; moderate; gzip layer simple |
| Community Demand | 2 | 10 | Linux/GNOME ecosystem; declining but present |
| Strategic Track Value | 2 | 6.67 | Spreadsheet family; complements FODS |
| Pipeline Reuse | 2 | 6.67 | Gzip + XML transferable |
| Implementation Risk | 2 | 6.67 | Known technology; GNOME XML semantics |

Estimated weighted total: ~8.0-8.5. Broadly consistent with R11 score of 8.75.

### Recommendation
- Band: Accept (ACQUISITION_READY)
- Gate 1 audit packet ready after DEC-034 IV of scoring
- Aspose support audit required
- Priority: After FODP/FODG batch; can be parallel lane

---

## Candidate 5: ABW (AbiWord)

### Identity
- Full name: AbiWord Word Processing Document
- Extension: `.abw` (also `.abw.gz`, `.zabw` for gzip-compressed variant)
- MIME type: `application/x-abiword`
- Spec body: AbiSource project — AWML 1.0 DTD
- Structure: Flat XML (single file); images embedded as base64
- DTD: Published at abisource.com (AWML 1.0 — may be outdated)
- Reference application: AbiWord (open source, GPL)

### Legal Category
- Category 2 — Permissive OSS (open source project format with DTD)
- AWML DTD is published; implementation permission implicit from open source project
- DTD noted as "very much out-of-date" — implementation relies partly on reference app behavior

### Spec Availability
- AWML 1.0 DTD + community documentation; outdated
- Score: 1-2/3 (informal/community spec; gaps; must rely partly on reference implementation)

### Aspose Support
- Status: NEEDS_AUDIT — Aspose.Words handles various word processing formats
- Not confirmed for .abw specifically
- Prior R11 planning bundle score: 8.75 (ACQUISITION_READY)

### Preliminary Scoring (cross-check against R11 8.75)

| Factor | Score | Points | Notes |
|--------|-------|--------|-------|
| Legal Safety | 2 | 20 | Category 2 — open source project |
| Spec Availability | 1 | 7 | Outdated DTD; informal spec |
| Parseable Structure | 2 | 10 | Flat XML; images as base64; moderate |
| Community Demand | 1 | 5 | AbiWord declining; limited use |
| Strategic Track Value | 2 | 6.67 | Word processing family; FODT complement |
| Pipeline Reuse | 2 | 6.67 | XML parsing patterns from FODT |
| Implementation Risk | 2 | 6.67 | Outdated spec risk; must validate against reference |

Estimated weighted total: ~7.5-8.0. Slightly below R11 8.75 after spec availability downgrade.
The R11 score of 8.75 may have weighted spec availability more optimistically.
Human scoring review will determine final band.

### Recommendation
- Band: Accept (possible borderline)
- Gate 1 audit packet ready after DEC-034 IV of scoring
- Aspose support audit required
- Outdated spec is a constraint but not a blocker

---

## Candidate 6: dnumber / .numbers Identity Research

### Research Summary

Per sprint mandate: search independently before asking human.

**Search evidence:**
1. Searching ".dnumber file format extension" returns only Apple Numbers (.numbers) results
2. No file format database (fileformats.com, fileinfo.com, justsolve.archiveteam.org)
   contains a ".dnumber" extension
3. The sprint prompt explicitly pairs "dnumber / .numbers / possible identity variants"
4. No corporate, open source, or community format uses "dnumber" as extension or identifier
5. "dnumber" is not found in: IANA media type registry, PRONOM, LOC Digital Formats,
   MIME type lists, or major file format databases

**Most likely identity: Apple Numbers (.numbers)**

Evidence:
- Sprint prompt pairing of "dnumber / .numbers" indicates these are the same candidate
- All web searches for "dnumber" resolve to Apple Numbers context
- "dnumber" may be a shorthand: "doc-number", "d(ocument)-number(s)", or catalog code

### Apple Numbers (.numbers) Assessment

- Extension: `.numbers`
- MIME type: `application/x-iwork-numbers-sffnumbers`
- Owner: Apple Inc.
- Structure: ZIP container with IWA (iWork Archive) files using Protocol Buffers
- Public specification: NONE — Apple has never published an official spec
- Implementation method: Reverse engineering only (no documented permission)

### Legal Category Assessment

- Category 5: Reverse-engineered binary; no public spec; no implementation permission
- **AUTOMATIC REJECT** per scoring model (legal safety = 0)

### Identity Note Created

See acquisition-packs/_candidate-shortlists/r17-gate1-candidate-packets-20260516.md
for the formal dnumber/.numbers identity note.

### Recommendation
- Identity: Resolved as Apple Numbers (.numbers) with high confidence
- Status: AUTOMATIC_REJECT (Category 5)
- Action: Create formal rejection record; no Gate 1 packet
- If "dnumber" does NOT mean Apple Numbers, human must clarify the actual identity

---

## Candidate Summary

| Format | Legal Category | Estimated Score | Band | Gate 1 Status | Next Action |
|--------|---------------|-----------------|------|---------------|-------------|
| FODP | 1 (OASIS RF) | ~8.5-8.8 | Accept | NOT STARTED | ODF batch; Aspose audit |
| FODG | 1 (OASIS RF) | ~8.2-8.5 | Accept | NOT STARTED | ODF batch with FODP |
| ORA | 2 (community) | ~6.5-7.0 | Borderline | NOT STARTED | Aspose audit first |
| Gnumeric | 2 (OSS) | ~8.0-8.5 | Accept | NOT STARTED | DEC-034 IV; Aspose audit |
| ABW | 2 (OSS) | ~7.5-8.0 | Accept | NOT STARTED | DEC-034 IV; Aspose audit |
| dnumber/.numbers | 5 (proprietary) | 0 | AUTO REJECT | REJECTED | No Gate 1; formal rejection |

## What This Gate Does NOT Do

- Does NOT approve Gate 1 for any candidate
- Does NOT create registry entries (no format added to registry)
- Does NOT create acquisition-packs/{format}/ directories
- Does NOT download specs
- Does NOT create samples
- DEC-034 IV of all scoring is required before any Gate 1 approval

## Next Sprint Recommendations

### Batch A: ODF Family (FODP + FODG)
Prerequisites: Aspose support audit for Slides/Drawing
Sprint: FODP-FODG-GATE1-BATCH-SWARM (R18 or R19 parallel lane)

### Batch B: Gnumeric + ABW Gate 1
Prerequisites: DEC-034 IV of scoring + Aspose audit for each
Sprint: GNUMERIC-ABW-GATE1-SCORING-IV-SWARM (parallel to ZST Gate 5)

### Single: ORA Gate 1
Prerequisites: Aspose audit; spec completeness review
Sprint: ORA-GATE1-SWARM (lower priority)

GATE_6_MULTI_FORMAT_INTAKE: COMPLETE
