# ORA-COMPOSITE-001 candidate ledger — bounded discovery (2026-08-12, fourth continuation)

Directive Section 8. Deduplicated ledger of every candidate evaluated this
cycle, beyond the three already covered in their own dedicated docs
(`jsora/ROOT-CAUSE-jsora-upstream-defect-2026-08-12b.md`,
`ora-js-candidate-audit-2026-08-12b.md`,
`gegl/GEGL-CANDIDATE-AUDIT-2026-08-12b.md`). Discovery method: exact
literal-identifier source-code search (`svg:plus`, `svg:dst-atop`,
`composite-op`, `stack.xml`, `application/x-openraster`,
`image/openraster`) via `gh api search/code`, per directive Section 8 —
not marketing pages. Drawpile, Pinta, Scribus, and MyPaint were NOT
re-run, per the user's own explicit standing constraint; `mypaint/mypaint`
and `dopeyanimation/dopey` (an early MyPaint fork, same lineage) hits from
these searches were excluded on sight for that reason, not re-evaluated.

| candidate | repo | license | maintenance | ORA I/O | operation coverage | lineage | verdict |
|---|---|---|---|---|---|---|---|
| **PyShop** | `SysAdminDoc/PyShop` (`pyshop/core/ora.py`) | unspecified | active (pushed 2026-08-10, 3 stars, tiny personal project) | real writer, own `stack.xml` generation | 9 blend functions only (`BLEND_TO_ORA` dict) — **zero** Porter-Duff operators (svg:plus, dst-in, dst-out, src-atop, dst-atop all absent), zero nonseparable blends, no hard-light/soft-light | independent of jsora/pyora/GIMP/Krita (fresh small project) | **REJECTED** for this obligation's priority gap — cannot represent svg:plus (the zero-producer operation) or any of the 5 Porter-Duff operators; only duplicates already-covered blend-function evidence |
| **PhotoDemon** | `tannerhelland/PhotoDemon` (`Classes/pdOpenRaster.cls`) | permissive (well-known real desktop app, VB6/.NET, tannerhelland) | active | real reader AND writer | Reader: `GetBlendModeFromSVGOp` explicitly marks all 5 Porter-Duff operators `"unsupported blend mode"` and silently falls back to `BM_Normal` — does not correctly render any of the 5 Porter-Duff operations. Writer: same 5 cases commented out. **However**, both the reader (`Case "svg:hue"/"svg:saturation"/"svg:color"/"svg:luminosity"`, lines 654-666) and the writer (`GetSVGOpFromBlendMode`, lines 727-733) implement all 4 nonseparable blend functions as live, non-commented code — confirmed by re-reading the exact line ranges, not inferred from the Porter-Duff finding. | independent | **SPLIT VERDICT, corrected from an earlier over-broad rejection**: REJECTED for `svg:plus` and the 4 Porter-Duff operators (cannot represent them, same structural gap as ora.js/GIMP/Krita). **NOT YET PURSUED** (not rejected) as a potential SECOND producer for `svg:hue`/`svg:saturation`/`svg:color`/`svg:luminosity` — 4 of the 10 single-producer operations. Source-level capability is real; native-export/consumer-render container work was not attempted this cycle because PhotoDemon is a VB6/.NET Windows desktop application, a materially harder automation target than the Linux CLI/container tools used for every other candidate this session — genuinely out of scope for this cycle's own remaining time, not dismissed on the merits. Flagged explicitly as unfinished technical-exhaustion work, not folded into "exhausted" for those 4 operations. |
| **pyora** (via LayeredImage) | `gitlab.com/inklabapp/pyora` | MIT | active (last activity 2025-07-12) | real reader/writer, delegated to by `FHPythonUtils/LayeredImage` | Exposes all `composite_op` strings including all 5 Porter-Duff — but see lineage | **NOT independent**: npm registry confirms jsora's own package author/maintainer is `InkLab` / `inklabapp@gmail.com` — the exact same organization as pyora's own GitLab namespace `inklabapp`. Same author's two ports (JS + Python) of the same underlying design. | **REJECTED on lineage** per directive Section 8's explicit instruction not to treat same-author ports as independent, before any container/render work was attempted |
| **blendmodes** (`FHPythonUtils/BlendModes`, PyPI `blendmodes`) | `github.com/FHPythonUtils/BlendModes` | MIT | active (PyPI version `2025`) | **none** — pure pixel-math library, no ORA container awareness at all (same non-producer classification as GEGL, decided up front) | `destin`/`destout`/`srcatop`/`destatop` implement the 4 non-Lighter Porter-Duff operators with explicit Porter-Duff-coefficient docstrings (`Fa=0; Fb=as` etc.); `additive` exists as an RGB blend function name but is NOT wired into the module's own special-cased `alphaFunc` dict, so `BlendType.ADDITIVE` (svg:plus) falls through to the generic Source-Over alpha formula instead of the correct clamped-additive one — a real, disclosed bug distinct from GEGL's own (GEGL's plus.c is correct; blendmodes' own ADDITIVE alpha handling is not) | credited lineage: "Paul Jewell (2019), implementing blending from the Open Raster Image Spec" — independent of jsora/pyora (InkLab), GEGL (GNOME), GIMP, Krita, and format-factory | **ACCEPTED as `REFERENCE_ORACLE_ONLY`** for `svg:dst-in`, `svg:dst-out`, `svg:src-atop`, `svg:dst-atop` only. Installed via real `pip install blendmodes` (PyPI, not vendored/reimplemented) and run against the established discriminating fixture: all 4 produce pixel-exact matches with format-factory/`composite_oracle.py`/GEGL. **EXCLUDED for `svg:plus`** — its own real Source-Over-alpha bug there means it cannot corroborate that operator (though it independently reinforces this whole investigation's own finding that Lighter/svg:plus's additive-alpha semantics are an easy, recurring mistake across unrelated codebases: this project's own former bug, GIMP's own semantic mismatch, and now blendmodes'). |

## Net effect on Tier-C-relevant evidence (directive Section 11 preparatory note, not itself a policy determination)

For `svg:dst-in`, `svg:dst-out`, `svg:src-atop`, `svg:dst-atop`: TWO
independent, differently-authored, non-format-factory implementations of
the underlying compositing formula (GEGL and blendmodes) now agree with
format-factory pixel-exactly, in addition to this project's own
independently-structured `composite_oracle.py`. This is the strongest
evidentiary position any of the 11 deficient operations has reached this
cycle.

For `svg:plus`: ONE independent implementation (GEGL) agrees pixel-exactly.
blendmodes was evaluated and found to have its own unrelated defect for
this specific operator, so it cannot serve as a second confirming
reference here — disclosed, not hidden, per directive Section 5's "avoid
carrying speculative explanations" instruction applied to evidence
selection as well as root-causing.

For `svg:overlay`/`svg:soft-light`: GEGL was found defective for this
family (see its own audit doc) and is excluded; no second reference
oracle identified this cycle.

No claim of PRODUCER status is made for GEGL or blendmodes anywhere in
this ledger — both are pure compositing-math libraries with zero
OpenRaster-container awareness, classified `REFERENCE_ORACLE_ONLY` per
this project's own already-established independent-producer policy
interpretation, decided before any container/install work per directive
Section 9's own instruction to reject early when a candidate cannot
qualify even in principle for the role being evaluated.

## Honest exhaustion status by operation (for Section 11's own gating question)

Technical exhaustion is **not uniform** across the 11 deficient
operations and must not be reported as if it were:

- `svg:plus`: **fully exhausted**. jsora root-caused as a genuine
  upstream defect (not recovered); ora.js, PyShop, PhotoDemon, pyora all
  rejected specifically for this operator; blendmodes evaluated and
  found to have its own unrelated bug here; GEGL confirms
  format-factory as the sole independent formula reference. No further
  known candidate remains unexamined.
- `svg:dst-in`/`svg:dst-out`/`svg:src-atop`/`svg:dst-atop`: **strong but
  not fully exhausted**. Same rejections as svg:plus for the new
  candidates found this cycle, but each now has TWO independent
  reference-oracle confirmations (GEGL, blendmodes) beyond the existing
  single producer. Still literally "single producer" under the current
  policy's own producer/consumer distinction.
- `svg:hue`/`svg:saturation`/`svg:color`/`svg:luminosity`: **not
  exhausted** — PhotoDemon is a real, live, source-confirmed candidate
  for a second producer here, explicitly not yet attempted (see its own
  ledger row above). This cycle's own work does not justify treating
  these 4 operations as technically exhausted.
- `svg:overlay`/`svg:soft-light`: unchanged from before this cycle — 1
  producer each, no new reference-oracle evidence gained (GEGL was
  tried and found itself defective for this family).

Any Section 11 policy determination reached this cycle should scope
itself accordingly — `svg:plus` can be argued on a full-exhaustion
record; the others cannot yet, without either pursuing PhotoDemon or
explicitly accepting a lower evidentiary bar for "exhausted" than
svg:plus received.
