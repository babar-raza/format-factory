# UBL Gate 10 (OSS Readiness Complete) Readiness Assessment

**Date:** 2026-08-08
**Prepared by:** claude (autonomous FF6 session, controller event FF6-EVENT-000288)
**Status:** ai_draft — PREPARATION ONLY, NOT AN APPROVAL RECORD

---

## 0. Why this document exists

FF6-EVENT-000288's own investigation flagged that ubl (like xliff) had never had a Gate 10
readiness packet prepared, unlike ipynb, safetensors, and nrrd (FF6-EVENT-000283/284). This
document closes that gap using the exact same method and citations established there —
see `reports/planning/ipynb/gate10-readiness-20260808.md` §0 for the full citation chain
(`docs/gates.md`, `docs/ai/ai-assisted-acquisition-pipeline.md`, CLAUDE.md). Summarized:
Gate 10 (not Gate 11, which is `.NET`-commercial-only) is the FF6-relevant checkpoint;
an agent may prepare the readiness packet but must never set `gate_10.status: passed`
without recorded human approval.

**This document does not set `gate_10.status`, does not set `visibility: public` anywhere,
and does not write to `plans/strategic/ff6/controller-state.yaml`'s `promotion` field.**

---

## 1. Gate 10 pass criteria (verbatim from `docs/gates.md`) — assessed against ubl

| # | Criterion | Status | Evidence |
|---|---|---|---|
| 1 | Production-quality Python source exists for the delivery-plan tiers | **MET, with a known scope gap** | `src/python/ubl/src/format_factory/ubl/` — 36 source files, ~5,537 LOC. 186/194 obligations `implemented` per `shared/format-contracts/implementation-evidence/ubl.yaml` (8 unresolved, reconciler-confirmed as of this session, including 1 obligation narrowed missing→partial this session at FF6-EVENT-000288). |
| 2 | Unit/integration tests exist for implemented features | **MET** | `tests/python/ubl/` — 54 test files, 1018 tests passing (this session's own regression run, includes the 5 new tests added for schema-order writing at FF6-EVENT-000286). |
| 3 | Release manifest generated, listing artifacts with visibility/license/provenance | **NOT MET — mechanical gap, not a content gap** | Same repo-wide gap documented for ipynb and xliff: `tools/validation/generate_manifest.py --release-type oss` requires file-level `visibility: public` YAML frontmatter that no FF6 format's files carry yet. Not ubl-specific. |
| 4 | Human review of the release manifest: no `commercial`/`blocked`/unreviewed `generated` artifacts | **BLOCKED ON #3** | Cannot be performed until a manifest listing ubl's own artifacts exists. |
| 5 | OSS solution built in isolation — zero commercial namespace references | **MET** | `tools/validation/check_boundary.py --src-only` re-run this session: 0 of 59 total repo-wide violations reference `ubl` (all 59 are in unrelated `src/net/fods/*.cs`). No `src/net/ubl/` exists — consistent with FF6's pure-Python-FOSS scope. |
| 6 | All test samples have `provenance_status: confirmed` with a compatible OSS license | **MET** | `samples/by-format/ubl/_provenance.yaml` — all 7 samples `provenance_status: confirmed`, Apache-2.0 (project-owned synthetic, generated via Python stdlib `xml.etree.ElementTree` and the package's own `write_ubl` round-trip, no third-party dependency). |
| 7 | `registry/format-registry.yaml` updated with `gate_10_status: passed` | **NOT DONE — requires human review per criterion 4** | Not set by this document. |

**Verdict: 3 of 7 criteria cleanly met (2, 5, 6). Criterion 1 is met for the implemented
majority but carries a real, quantified content gap (8/194 obligations unresolved) — see
§2 for what those are, including the one this session's own work directly narrowed.
Criteria 3–4 share the same mechanical, repo-wide frontmatter gap as every other FF6
format. Criterion 7 is the human gate itself.**

---

## 2. The 8 remaining unresolved obligations (honest accounting)

**Correction (FF6-EVENT-000293):** this section originally claimed `UBL-CODELIST-001`
was "the majority of the 8" remaining obligations. That claim was stale, carried forward
from an earlier session narrative without a fresh check against this session's own
reconciler output, and was wrong: a direct reconciliation run confirms all 10
`UBL-CODELIST-001` obligations are `implemented`. The table below lists the actual 8,
verified directly against `reports/format-contract-layer/ubl-obligation-reconciliation.json`
at the time of this correction.

| Obligation | Capability | Nature of the gap |
|---|---|---|
| `SAL-UBL-OBL-0996E6D7B91D544F` | `UBL-PARSE-001` | `find()`/`find_all()` (model/typed.py) can return a spoofed element's value when called directly without validating the document first — a real, confirmed primitive-level gap, not merely untested. |
| `SAL-UBL-OBL-237188D47391391E`, `SAL-UBL-OBL-AF5263F0FC7036B9` | `UBL-EDIT-001` (2 obligations) | No CRUD API for core business components beyond the low-level, schema-unaware `XmlNode.with_children()`/`UblDocument.with_root()` immutable-replace primitives — confirmed by grepping the whole package for a mutation/edit module (none exists). A typed builder/mutation API redesign was independently investigated and rejected as out of scope for a single slice, both earlier this session and re-confirmed at FF6-EVENT-000288. |
| `SAL-UBL-OBL-49E8A72A55F540E1` | `UBL-REF-001` | "Broken references" and "inconsistent line references" are not built as dedicated diagnostics. `DocumentIndex.by_id()`/`lines_referencing_item_id()` (model/query.py) exist and could be composed into such a check the same way `duplicate_line_ids()` already is, but the exact UBL semantics of what counts as a "broken" cross-document reference (many reference roles legitimately point outside a single document) were judged too ambiguous to build without inventing unstated spec content — deliberately left unattempted rather than risk false positives on valid documents. |
| `SAL-UBL-OBL-6C91BBF7F11E4402` | `UBL-LIFECYCLE-001` | `reader.py` validates `mode` is one of `"strict"`/`"preservation"` but never branches on its value — both modes reject malformed input identically. A genuine tolerant/recovery read mode does not exist. |
| `SAL-UBL-OBL-788B2748204338B8` | `UBL-VALIDATE-001` | The 5 validation layers (`validate()`, `schema_validate()`, `DocumentIndex` methods, `CodeListRegistry.validate_code`, `ProfileValidatorRegistry`) are not unified into one combined call; would additionally require a pluggable business-rule mechanism with a real default rule set, a genuinely separate, larger undertaking. |
| `SAL-UBL-OBL-7B16479ACBBC8EFC` | `UBL-UPGRADE-001` | No transform infrastructure exists for any UBL version pair (2.0→2.3, 2.1→2.3, etc.) — needs concrete version-migration semantics beyond the one coarse SAL fact currently mapped, a real, scoped design item. |
| `SAL-UBL-OBL-F9D5251F2302AE3A` | `UBL-WRITE-001` (narrowed this session) | The schema-valid-element-order clause is now `implemented` (FF6-EVENT-000286's `reorder_for_schema_order()`). The obligation's own remaining clause — proving round-trip fidelity against **real official UBL sample documents** — needs a genuine external corpus; the project's own samples are synthetic (see `samples/by-format/ubl/_provenance.yaml`), sufficient for Gate 10 criterion 6 but not for this obligation's own official-round-trip claim. |

None of these are stale-evidence reconciliation gaps — all 8 were independently re-verified
this session (including a fresh word-for-word duplicate-rule_text sweep against every other
already-implemented ubl obligation, which found none) as requiring either new external data
(an official sample corpus), genuine new design work (version-migration semantics, a unified
validation call, a CRUD API), or a semantics question too ambiguous to resolve without
inventing unstated spec content (broken-reference detection).

---

## 3. Concrete next steps

1. Same repo-wide frontmatter step as every other format's Gate 10 packet — deferred to
   the same human-reviewed batch, not done unilaterally here.
2. None of the 8 remaining obligations are small: `UBL-PARSE-001`'s own remaining gap
   is itself a real cross-cutting audit (the document-level namespace-spoofing detection
   already in place is a genuine defense-in-depth mitigation, but the obligation's own
   full "unambiguous resolution" claim needs roughly 78 call sites across
   typed.py/aggregates.py/charges.py/reference.py/document.py individually audited and
   fixed to check namespace, not just local name — comparable in scope to the CRUD API
   or unified-validation items, not a quick follow-up).
3. Gate 10's own text does not require 100% obligation closure, only "production-quality
   source... for the delivery-plan tiers." Whether 186/194 clears that bar is a human
   judgment call, not this document's to make.

## 4. Explicit non-claims

- This document does not claim ubl is "certified," "production-ready for release," or
  "Gate 10 passed."
- This document does not modify `registry/format-registry.yaml`, any `visibility` field,
  or `plans/strategic/ff6/controller-state.yaml`'s `promotion` field.
- The 8 unresolved obligations in §2 are not hidden or minimized — they are the single
  biggest open question this document surfaces for human review.
