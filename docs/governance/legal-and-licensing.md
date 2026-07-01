# Legal and Licensing Policy

**Document type:** Policy — Phase 0 Foundation
**Last reviewed:** 2026-05-04 (run014: global audit — content verified consistent with current governance)
**Authority:** This document governs the legal classification of all format specifications and the licensing of all produced artifacts.

---

## Purpose

The format-factory project builds legal parsers, converters, importers, exporters, validators, and compatibility tools. It never engages in unauthorized binary reverse engineering, bypasses access controls, or violates intellectual property rights. This document defines the legal framework that governs which formats may be worked on, what constitutes acceptable evidence, and what licenses govern project outputs.

**This document must be read and applied at Gate 2 (Evidence Complete) for every format.** No format may enter the acquisition pipeline without a confirmed legal category.

---

## Six Legal Categories

Every format candidate must be assigned one of the following six legal categories. The category determines whether the format is eligible for Gate 1 acceptance and what level of legal review is required at Gate 2.

### Category 1: Open Standard (Royalty-Free)

**Definition:** Published by a recognized standards body (OASIS, W3C, ISO, ECMA, IEEE, IETF) under royalty-free (RF) terms. No known patent encumbrances that restrict parser implementation. Multiple independent open-source implementations exist without legal challenge.

**Gate 1:** Eligible. Score positively on the legal safety dimension.
**Gate 2:** Fast-path approval available (see Fast-Path Rules below).
**Examples:** ODF (OASIS), SVG (W3C), OOXML (ECMA 376), HTML (W3C), CSV (IETF RFC 4180), JSON (IETF RFC 8259).

### Category 2: Permissive Open-Source Implementation

**Definition:** No formal specification exists, but a reference implementation is published under a permissive open-source license (Apache 2.0, MIT, BSD, or equivalent). The format behavior is inferred from the reference implementation's source code and documentation. Risk: the spec is implementation-defined and may change without notice.

**Gate 1:** Eligible, with a note that the format carries higher spec-drift risk.
**Gate 2:** Full Gate 2 review required. The Gate 2 review must document the reference implementation version, license, and the risk of format behavior changes.
**Examples:** Many text-based utility formats with a single reference implementation and permissive license.

### Category 3: Published Proprietary Spec with Parser Permission

**Definition:** The specification is proprietary but has been explicitly published by the rights holder with permission to implement parsers and converters. The permission may be explicit (e.g., Microsoft's Open Specifications program under the Microsoft Community Promise, MCPP) or implicit through a published document with no prohibition on implementation.

**Gate 1:** Eligible, with a reduced score on the legal safety dimension reflecting the proprietary nature.
**Gate 2:** Full Gate 2 review required. The review must cite the exact publication, version, and the specific permission grant. Legal notes must be signed off by the project lead or legal reviewer.
**Examples:** Certain legacy Microsoft format specifications published under MCPP.

### Category 4: Ambiguous Public Documentation

**Definition:** Documentation exists in the public domain (blog posts, community wikis, third-party analyses, forum posts) but no formal specification has been published and no explicit parser permission exists. The legal status of implementing a parser based solely on this documentation is unclear and carries meaningful risk.

**Gate 1:** Eligible, but scores 0 on legal safety (score 0 on any single dimension triggers further scrutiny; full score 0 on legal safety triggers automatic reject — see scoring model). Typically results in a score in the "defer" band.
**Gate 2:** Full Gate 2 review required, plus explicit identification of the specific public documentation relied upon, any patent searches performed, and a written risk assessment. Sign-off by project lead acting as legal reviewer.
**Note:** This category is rarely appropriate for early-phase formats. Defer these formats until the project has legal review capacity.

### Category 5: Reverse-Engineered Binary with No Public Permission

**Definition:** No published specification exists. The format can only be understood by analyzing binary files without any publicly available permission to do so. Implementing a parser based solely on binary reverse engineering without a spec or permission may violate DMCA Section 1201 (anti-circumvention), trade secret law, or patent rights.

**Gate 1:** **Automatic reject.** Score 0 on legal safety = automatic reject regardless of total score.
**Gate 2:** Not applicable.
**Note:** If a format that was previously in Category 5 later has a spec published by the rights holder, it may be reconsidered as Category 3.

### Category 6: Blocked

**Definition:** Explicitly known to be under active patent enforcement by the rights holder, or the rights holder has explicitly prohibited reverse engineering or parser implementation. Includes formats where pursuing implementation would expose the project to litigation risk that is not acceptable.

**Gate 1:** **Automatic reject at all gates.** Must not be entered in the registry with any status other than `rejected`.
**Gate 2:** Not applicable.
**Note:** A blocked format must have a note in the registry documenting why it is blocked.

---

## Fast-Path Approval Rules (Gate 2)

For formats in Category 1 (Open Standard, Royalty-Free), Gate 2 legal review may follow a fast-path process. The fast-path allows the project lead to self-approve with a documented rationale, without engaging external legal review.

**Fast-path eligibility requirements:**
1. The format is on the Pre-Approved Fast-Path List below, OR
2. The format's specification is published by OASIS, W3C, ISO, ECMA, or IETF under documented RF terms, AND
3. At least two independent open-source implementations exist (e.g., LibreOffice, Apache OpenOffice, Calligra for ODF), AND
4. No patent litigation related to the format has been reported in the past five years.

**Fast-path process:**
1. Populate `spec-evidence.md` with primary source URL, exact version, and section references.
2. Write `legal-notes.md` with: legal category (Category 1), rationale for fast-path eligibility, spec body name, RF license citation, date reviewed, project lead sign-off.
3. Mark Gate 2 as passed in the registry.
4. No further review is required unless a patent concern is subsequently discovered.

**Fast-path is NOT available for:**
- Category 2 (permissive OSS implementation) — requires full review
- Category 3 (proprietary spec) — requires full review
- Category 4 (ambiguous docs) — requires full review
- Any format not on the pre-approved list that is not explicitly verified as Category 1

### Pre-Approved Fast-Path List

The following formats are pre-approved for fast-path Gate 2 review based on their well-established open standard status:

- All OASIS ODF variants: ODS, ODT, ODP, ODS, FODS, FODT, FODP (ODF 1.0–1.3)
- W3C XML-based formats: SVG 1.1 and 2.0, XHTML 1.0, MathML
- IETF formats: CSV (RFC 4180), JSON (RFC 8259), JSON Lines (informal but no IP concerns)
- ECMA OOXML: XLSX, DOCX, PPTX (ECMA 376) — **Note:** ECMA 376 has an associated patent pool (Microsoft Community Promise covers parser implementation; legal notes must document this explicitly)

**Important:** Even fast-path formats must still go through Gate 2 with a documented rationale. "Fast-path" means the review is lightweight, not that it is skipped.

---

## Sample License Requirements

Samples acquired for `samples/by-format/` must conform to the following license requirements:

**Acceptable sample licenses:**
- Creative Commons Zero (CC0) — Public Domain Dedication
- Creative Commons Attribution (CC-BY) — attribution required in provenance
- Creative Commons Attribution-ShareAlike (CC-BY-SA) — attribution + share-alike
- Apache 2.0 or MIT (for samples embedded in open-source projects)
- Explicit "public domain" dedication by the creator
- Original samples created specifically for this project (owned by the project)

**Not acceptable:**
- No-derivatives licenses (CC-BY-ND) — prevents modification for test variants
- Non-commercial licenses (CC-BY-NC) — incompatible with commercial product testing
- Unknown or unconfirmed license — must be classified `blocked` until confirmed
- Samples extracted from commercially licensed software — blocked regardless of incidental open access

Every sample must have a provenance entry in `samples/_provenance.yaml` confirming its license before it is committed.

---

## Output License Policy

| Track | Declared License |
|---|---|
| Python open-source product | Apache 2.0 (preferred) or MIT |
| .NET open-source product | Apache 2.0 (preferred) or MIT |
| .NET commercial product | Proprietary (decided at Gate 11) |
| Acquisition evidence | Internal evidence only (not released) |
| Neutral model schemas | Apache 2.0 (same as OSS product) |
| Prototypes | Internal only (not released) |

The exact open-source license (Apache 2.0 vs MIT) is confirmed in `docs/product-tracks.md`. The default assumption is Apache 2.0 unless changed by an explicit project decision.

---

## Patent Risk Framework

For any format not in Category 1, a patent risk assessment must be included in `legal-notes.md`. The assessment must address:

1. Are there known patents that cover parsing, reading, or writing this format?
2. Has the format been involved in patent litigation?
3. Does the rights holder participate in a patent non-assertion covenant (e.g., Microsoft Community Promise)?
4. What is the realistic worst-case legal exposure for a parser-only implementation?

This assessment does not require external legal counsel for Category 2 or Category 3 formats in early phases. It requires honest documented analysis. If the assessment reveals meaningful patent risk, the format must be reclassified to Category 4 or held for proper legal review.

---

## Four Permissions: Read, Implement, Store, Redistribute

When evaluating any specification, four distinct permissions must be assessed independently. Having one permission does not imply having another.

### Permission 1: Read / Access

The right to download, open, and read the specification document. For most public standards (OASIS, W3C, IETF, ECMA, ISO), this is freely permitted. This is the minimum required permission to begin any acquisition work.

### Permission 2: Implement a Parser

The right to write software that reads or writes files conforming to the specification. This is the core permission needed for format-factory work. Most open standards (Category 1) grant this explicitly. Proprietary formats (Category 3) require a specific permission grant (e.g., Microsoft Community Promise for ECMA 376). Reverse-engineered formats (Category 5) typically lack any parser permission.

### Permission 3: Store a Local Copy

The right to download and retain a local copy of the specification document for internal use. Most public standards permit local copies for personal or internal use. The spec-cache stores local copies under `.local/spec-cache/` (gitignored, not committed). **Permission to store a local copy does not imply permission to redistribute.**

### Permission 4: Redistribute or Commit

The right to copy, distribute, or include the specification document in a repository, release package, or publicly accessible location. Most standards bodies explicitly prohibit redistribution of their specification documents even when reading and implementing are freely permitted.

**Default policy:** `redistribution_permitted: false` for all cached specs unless the standards body's terms explicitly grant redistribution rights. Committing a specification document to the git repository requires:
1. Confirmed redistribution permission from the standards body.
2. Explicit human approval documented in the gap register.
3. A visibility classification of `public`.

**Local caching does not imply redistribution rights.** The spec-cache policy stores specs locally for evidence use only. Local-only storage and redistribution are distinct permissions.

---

## Relationship to Other Documents

- See `docs/release-control.md` for visibility classification of legal evidence artifacts.
- See `docs/specification-cache.md` for spec acquisition authorization model and storage policy.
- See `docs/gates.md` for Gate 2 pass criteria and authorization rules.
- See `registry/scoring/_scoring-model.md` for how legal category affects Gate 1 scoring.
- See `acquisition-packs/_template/legal-notes.md` for the legal notes template.
