---
artifact_id: <format-id>-legal-notes-v1
artifact_type: acquisition-pack
path: acquisition-packs/<format-id>/legal-notes.md
format_id: <format-id>
product_family: <cells|words|slides|imaging|diagram|archive>
visibility: evidence-only
publish_allowed: false
license: null
provenance_required: false
provenance_status: not-applicable
source_hash: null
generated_by: <human|claude>
generated_at: <ISO-8601>
reusable: false
refresh_policy:
  trigger: manual
  max_age_days: 730
stale: false
open_source_allowed: false
commercial_allowed: false
release_blockers: []
notes: Gate 2 legal artifact. Always evidence-only. Never released. Sign-off required before gate passage.
---

# Legal Notes — [Format Name]

**Format ID:** `<format-id>`
**Gate:** 2
**Status:** Not started

---

## Legal Category Assignment

| Field | Value |
|---|---|
| Legal category | [1 | 2 | 3 | 4] |
| Category name | [Open Standard RF | Permissive OSS Implementation | Published Proprietary+Permission | Ambiguous Public Documentation] |
| Fast-path eligible | [yes | no] |
| Fast-path basis | [format name on pre-approved list, or manual verification of RF terms] |

---

## Standard Body or Rights Holder

| Field | Value |
|---|---|
| Standard body / rights holder | |
| Publication URL | |
| RF license citation | |
| Date of RF confirmation | |

---

## Permission Grant (Category 2, 3, 4 only)

[For Category 1, this section may say "Not applicable — open standard, royalty-free."]

[For Category 2: Identify the open-source reference implementation, its license, and any relevant notes about spec-drift risk.]

[For Category 3: Cite the exact publication or permission grant by the rights holder. Include the document title, URL, version, and the specific language that grants parser implementation permission.]

[For Category 4: Document the public documentation relied upon and explain why it is being used despite the legal ambiguity.]

---

## Patent Risk Assessment

[For Category 1 on the pre-approved fast-path list: State that no known patents encumber parser implementation of this format based on fast-path eligibility.]

[For all other categories: Address the four questions from docs/legal-and-licensing.md Section "Patent Risk Framework":]

1. Are there known patents that cover parsing, reading, or writing this format?
2. Has the format been involved in patent litigation?
3. Does the rights holder participate in a patent non-assertion covenant?
4. What is the realistic worst-case legal exposure for a parser-only implementation?

---

## Fast-Path Checklist (Category 1 only)

If using the fast-path process from `docs/legal-and-licensing.md`:

- [ ] Format is on the Pre-Approved Fast-Path List, OR manually verified as OASIS/W3C/ISO/ECMA/IETF with documented RF terms
- [ ] At least two independent open-source implementations exist
- [ ] No patent litigation related to this format reported in the past five years
- [ ] `spec-evidence.md` contains primary source URL, exact version, and section references
- [ ] Project lead sign-off below

---

## Residual Risks

[List any legal risks that are accepted rather than mitigated. For each risk, describe the risk and the rationale for accepting it.]

| Risk | Category | Rationale for Acceptance |
|---|---|---|
| | | |

---

## Gate 2 Sign-off

**Reviewed by:** (to be filled — project lead or designated legal reviewer)
**Review date:** (to be filled)
**Fast-path used:** (yes/no)
**Fast-path basis:** (to be filled if fast-path)
**Notes:** (to be filled)

---

## Change Log

| Date | Change | Reviewer |
|---|---|---|
| | Initial creation | |
