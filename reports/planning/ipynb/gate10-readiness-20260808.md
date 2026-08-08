# IPYNB Gate 10 (OSS Readiness Complete) Readiness Assessment

**Date:** 2026-08-08
**Prepared by:** claude (autonomous FF6 session, controller event FF6-EVENT-000283)
**Status:** ai_draft — PREPARATION ONLY, NOT AN APPROVAL RECORD

---

## 0. Why this document exists

The FF6 mission (`FF6-PRODUCTION-LIBRARIES-001`) has driven `ipynb` to 0/68 unresolved
obligations and a fully green independent-oracle result this session (FF6-EVENT-000281),
but `plans/strategic/ff6/controller-state.yaml`'s own `promotion.ipynb` field has stayed
`UNASSESSED` throughout — the goal_driver's own hardcoded next-action text
("ipynb obligations resolved; run certification gates") gave no concrete mechanism for
what "run certification gates" means or who is authorized to act on the result.

This document resolves that ambiguity with citation, for this and future sessions:

- **`docs/gates.md`, Gate 10 section:** *"Gate 10 is the gate that changes
  `format-registry.yaml` visibility from `internal` to `public`."* This — not Gate 11 — is
  the gate relevant to FF6's own goal (publishable Python FOSS libraries with no commercial
  `.NET` track; product-goal.yaml lists only Python distributions).
- **`docs/gates.md`, "Gate Status Fields in Registry":** *"An agent must update
  `gate_N.status` to `passed` only after human approval has been confirmed... An agent must
  never set `status: passed` without human confirmation."*
- **`docs/ai/ai-assisted-acquisition-pipeline.md`, Gate 10 row:** AI role is
  "Release readiness gap analysis," output is "Readiness assessment (ai_draft)," authority
  is "Human approves release candidate."
- **CLAUDE.md's own standing rule:** "PREPARATION is always agent-owned (prepare packet,
  assess readiness, verify). Only the final commercial sign-off requires human business
  authority" — Gate 10 is the OSS-track equivalent checkpoint, and this document is that
  preparation.

**This document does not set `gate_10.status`, does not set `visibility: public` anywhere,
and does not write to `plans/strategic/ff6/controller-state.yaml`'s `promotion` field.** It
is the packet a human reviewer needs to make that call.

---

## 1. Gate 10 pass criteria (verbatim from `docs/gates.md`) — assessed against ipynb

| # | Criterion | Status | Evidence |
|---|---|---|---|
| 1 | Production-quality Python source exists for the delivery-plan tiers | **MET** | `src/python/ipynb/src/format_factory/ipynb/` — 32 source files, ~5,905 LOC. All 68 obligations `implemented` per `shared/format-contracts/implementation-evidence/ipynb.yaml` (0 unresolved, reconciler-confirmed). |
| 2 | Unit/integration tests exist for implemented features | **MET** | `tests/python/ipynb/` — 41 test files, 720 tests passing (this session's own regression run). |
| 3 | Release manifest generated, listing artifacts with visibility/license/provenance | **NOT MET — mechanical gap, not a content gap** | `tools/validation/generate_manifest.py --release-type oss` scans for `visibility: public` YAML frontmatter on individual files (not a registry-level field) — ipynb's own source/doc files carry no such frontmatter yet, so the tool currently reports 0 ipynb artifacts (2 unrelated fods/fodt README.md files were the only hits repo-wide). This is a file-metadata gap, not evidence ipynb's own content is unready — see §3. |
| 4 | Human review of the release manifest: no `commercial`/`blocked`/unreviewed `generated` artifacts | **BLOCKED ON #3** | Cannot be performed until a manifest listing ipynb's own artifacts exists. |
| 5 | OSS solution built in isolation — zero commercial namespace references | **MET** | `tools/validation/check_boundary.py --src-only` run repo-wide this session: 59 total violations, **0 involving ipynb** (all 59 are in `src/net/fods/*.cs`, an unrelated commercial .NET file). No `src/net/ipynb/` exists at all — consistent with FF6's pure-Python-FOSS scope. |
| 6 | All test samples have `provenance_status: confirmed` with a compatible OSS license | **MET** | `samples/by-format/ipynb/_provenance.yaml` — all 4 samples `provenance_status: confirmed`, licensed Apache-2.0 or BSD-3-Clause (nbformat's own upstream license, `LICENSE.nbformat-BSD-3-Clause.txt` present with a recorded sha256). |
| 7 | `registry/format-registry.yaml` updated with `gate_10_status: passed` | **NOT DONE — requires human review per criterion 4** | Not set by this document. |

**Verdict: 4 of 7 criteria cleanly met (1, 2, 5, 6). Criteria 3–4 are blocked on a
mechanical, well-scoped gap (missing file-level release frontmatter), not a content or
quality gap. Criterion 7 is the human gate itself.**

---

## 2. Supporting evidence from this session's own 10-gate certification survey (FF6-EVENT-000275)

Beyond Gate 10's own 7 criteria, this session separately surveyed ipynb against
`product-goal.yaml`'s 10 named technical-certification gates (installed-wheel,
independent-oracle, corpus, security, resource, typing, documentation, compatibility,
performance, reproducible-build):

| Gate | Verdict (as of this session) |
|---|---|
| installed-wheel | STRONG — dated, isolated-venv, non-editable install proof |
| independent-oracle | STRONG — fully green 5/5 as of FF6-EVENT-000281 (was SUSPECT/bound to a shadow package until FF6-EVENT-000275 fixed it) |
| reproducible-build | STRONG — sensitivity-tested, byte-identical builds at fixed `SOURCE_DATE_EPOCH` |
| corpus | PARTIAL — real but thin (4 samples); broader coverage lives in obligation test fixtures |
| security | PARTIAL — real shipped-namespace tests exist; no dated mutation-kill-rate aggregate report |
| resource | PARTIAL — real but scattered across obligation tests, no dedicated stress report |
| typing | PARTIAL — `mypy --strict` config present, no dated whole-package report artifact |
| documentation | PARTIAL — README/SECURITY/CHANGELOG exist, no generated API reference |
| compatibility | PARTIAL — real interop tests against the shadow-package-excluded namespace |
| performance | NO_EVIDENCE — no benchmark exists for any FF6 format yet |

This is a genuinely strong technical profile (3 STRONG, 6 PARTIAL-but-real, 1 absent) —
consistent with, and additional context for, the Gate 10 assessment above.

---

## 3. Concrete next steps to close the Gate 10 mechanical gap (criteria 3–4)

None of these require product-code changes; ipynb's own source and tests are already
sufficient per criteria 1, 2, 5, 6:

1. Add `visibility: public`, `publish_allowed: true`, `open_source_allowed: true` YAML
   frontmatter to the specific files `generate_manifest.py` expects (its own
   `is_oss_eligible()` check) — likely `src/python/ipynb/README.md` at minimum, possibly
   extended to cover the package's other top-level docs. **This step itself is a
   release-readiness declaration and should be done as part of, not before, the human
   review this document requests** — adding it unilaterally would preempt exactly the
   review Gate 10 exists to perform.
2. Re-run `tools/validation/generate_manifest.py --release-type oss` and confirm ipynb's
   artifacts appear with correct `license`/`provenance_status`.
3. A human (per `docs/gates.md`'s own binding rule) reviews the resulting manifest and,
   if satisfied, records `gate_10.status: passed`, `approved_by`, and `approved_date` in
   `registry/format-registry.yaml` for the `ipynb` entry.

## 4. Explicit non-claims

- This document does not claim ipynb is "certified," "production-ready for release," or
  "Gate 10 passed."
- This document does not modify `registry/format-registry.yaml`, any `visibility` field,
  or `plans/strategic/ff6/controller-state.yaml`'s `promotion` field.
- Corpus/security/resource/typing/documentation/performance gates from §2 remain
  genuinely PARTIAL or absent — closing the Gate 10 mechanical gap does not resolve those,
  and they are independent, ongoing work tracked separately in this session's own
  FF6 controller events (275, 280, 281).
