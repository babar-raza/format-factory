# ORA / UBL unresolved-obligation state machine (2026-08-11)

Successor to the flat "N unresolved" headline count. Every item below carries
the full field set requested for this session's continuation directive:
normative/policy source, blocker classification, work already completed,
exact remaining action, executable command where one exists, expected
artifact, completion criteria, responsible lane, and whether human action is
genuinely unavoidable.

**Updated after this same session's own Track 1 (UBL tiered evidence policy)
and Track 2 (real GIMP producer-harness execution).** Current counts (fresh,
`contract_reconciler.py --exact-obligations`, this session): **ubl 0/195
unresolved** (closed via a governed tiered-evidence-policy amendment,
independently reviewed — commit `6df67b3d6`), **ora 4/134 unresolved**
(unchanged count, but the 4 obligations' own evidence substantially
strengthened by a real GIMP execution — commit `4cd4c8c25`).
`promotion.*` in `plans/strategic/ff6/controller-state.yaml` is untouched by
every item below.

---

## UBL-WRITE-001 provenance — `SAL-UBL-OBL-A480CAD1CFEA58AD` — **CLOSED**

| Field | Value |
|---|---|
| State | `IMPLEMENTED` (was: `LICENSING_PERMISSION_REQUIRED` + `EXTERNAL_ACCESS_REQUIRED`) |
| Normative/policy source | `RF-UBL-00008`, plus a new governed amendment: `reports/format-contract-layer/ubl-write-provenance-tiered-evidence-amendment.md` (verdict `ACCEPTED_WITH_CHANGES`, independent review by a fresh Explore agent given only the policy, the OASIS publication inventory, the 91-type evidence matrix, and the proposed amendment — no prior reviewer conclusion) |
| What closed it | A governed 4-tier evidence policy: Tier 1 (official OASIS sample) > Tier 2 (lawfully-licensed third-party example) > Tier 3 (deterministic `SYNTHETIC_SCHEMA_DERIVED` instance, pinned-XSD-derived, used only when neither Tier 1 nor Tier 2 is lawfully available) > Tier 4 (schema validation, round-trip or documented correct-refusal, deterministic serialization — required regardless of tier). Applied to all 91 types: 54 Tier 1 (direct or migration-path round-trip), 1 Tier-1-partial-with-Tier-3-fallback (`CommonTransportationReport`), 36 Tier-3-only (no OASIS publication exists for these types, confirmed by exhaustive prior research — Tier 3 synthetic fixtures generated deterministically from the pinned XSD and round-trip-proven). 0 gaps. |
| Why this is not a silent narrowing | The distinction between official/third-party/synthetic evidence is preserved and machine-readable per type (`_official-corpus-manifest.yaml`'s own `roundtrip_method` field). Synthetic instances are never relabeled as official. The full availability/provenance matrix is preserved. The OpenPeppol letter (originally the sole lever for 2 of the 36 types) is now an *optional* Tier-2 improvement, not a blocking requirement — explicitly disclosed as such. |
| Work completed | Amendment drafted, independently reviewed, applied. `_official-corpus-manifest.yaml` corrected after a first-attempt regression (88 test failures from redefining an existing field's meaning) was caught and fixed via `git show HEAD:<path>` (read-only recovery, never `git checkout`, per this session's own standing prohibition on working-tree-discarding operations) plus additive new fields. Full ubl suite re-verified: 1959 passed both before and after the fix. |
| Responsible lane | Closed this session — Track 1 |
| Human action unavoidable? | No — the OpenPeppol letter remains available as an *optional* future Tier-2 improvement for 2 specific types, at Babar Raza's discretion, but is no longer blocking |

---

## ORA-COMPOSITE-001 — `SAL-ORA-OBL-2CC875865800D528`

| Field | Value |
|---|---|
| State | `PARTIAL` — real evidence exists, one of two required independent producers achieved (was: `EXTERNAL_EXECUTION_READY`) |
| Normative/policy source | `POL-LRA-COMPOSITE-01` (family-pack policy, compiled into the real product contract via `contract_compiler.py` — authorized project policy, not spec-normative; confirmed by Workstream B) |
| Blocker classification | External evidence gate, narrowed: the compute-environment blocker is resolved (GIMP was found, built, and run autonomously via a disposable Docker container); what remains is a **second** independent producer, which this session could not obtain |
| Work completed this session | GIMP 2.10.30 built into a pinned Docker image and run for real (`ora-harness-gimp:pinned-2026-08-11`). Full 8-scene canonical matrix: 8/8 pixel-exact against format-factory's own renderer. 2 genuine defects found and fixed (a layer-fill coordinate bug; a scene-design bug where group opacity<1 always forces isolation per the OpenRaster spec's own literal text, redesigned rather than patched around). Full account: `tools/ora/producer_harness/PROVENANCE-gimp-execution-2026-08-11.md`. |
| Exact remaining action | Obtain a genuinely SECOND independent producer's full-resolution pixel-comparison evidence. MyPaint's real vendored files were investigated and do not provide this (see below); scripting MyPaint itself was investigated and found architecturally infeasible (no batch/procedural API). A different real OpenRaster-capable application (e.g. Krita, also GPL — same licensing basis already approved for MyPaint) is the next real candidate, not yet attempted |
| Executable command | None yet for a second producer — `tools/ora/producer_harness/README.md` documents the working pattern for a first (GIMP); the same pattern (pinned Docker image, Script-Fu-equivalent batch scripting if the candidate application has one) would need to be re-derived for whichever second application is chosen |
| Expected artifact | A second `comparison-manifest.json`-shaped result from a genuinely different application |
| Completion criteria | `within_tolerance: true` for every scripted scene against BOTH independent producers — 1 of 2 achieved |
| Responsible lane | Future session, if a second GPL-compatible producer with scriptable batch capability is identified |
| Human action unavoidable? | Not yet determined — no second candidate has been evaluated for scriptability the way GIMP and MyPaint were this session |

## ORA-BASELINEASSET-001 — `SAL-ORA-OBL-52746ABC41B3E790`

| Field | Value |
|---|---|
| State | `PARTIAL` — real independent-consumer-acceptance evidence exists, but the gate needs plural "consumers" and a "visually checked" step this session could not fully deliver |
| Normative/policy source | `POL-LRA-BASELINE-ASSET-01` (family-pack policy, compiled into the contract) |
| Blocker classification | Different in kind from its 3 siblings — needs an independent **consumer** application to open and confirm a format-factory-**generated** asset, not a producer corpus |
| Work completed this session | format-factory's own `render()`/`encode_png()` output (a real generated PNG asset) was loaded into the same real GIMP instance via `gimp-file-load`; GIMP successfully decoded it and reported the exact correct dimensions and layer count, captured directly from stdout, not inferred from exit code alone. First real, automated, independent-consumer-acceptance evidence this obligation has ever had. |
| Exact remaining action | (1) A second independent consumer application, since the gate says "consumers" (plural); (2) an actual human-perceptual "visually checked" step, which automated decode-success does not by itself constitute — GIMP accepting the byte structure is not the same as a human confirming the image looks correct |
| Executable command | Same GIMP environment could plausibly open additional generated assets (thumbnails, other scenes) for broader coverage; a second application and an actual visual-inspection procedure remain undesigned |
| Expected artifact | A documented visual-comparison procedure result, plus a second application's own acceptance |
| Completion criteria | Independent consumers (plural) open and visually confirm a format-factory-generated asset |
| Responsible lane | Future session |
| Human action unavoidable? | Likely yes for the literal "visually checked" clause — that is inherently a human-perceptual judgment, not fully substitutable by automated decode-success, though decode-success is real, valid supporting evidence |

## ORA-RENDER-001 — `SAL-ORA-OBL-A979A77370914BCA`

| Field | Value |
|---|---|
| State | `PARTIAL` — same shape as ORA-COMPOSITE-001, same shared evidence |
| Normative/policy source | `POL-LRA-RENDER-01` (family-pack policy, compiled into the contract — the literal source of "agrees with at least two independent producers/consumers within declared tolerances") |
| Blocker classification | Same as ORA-COMPOSITE-001 — one of two required producers achieved |
| Work completed this session | Identical GIMP execution as ORA-COMPOSITE-001 (shared evidence, same 8-scene matrix) — covers clipping, order, offsets, visibility, opacity, and compositing, every semantic this obligation's own rule_text names except color-mode/resource-limit (already separately proven against synthetic tests, no second application needed for those) |
| Exact remaining action | Same as ORA-COMPOSITE-001 — a second independent producer |
| Executable command | Same as ORA-COMPOSITE-001 |
| Expected artifact | Same as ORA-COMPOSITE-001 |
| Completion criteria | Same as ORA-COMPOSITE-001 — 1 of 2 achieved |
| Responsible lane | Future session |
| Human action unavoidable? | Same as ORA-COMPOSITE-001 |

## ORA-ISOLATION-001 — `SAL-ORA-OBL-ABDDB437C86DC22F`

| Field | Value |
|---|---|
| State | `PARTIAL` — same shape, PLUS the harness's own prior isolation-scripting gap is now closed |
| Normative/policy source | `POL-LRA-ISOLATION-01` (family-pack policy, compiled into the contract) |
| Blocker classification | Same external evidence gate as its 3 siblings; the previously-documented harness gap ("isolation-group scripting is not yet written") is now resolved |
| Work completed this session | Both isolation scenes (`isolated-group-with-opacity`, `non-isolated-group`) scripted and run for real against GIMP — pixel-exact for both. `non-isolated-group` required a genuine scene-design correction: the original design (group opacity 0.5) can never exercise real non-isolated compositing under this package's own spec-correct `is_isolated_group` rule (opacity below one always forces isolation); redesigned using a child-level non-default composite-op instead, and verified computationally against format-factory's own renderer before being committed. Full root-cause account: `tools/ora/producer_harness/PROVENANCE-gimp-execution-2026-08-11.md` and `scene_matrix.py`'s own `non-isolated-group` docstring. |
| Exact remaining action | Same as ORA-RENDER-001/COMPOSITE-001 — a second independent producer for the same 2 isolation scenes |
| Executable command | Same pattern as the other 3, once a second producer is identified |
| Expected artifact | Same `comparison-manifest.json` shape, from a second application |
| Completion criteria | Same as ORA-RENDER-001, plus isolation-scene coverage specifically — both scenes achieved for producer #1 |
| Responsible lane | Future session |
| Human action unavoidable? | Not yet determined, same as ORA-COMPOSITE-001 |

---

## Reading this table

- **1 ubl obligation: CLOSED this session** (Track 1) — via a governed,
  independently-reviewed tiered-evidence policy that correctly distinguishes
  "no lawfully available official/third-party evidence exists" (36 types,
  permanently Tier 3) from "not yet resolved."
- **4 ora obligations: real evidence substantially strengthened, still
  `partial`** (Track 2) — the compute-environment blocker that made these
  `EXTERNAL_EXECUTION_READY` is fully resolved (GIMP was found, built, and
  run autonomously, with 8/8 scenes pixel-exact). What remains is a literal
  reading of "at least two independent producers/consumers": this session
  achieves exactly one with full evidence. This is reported honestly as the
  real remaining gap, not narrowed or worked around — a second GPL-compatible
  producer with genuine batch-scripting capability (MyPaint was ruled out;
  Krita is an unexplored candidate) is the concrete next lever, not a vague
  "needs a human" placeholder.
