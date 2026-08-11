# ORA / UBL unresolved-obligation state machine (2026-08-11)

Successor to the flat "N unresolved" headline count. Every item below carries
the full field set requested for this session's continuation directive:
normative/policy source, blocker classification, work already completed,
exact remaining action, executable command where one exists, expected
artifact, completion criteria, responsible lane, and whether human action is
genuinely unavoidable.

Current counts (fresh, `contract_reconciler.py --exact-obligations`, this
session): **ora 4/134 unresolved**, **ubl 1/195 unresolved** (up from 194 —
Workstream A split one conflated obligation into two precisely-scoped ones).
`promotion.*` in `plans/strategic/ff6/controller-state.yaml` is untouched by
every item below.

---

## ORA-COMPOSITE-001 — `SAL-ORA-OBL-2CC875865800D528`

| Field | Value |
|---|---|
| State | `EXTERNAL_EXECUTION_READY` |
| Normative/policy source | `POL-LRA-COMPOSITE-01` (family-pack policy, compiled into the real product contract via `contract_compiler.py` — authorized project policy, not spec-normative; confirmed by Workstream B) |
| Blocker classification | External evidence gate — needs a real second independent OpenRaster producer's output to compare against |
| Work completed | Rendering/compositing engine built and proven via hand-computed arithmetic + a genuinely independent second implementation (`StraightAlphaReferenceRenderer`, commit `26bb8d64a`). MyPaint GPL corpus vendored, tested, and its 2 real non-conformances found (mimetype position, missing version). `ReadMode.TOLERANT` extended (commit `77a3c0588`) — all 3 MyPaint files now load and render. Portable comparison harness built and tested against mocked producers (commit `53ac6fab4`), `EXTERNAL_EXECUTION_READY` for a GIMP-capable environment. |
| Exact remaining action | Run the harness's own documented external command (`tools/ora/producer_harness/README.md`) in an environment with GIMP installed; extend the scripted scene set to include the composite-op family beyond `svg:multiply` if broader coverage is wanted |
| Executable command | See `tools/ora/producer_harness/README.md` § "Exact external command" |
| Expected artifact | `comparison-manifest.json` (schema `ora-producer-harness/comparison-manifest@1`) |
| Completion criteria | `within_tolerance: true` for every scripted scene against a real GIMP export, from at least one genuine independent producer — narrows, does not by itself close (release gate says "at least two") |
| Responsible lane | Workstream D follow-through (external execution) |
| Human action unavoidable? | Yes, narrowly: installing/running GIMP requires an environment this sandbox does not provide — not a business/legal/credential gate, a compute-environment one |

## ORA-BASELINEASSET-001 — `SAL-ORA-OBL-52746ABC41B3E790`

| Field | Value |
|---|---|
| State | `EXTERNAL_ACCESS_REQUIRED` |
| Normative/policy source | `POL-LRA-BASELINE-ASSET-01` (family-pack policy, compiled into the contract) |
| Blocker classification | Different in kind from its 3 siblings — needs an independent **consumer** application to open and visually confirm a format-factory-**generated** asset, not a producer corpus at all |
| Work completed | Read/validate/generate/replace all built and tested. `ReadMode.TOLERANT` extension corrected this obligation's own stale "none of the 3 files load" premise (they now do) — explicitly noted as not touching this obligation's own actual gate, since loading MyPaint's files is orthogonal to a consumer opening format-factory's own output |
| Exact remaining action | Identify a permissively-licensed OR appropriately-licensed independent OpenRaster consumer application; open a format-factory-generated thumbnail/mergedimage in it; record acceptance |
| Executable command | None yet — no candidate application identified. GIMP (once installed per the Workstream D harness) could plausibly serve this role too, opening a format-factory-generated `.ora` and confirming it displays correctly — worth trying opportunistically once GIMP is available for the other 3 obligations |
| Expected artifact | A screenshot or a scripted "opened without error, thumbnail matches" GIMP batch-mode check, plus the license basis for using GIMP as the consumer |
| Completion criteria | Independent consumer opens and visually/structurally confirms a format-factory-generated asset |
| Responsible lane | Workstream D follow-through (can likely reuse the same GIMP environment once available) |
| Human action unavoidable? | Same environment constraint as the other 3 — not yet a licensing/business question since GIMP (GPL, same basis as the vendoring decision already approved) is a plausible candidate once installed |

## ORA-RENDER-001 — `SAL-ORA-OBL-A979A77370914BCA`

| Field | Value | |
|---|---|---|
| State | `EXTERNAL_EXECUTION_READY` | |
| Normative/policy source | `POL-LRA-RENDER-01` (family-pack policy, compiled into the contract — the literal source of "agrees with at least two independent producers/consumers within declared tolerances") | |
| Blocker classification | Same external evidence gate as ORA-COMPOSITE-001 | |
| Work completed | Full pixel-level renderer built (commit `1865ac15d` and follow-ons), proven against hand-computed arithmetic and this project's own corpus. MyPaint vendoring + tolerant-reader extension + portable harness, same as ORA-COMPOSITE-001 above | |
| Exact remaining action | Same external GIMP run as ORA-COMPOSITE-001 — this obligation and COMPOSITE-001 share the identical remaining lever and would be closed by the same evidence run | |
| Executable command | See `tools/ora/producer_harness/README.md` | |
| Expected artifact | Same `comparison-manifest.json` | |
| Completion criteria | Same as ORA-COMPOSITE-001 | |
| Responsible lane | Workstream D follow-through | |
| Human action unavoidable? | Same environment constraint | |

## ORA-ISOLATION-001 — `SAL-ORA-OBL-ABDDB437C86DC22F`

| Field | Value |
|---|---|
| State | `EXTERNAL_EXECUTION_READY` |
| Normative/policy source | `POL-LRA-ISOLATION-01` (family-pack policy, compiled into the contract) |
| Blocker classification | Same external evidence gate, PLUS a documented harness gap: `generate_scene.py`'s own isolation-group scripting is not yet written (GIMP's own group→`isolation` attribute mapping could not be verified without a real GIMP install to check against) |
| Work completed | Isolation semantics (declared/inferred, transparent intermediate backdrop) built and tested. fill_outlines.ora's own declared isolation groups investigated directly — all `visibility="hidden"`, so even loadable they exercise no visible isolated compositing. 2 isolation scenes added to the portable harness's own Python-side matrix (`isolated-group-with-opacity`, `non-isolated-group`) — a real design bug (both scenes using fully-opaque layers, which cannot mathematically discriminate isolated vs. non-isolated) was caught and fixed before commit. GIMP-side scripting for these 2 scenes explicitly deferred, not guessed |
| Exact remaining action | (1) Script the 2 isolation scenes in `generate_scene.py` using GIMP layer groups, verified against a real GIMP install before trusting the export; (2) run the same external comparison as the other 3 |
| Executable command | Extend `tools/ora/producer_harness/gimp_scripts/generate_scene.py`, then run the same command as ORA-RENDER-001 |
| Expected artifact | Same `comparison-manifest.json`, extended to cover the 2 isolation scenes |
| Completion criteria | Same as ORA-RENDER-001, plus isolation-scene coverage specifically |
| Responsible lane | Workstream D follow-through, with one additional scripting task before the external run |
| Human action unavoidable? | Same environment constraint, plus the GIMP-side verification step itself needs a real GIMP session to confirm the group→isolation mapping before the isolation scenes can be trusted |

---

## UBL-WRITE-001 provenance — `SAL-UBL-OBL-A480CAD1CFEA58AD`

(Split from the original `SAL-UBL-OBL-F9D5251F2302AE3A` by Workstream A;
writer functionality itself is now `implemented`, not tracked here.)

| Field | Value |
|---|---|
| State | Two independent sub-items, tracked together on this one obligation: `LICENSING_PERMISSION_REQUIRED` (2 of 36 types) + `EXTERNAL_ACCESS_REQUIRED` (the remaining 34, plus the 1 non-migratable official sample) |
| Normative/policy source | `RF-UBL-00008` (research-plane finding, `authority_class: PRODUCT_REQUIREMENT`, reviewed 2026-07-16, verdict ACCEPTED — an authorized project policy, confirmed independently by a fresh Explore agent this session) |
| Blocker classification | Provenance-only, explicitly not a writer-functionality gap (Workstream A's own split makes this precise) |
| Work completed | 55/91 types have official OASIS samples vendored and round-trip-proven (54 of 55; the 1 remaining, CommonTransportationReport, independently confirmed to be a migration-path limitation, not a writer defect, via a dedicated supplementary synthetic fixture). 36/91 types have no official example in any UBL release, exhaustively confirmed. 2 of those 36 have real-world OpenPEPPOL examples under restrictive copyright — a licensing-inquiry letter requesting permission was drafted (`reports/format-contract-layer/openpeppol-licensing-inquiry-draft.md`) |
| Exact remaining action | (1) Babar Raza sends the drafted OpenPeppol letter; if granted, vendor the 2 documents. (2) The other 34 types have no known real-world source at all — this is a standing, exhaustively-researched negative result, not an unexplored option |
| Executable command | None automatable — (1) is an outbound business communication; (2) has no further lead to chase without a new source appearing |
| Expected artifact | If (1) succeeds: 2 real OpenPEPPOL documents vendored under the granted license terms |
| Completion criteria | Official OASIS or explicitly-licensed real-world example for each of the 36 types — a bar this obligation may never fully clear if OASIS itself never publishes examples for the remaining ~34 |
| Responsible lane | Human (letter-sending) for the 2; none identified for the other 34 |
| Human action unavoidable? | Yes for the letter itself (an actual outbound communication this agent cannot send — no authenticated email tool in this session). The other 34 have no actionable next step of any kind, human or automated, until a new source is found |

---

## Reading this table

Every item above resolves to one of two shapes, matching the user's own
"reduce to either fully resolved obligations or precisely isolated,
externally executable evidence gates" instruction:

- **4 ora obligations**: technically ready, blocked only on a compute
  environment with GIMP installed — a genuinely mechanical gap, not a
  business/legal/credential one. The exact command to close it is written
  down (`tools/ora/producer_harness/README.md`); running it is the entire
  remaining task.
- **1 ubl obligation** (now precisely 2 tracked sub-questions instead of one
  conflated one): one part needs a human to send an already-drafted letter;
  the other part has been exhaustively researched and has no further lever
  to pull without a new external source appearing.

None of these five remain in an undifferentiated "blocked" state.
