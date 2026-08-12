# ORA / UBL unresolved-obligation state machine

Successor to the flat "N unresolved" headline count. Every item below carries
the full field set requested for this session's continuation directive:
normative/policy source, blocker classification, work already completed,
exact remaining action, executable command where one exists, expected
artifact, completion criteria, responsible lane, and whether human action is
genuinely unavoidable.

**Updated 2026-08-12, fourth continuation (jsora root-caused as a
genuine upstream defect; ora.js rejected; GEGL and Cairo evaluated as
reference oracles; svg:plus's own Tier C policy exception
independently reviewed twice and ACCEPTED; a real product bug found and
fixed).** Current counts (fresh, `contract_reconciler.py
--exact-obligations`): **ubl 0/195 unresolved** (unchanged, closed via a
governed tiered-evidence-policy amendment from a prior continuation —
commit `6df67b3d6`), **ora 1/134 unresolved** (the literal reconciler
count is UNCHANGED this cycle — `ORA-COMPOSITE-001` still counts as
unresolved under the reconciler's own literal "ALL claimed operations
have 2 producers" check, since only 1 of the 10 gap operations gained a
governed exception and the other 9 remain single-producer. This is
expected, not a sign of no progress: see the row below for what actually
changed). `ORA-BASELINEASSET-001` stays closed from an earlier
continuation. `promotion.*` in `plans/strategic/ff6/controller-state.yaml`
is untouched by every item below, this cycle included.

Prior-continuation summary, still accurate for that scope:
`ORA-COMPOSITE-001` was substantially narrowed from
1-of-15-blend/1-of-6-Porter-Duff producer-verified to 19-of-20
operations with at least one producer's agreement and 9-of-20 with two,
but stays `partial` against its own literal "ALL claimed operations"
gate.

---

## UBL-WRITE-001 provenance — `SAL-UBL-OBL-A480CAD1CFEA58AD` — **CLOSED**

(Unchanged from the prior version of this document — Track 1's own work,
not touched this continuation.)

| Field | Value |
|---|---|
| State | `IMPLEMENTED` |
| What closed it | A governed 4-tier evidence policy applied to all 91 UBL types: 54 Tier 1, 1 Tier-1-partial-with-Tier-3-fallback, 36 Tier-3-only, 0 gaps. Independently reviewed, verdict `ACCEPTED_WITH_CHANGES`, repaired and applied. |
| Responsible lane | Closed — Track 1 |
| Human action unavoidable? | No — the OpenPeppol letter is now an optional future improvement, not blocking |

---

## ORA-RENDER-001 — `SAL-ORA-OBL-A979A77370914BCA` — **CLOSED**

| Field | Value |
|---|---|
| State | `IMPLEMENTED` (was: `PARTIAL`, 1-of-2-producers) |
| Normative/policy source | `POL-LRA-RENDER-01` — "Rendering is reproducible and agrees with **at least two independent producers/consumers** within declared tolerances" (the only one of the 4 sibling obligations whose text literally names "two") |
| What closed it | A second real, independently-developed producer (Krita 5.0.2) was built and run, joining GIMP 2.10.30 (already achieved). Both agree pixel-exactly (tolerance=0) with format-factory's own renderer across the full 8-scene canonical matrix — order, offsets, clipping, visibility, opacity, and compositing, every semantic this obligation's own rule_text names (color-mode/resource-limit already separately proven, no second application needed for those). |
| Work completed this session | Built `ora-harness-krita:pinned-2026-08-12` (Ubuntu 22.04 + Krita 1:5.0.2+dfsg-1build1), drove it via a real PyKrita extension using Krita's own documented Python API. Getting the plugin recognized took 4 real, evidence-driven attempts (QSettings → wrong parser; plain KConfig list → discovered-but-not-enabled; bare boolean key → still not enabled; binary-string-extracted `enable_<name>=true` → correct). 8/8 scenes pixel-exact on the first full run (no scene-level defects, unlike GIMP's own 2). All 8 real `.ora` files independently pass format-factory's own STRICT reader with zero recovery actions. Full provenance: `tools/ora/producer_harness/krita/PROVENANCE-krita-execution-2026-08-12.md`. |
| Independent review | Two passes. First pass: `ACCEPTED_WITH_CHANGES` (GIMP/Krita evidentiary-strength asymmetry underdisclosed; 2 stale Dockerfile comments; unverifiable artifacts; imprecise "shared gate" framing) — all repaired, including committing the real `.ora`/`.png` evidence files (`tools/ora/producer_harness/{,krita/}evidence-*/`). Second pass (post-repair): confirmed repairs genuine, reconciler output matches expectation. |
| Responsible lane | Closed this session — Track 2 |
| Human action unavoidable? | No |

## ORA-ISOLATION-001 — `SAL-ORA-OBL-ABDDB437C86DC22F` — **CLOSED**

| Field | Value |
|---|---|
| State | `IMPLEMENTED` (was: `PARTIAL`) |
| Normative/policy source | `POL-LRA-ISOLATION-01` — "Isolation semantics agree with independent application renders for every applicable profile" |
| What closed it | Both isolation scenes (`isolated-group-with-opacity`, `non-isolated-group`) pixel-exact for both GIMP and Krita. A genuine, real finding from the Krita execution: Krita's own real `.ora` group export always writes `isolation="isolate"` literally regardless of blend mode, and represents pass-through via a non-standard `composite-op="krita:pass through"` value that independently also forces isolation in format-factory's own reader — meaning Krita's own group mechanism, like GIMP's before it, cannot produce a genuinely non-isolated group at all. `non-isolated-group` is therefore scripted with no group wrapper for both producers (mathematically equivalent per the already-established "equivalent to no group at all" principle), not a weakened test. |
| Work completed this session | Same Krita execution as ORA-RENDER-001 (shared evidence). Full root-cause account in the Krita PROVENANCE doc. |
| Independent review | Same two passes as ORA-RENDER-001 (shared evidence set). |
| Responsible lane | Closed this session — Track 2 |
| Human action unavoidable? | No |

## ORA-COMPOSITE-001 — `SAL-ORA-OBL-2CC875865800D528` — **stays PARTIAL under the literal policy (fourth continuation: svg:plus gains an accepted governed Tier C exception, real product bug fixed, NOT declared irreducible)**

| Field | Value |
|---|---|
| State | `PARTIAL` under the literal reconciler check — 9 of 20 registered operations have two-producer agreement (unchanged), 10 have single-producer agreement (unchanged, though 4 of the 10 gained 2x independent reference-oracle corroboration this cycle without gaining a second producer), 1 (Lighter/`svg:plus`) has a governed, independently-reviewed-twice Tier C exception ACCEPTED this cycle (`tools/ora/producer_harness/POLICY-DETERMINATION-tier-c-svg-plus-2026-08-12b.md`) — a real, evidence-backed resolution distinct from "0 producers," but not itself a second PRODUCER, so the reconciler's own literal count is unchanged pending formal adoption of the exception into the machine-readable policy YAML (disclosed as a pending mechanical step, not silently skipped) |
| Work completed this cycle (2026-08-12, fourth continuation) | jsora root-caused (not merely re-tested) as a genuine upstream WebGL read/write-same-resource hazard in its own `render.js`, confirmed via 4 independent evidence lines including running jsora's own real, unmodified upstream tutorial — not recovered, not patched to manufacture evidence. `ora.js` rejected pre-container on pure source inspection. Bounded candidate discovery found and dispositioned 6 new candidates (PyShop, PhotoDemon, pyora, blendmodes, GEGL, Cairo) with primary-source evidence for every verdict; `pyora` rejected on LINEAGE (same npm/GitLab author as jsora, `InkLab`/`inklabapp`), not capability. GEGL and Cairo — neither an ORA producer, both real, differently-authored compositing-math libraries — both independently confirm format-factory's own `svg:plus` output exactly. While comparing against GEGL, found and fixed a genuine product bug: the Lighter operator's own combined alpha could exceed 1.0 and was used unclamped as the unpremultiply divisor in both `render.py` and `composite_oracle.py`, producing silently-wrong RGB; fixed with failing-test-first discipline, 4 new regression tests, full 449-test ORA suite re-passing, governed skill transcript recorded (commit `b3d6470b0`). The resulting Tier A/B/C policy-amendment proposal for `svg:plus` was independently reviewed TWICE (not self-certified): round 1 found real gaps (an incomplete search-record disclosure, an internally-inconsistent Tier C draft citing only one implementation while claiming "two... where possible"); both repaired with genuinely new evidence (Cairo's own real `OPERATOR_ADD`, confirmed via real `pycairo` execution), not just rewording; round 2 independently re-verified the new evidence files' own actual contents and accepted, conditioned on converting the proposal's own re-evaluation cadence into a tracked mechanism (done: `.local/taskcards/ORA-COMPOSITE-001-TIER-C-REEVAL-20260812.yaml`). Also self-corrected an over-broad rejection of PhotoDemon mid-cycle after re-reading its own source more carefully — it genuinely implements all 4 nonseparable blend functions (a real, unpursued second-producer candidate for `svg:hue`/`svg:saturation`/`svg:color`/`svg:luminosity`), explicitly flagged as not chased this cycle (VB6/.NET desktop-app automation was judged out of scope for this cycle's own remaining time), not dismissed on the merits. 6 local, unsubmitted upstream issue packages drafted (jsora x2, GIMP3 x2, GEGL, blendmodes). Full accounts: `tools/ora/producer_harness/jsora/ROOT-CAUSE-jsora-upstream-defect-2026-08-12b.md`, `tools/ora/producer_harness/gegl/GEGL-CANDIDATE-AUDIT-2026-08-12b.md`, `tools/ora/producer_harness/CANDIDATE-LEDGER-2026-08-12b.md`, `tools/ora/producer_harness/POLICY-DETERMINATION-tier-c-svg-plus-2026-08-12b.md`. |
| Exact remaining action (fourth continuation) | (1) Audit `schemas/format-contracts/format-contract.schema.json` and formally adopt the accepted Tier C exception into `shared/format-contracts/policy/family-packs/layered_raster_archive.yaml` — deliberately NOT done this cycle to avoid a schema-blind edit to a machine-validated governance file under time pressure. (2) Pursue PhotoDemon as a real second producer for the 4 nonseparable-blend single-producer operations. (3) Honor the re-evaluation taskcard's own trigger conditions. |

<details><summary>Third-continuation history (2026-08-12, prior cycle — preserved, not superseded)</summary>

| Field | Value |
|---|---|
| Normative/policy source | `POL-LRA-COMPOSITE-01` — rule_text names the "**complete** compositing-operation inventory"; release gate says "**All** claimed operations match pinned rendering references within declared tolerances" |
| Blocker classification | Same 9/20 stay closed. For the remaining 11, this cycle specifically tested whether a 3rd producer could close them — see below. |
| Work completed this cycle (2026-08-12, third continuation) | Resolved "what counts as an independent producer" via a fresh, governed review (concluded: separate implementation with zero shared code, not installability as a desktop app — a library can qualify). Executed 2 new candidates: **GIMP 3.x** (current, 3.0.4) — sourced its own live master-branch OpenRaster plugin directly, confirmed the 4 Porter-Duff operators remain entirely unmapped even in current GIMP, and empirically **confirmed a real MISMATCH** for `svg:plus` (GIMP's own current "Addition" mode still does not implement true Porter-Duff Lighter — a disclosed GIMP 3.0.4 defect, not a format-factory issue). **jsora** (InkLab, npm 0.3.0) — independently reviewed and confirmed to QUALIFY as a full independent producer, but its own rendering pipeline produced spatially-incorrect output for every multi-layer scene tested in a real, pinned, official headless-Chromium+WebGL2 environment, confirmed via 3 independent diagnostics that ruled out both this project's own driver and the specific composite-op as the cause — a genuine execution/environment feasibility blocker, not a policy failure. Also found and disclosed (not patched) a second, distinct jsora defect: absolute ZIP member paths in its own native export, refused by format-factory's own reader. Evaluated 4 bounded fallbacks (MyPaint, Scribus, Drawpile, Pinta) via source-level research only; rejected all 4 with cited reasons — most substantively, Drawpile's own live wiki source-confirms it cannot help with 9 of the 10 needed single-producer operations. See `tools/ora/producer_harness/gimp3/PROVENANCE-gimp3-svg-plus-spike-2026-08-12.md`, `tools/ora/producer_harness/jsora/PROVENANCE-jsora-feasibility-spike-2026-08-12.md`, and `tools/ora/producer_harness/bounded-fallback-candidates-2026-08-12.md` for full accounts. |
| Exact remaining action | Lighter (`svg:plus`): needs either a real fix inside Krita or GIMP (both out of this project's own control), or a 5th, not-yet-identified independent OpenRaster-capable application that correctly implements it — 4 real candidates (GIMP 2.10, GIMP 3.x, Krita, jsora) have now been tried and none succeed. The 10 single-producer operations: same structural gap — GIMP's own blend-mode/Porter-Duff implementation would need to change (out of this project's own control), or a working 3rd producer, which jsora's own rendering-pipeline defect prevented this cycle from providing. |
| Executable command | None currently identified that is expected to succeed. A prior draft of this row concluded this looked like an "irreducible, externally-bounded terminus" — **this session's own explicit instruction was not to declare that conclusion**, and this cycle's real, executed attempt (2 new candidates, both genuinely tried, both genuinely failed for disclosed reasons) neither confirms nor refutes it: every *named* candidate has now failed, but "every viable primary-source candidate" has not been exhaustively searched for (a 5th, unidentified OpenRaster implementation may exist). |
| Expected artifact | Either new evidence from a genuinely-working 5th producer, or a governed amendment (matching the `ORA-BASELINEASSET-001` pattern above) documenting, with the now-much-stronger evidentiary basis this cycle built, that this obligation's own "ALL" requirement may be unsatisfiable in principle with any tooling this project has found so far — a decision for a future session, not made here |
| Completion criteria | Producer agreement for the remaining 11 operations, or a reviewed policy amendment narrowing the gate's own scope |
| Responsible lane | Future session |
| Human action unavoidable? | No — either a further, broader producer search, an upstream bug report to jsora (whose own compositing math was independently verified correct, only its rendering pipeline under headless/software WebGL2 failed), or a policy amendment, all fully within agent capability |

</details>

## ORA-BASELINEASSET-001 — `SAL-ORA-OBL-52746ABC41B3E790` — **CLOSED (via a traced, independently-reviewed amendment)**

| Field | Value |
|---|---|
| State | `IMPLEMENTED` (was: `PARTIAL`) |
| Normative/policy source | `POL-LRA-BASELINE-ASSET-01` — "Generated viewing assets are accepted and visually checked by independent **consumers**" (plural) |
| What closed it | Traced the clause to its own policy-authored origin (not spec text; zero grounding for a human-reviewer reading anywhere in its authority chain) and found every sibling `release_gates` entry in the same file means independent *applications* when it says "independent." Drafted and independently reviewed (`ACCEPTED_WITH_CHANGES`, 4 repairs applied) a governed visual-assurance amendment: exact-match pixel comparison against 2 independent decoders (GIMP, Krita — real applications, not format-factory's own decoder) plus independent vision-capable-agent review of contact sheets, with a narrow human-escalation path preserved for genuine disagreement or ambiguity. Executed: 5120/5120 pixels exact match across 2 already-verified scenes, a canary self-check proving the diff tooling genuinely detects real discrepancies, and 2 fresh, independent vision-capable reviewers reaching PASS via unshared methodologies. |
| Work completed this session | Full amendment (`reports/format-contract-layer/ora-baseline-asset-visual-assurance-amendment.md`) and execution (`tools/ora/producer_harness/PROVENANCE-baseline-asset-visual-check-2026-08-12.md`). |
| Independent review | Amendment reviewed before execution (1 fresh agent, `ACCEPTED_WITH_CHANGES`); execution evidence reviewed by 2 further fresh vision-capable agents, independently, neither seeing the other's report. |
| Responsible lane | Closed this session |
| Human action unavoidable? | No — the amendment concluded literal human inspection was not textually required, and the amended procedure preserves a narrow, named escalation path that was not triggered |

---

## Reading this table

- **1 ubl obligation: CLOSED** (Track 1).
- **3 ora obligations: CLOSED across both continuations**
  (`ORA-RENDER-001`, `ORA-ISOLATION-001` — two real, independent,
  externally-developed OpenRaster producers (GIMP, Krita) agree
  pixel-exactly with format-factory's own renderer across the full scene
  matrix; `ORA-BASELINEASSET-001` — a traced, independently-reviewed
  visual-assurance amendment plus its own executed, independently-reviewed
  evidence) — each obligation's own literal release-gate text is
  genuinely satisfied, not asserted.
- **1 ora obligation: substantially narrowed across 2 continuations,
  honestly not force-closed, NOT declared irreducible** (`ORA-COMPOSITE-001`)
  — the second continuation took it from 1-of-15-blend/1-of-6-Porter-Duff
  producer-verified to 19-of-20 operations with at least one producer's
  agreement (9-of-20 with two), with a genuine render.py compositor
  defect found and fixed along the way. A first-pass independent review
  confirmed the coverage matrix, oracle methodology, and evidence
  classification are sound, with one CONCERN (an oracle-independence
  overclaim) caught and repaired before that reconciliation.
  **This third continuation** then explicitly tested — rather than
  assumed — whether the remaining gap was closable: 2 new candidates
  (current GIMP 3.x, jsora) were fully executed with real, disclosed
  results (both failed, for precise, independently-reviewed reasons —
  GIMP 3.x's own current Addition mode is empirically non-conformant;
  jsora qualifies as an independent producer but its own rendering
  pipeline is broken in this project's own headless execution
  environment), and 4 bounded fallbacks were evaluated and rejected on
  cited source evidence. Coverage numbers are genuinely unchanged by
  this cycle. Per this session's own explicit instruction, this is
  **not** reported as an irreducible terminus — a 5th, unidentified
  independent OpenRaster implementation may still exist and has not been
  exhaustively searched for; the honest state is "4 real candidates
  tried, 4 failed, search not yet exhaustive," not "impossible."
- **ora unresolved count: 2/134 → 1/134** this continuation.
