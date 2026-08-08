# NRRD Gate 10 (OSS Readiness Complete) Readiness Assessment

**Date:** 2026-08-08
**Prepared by:** claude (autonomous FF6 session, controller event FF6-EVENT-000285)
**Status:** ai_draft — PREPARATION ONLY, NOT AN APPROVAL RECORD

---

## 0. Why this document exists

Same rationale and governing citations as `reports/planning/ipynb/gate10-readiness-20260808.md`
(FF6-EVENT-000283), not repeated in full here.

**This document does not set `gate_10.status`, does not set `visibility: public`
anywhere, and does not write to `plans/strategic/ff6/controller-state.yaml`'s
`promotion` field.**

**Unlike the ipynb and safetensors assessments (FF6-EVENT-000283/284), nrrd's own
obligation-closure state is materially less complete, and this document says so plainly
rather than presenting a uniform picture across formats.**

---

## 1. Gate 10 pass criteria (verbatim from `docs/gates.md`) — assessed against nrrd

| # | Criterion | Status | Evidence |
|---|---|---|---|
| 1 | Production-quality Python source exists for the delivery-plan tiers | **PARTIAL — genuine open work remains** | `src/python/nrrd/src/format_factory/nrrd/` — 21 source files. **18 of 65 obligations remain unresolved** per `shared/format-contracts/implementation-evidence/nrrd.yaml` (freshly reconciler-confirmed at FF6-EVENT-000293 — was 19 at this packet's original writing; FF6-EVENT-000291 closed `validate()`'s own raw-source trailing-payload-reporting gap in the meantime), not merely unaudited: a typed dtype/stride/slicing array API (NRRD-ARRAY-001, 2 obligations), the NRRD0005 measurement-frame transform (NRRD-SPACE-001/FRAME-001, deliberately kept separate from the already-built NRRD0004 index-to-world transform), a detached multi-file partition writer (NRRD-MULTIFILE-001/WRITE-001), a tolerant recovery-read mode (NRRD-LIFECYCLE-001), and encoding/form conversion (NRRD-CONVERT-001) remain genuinely unbuilt, each independently investigated and confirmed out-of-scope-for-a-single-tick this session, not merely deferred without investigation. |
| 2 | Unit/integration tests exist for implemented features | **MET for what exists** | `tests/python/nrrd/` — 622 tests passing (fresh count). Coverage is real for the 47 implemented obligations; the 18 unresolved obligations above correctly have no test claiming to cover them. |
| 3 | Release manifest generated, listing artifacts with visibility/license/provenance | **NOT MET — same mechanical gap as ipynb/safetensors** | Same tooling gap (`tools/validation/generate_manifest.py` needs file-level frontmatter nrrd's files don't have yet). Not the blocking gap for this format regardless — see criterion 1. |
| 4 | Human review of the release manifest | **BLOCKED ON #3 (and, substantively, on #1)** | |
| 5 | OSS solution built in isolation — zero commercial namespace references | **MET** | `tools/validation/check_boundary.py --src-only`: 0 of 59 repo-wide violations involve nrrd. No `src/net/nrrd/` exists. |
| 6 | All test samples have `provenance_status: confirmed` with a compatible OSS license | **MET** | `samples/by-format/nrrd/_provenance.yaml` — all 4 samples `provenance_status: confirmed`, licensed Apache-2.0. |
| 7 | `registry/format-registry.yaml` updated with `gate_10_status: passed` | **NOT DONE** | Not set by this document. |

**Verdict: 2 of 7 criteria cleanly met (5, 6), 1 partially met with real, substantial,
already-scoped remaining work (criterion 1 — 18/65 obligations, mostly large-architecture
items). Unlike ipynb/safetensors, nrrd is honestly NOT close to Gate 10 readiness yet on
its own merits, independent of the mechanical manifest gap.**

---

## 2. Supporting evidence from this session's own 10-gate certification survey (FF6-EVENT-000281)

| Gate | Verdict |
|---|---|
| installed-wheel | STRONG |
| independent-oracle | STRONG — fully green 5/5 as of FF6-EVENT-000281 (was SUSPECT/shadow-bound, then briefly a genuine spec_qname gap, both fixed this session) |
| reproducible-build | STRONG |
| corpus | PARTIAL — 4 samples, thin |
| security | PARTIAL — real tests exist, no dated aggregate report |
| resource | PARTIAL — scattered, real |
| typing | PARTIAL — no dated whole-package report; an ad hoc run this session found 14 issues (mostly import-resolution artifacts of standalone invocation, plus 2 real-looking issues in `codec/payload.py`/`writer.py` not yet triaged) |
| documentation | PARTIAL — candid rather than inflated: README explicitly states "independent Teem/pynrrd certification remain mandatory open obligations" |
| compatibility | PARTIAL, honestly disclosed — `pynrrd==1.1.3` is declared as the reference-implementation extra but genuinely never exercised (no interop test imports it at all, unlike safetensors' now-fixed equivalent) |
| performance | NO_EVIDENCE |

**3 STRONG, 6 PARTIAL, 1 absent — the technical-certification-gate profile itself is
comparable to ipynb/safetensors, but this is a narrower slice than Gate 10's own
criterion 1, which additionally requires the obligation set itself to be substantially
complete.**

---

## 3. Concrete next steps

Two independent tracks, not to be conflated:

1. **Gate 10 mechanical gap** (shared with ipynb/safetensors): release-manifest
   frontmatter, deferred to the human review step per those documents' own §3.
2. **nrrd's own remaining obligation work** (criterion 1, nrrd-specific, substantial):
   the 18 unresolved obligations named above are real product-source gaps, not a
   documentation or process gap. Closing them is ordinary FF6 product-source work,
   already tracked via this session's own controller events, and does not require any
   human gate decision to continue.

## 4. Explicit non-claims

Identical to `reports/planning/ipynb/gate10-readiness-20260808.md` §4, with the
additional, load-bearing non-claim that **nrrd is not represented here as close to
Gate 10 readiness** — criterion 1's own gap is real and unresolved, not merely
unaudited or unpackaged.
