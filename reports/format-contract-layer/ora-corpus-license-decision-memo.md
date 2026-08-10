# ORA Independent-Producer-Corpus: License Decision Memo

**Status:** Decision-ready. Awaiting business/legal authority (not resolvable by an agent).
**Affects:** SAL-ORA-OBL-2CC875865800D528 (ORA-COMPOSITE-001), SAL-ORA-OBL-52746ABC41B3E790 (ORA-BASELINEASSET-001), SAL-ORA-OBL-A979A77370914BCA (ORA-RENDER-001), SAL-ORA-OBL-ABDDB437C86DC22F (ORA-ISOLATION-001) — 4 of ora's 6 remaining unresolved obligations.
**Prepared:** 2026-08-10, via a dedicated research pass (multi-agent workflow, full repository-tree scans, not web-search summaries).

## Bottom line

No independently-produced, permissively-licensed OpenRaster test corpus exists anywhere that was found, after an exhaustive search. The only route to a corpus rich enough for the blocked obligations (multi-layer, blend-mode, isolated-group compositing) is accepting GPL-licensed MyPaint fixtures. This is confirmed, not assumed — see Section A for exact evidence.

## A. What actually exists, verified by direct repository inspection

**MyPaint** (`github.com/mypaint/mypaint`, full recursive tree scan, exhaustive):
- `tests/bigimage.ora` — 128,487 bytes
- `tests/fill_outlines.ora` — 188,920 bytes
- `tests/smallimage.ora` — 64,316 bytes
- Plus two "known-correct" composited reference PNGs used by MyPaint's own rendering tests: `tests/correct_docPaint_alpha.png`, `tests/correct_docPaint_flat.png`

These are consumed by MyPaint's own `tests/test_rendering.py` and `tests/test_compositeops.py` — the same category of validation ora's own blocked obligations need.

**Krita** (`github.com/KDE/krita`, full recursive tree scan, 13,315 entries, exhaustive): **zero** `.ora` files committed anywhere. Krita's own OpenRaster plugin test (`plugins/impex/ora/tests/KisOraTest.cpp`) uses synthetic/generated scenarios, not a bundled sample. There is no "Krita sample" to vendor — MyPaint is the only real candidate.

## B. The actual license text

MyPaint `COPYING` (repo root): GNU GPL v2.
MyPaint `Licenses.dep5` (machine-readable copyright manifest): `Files: * / License: GPL-2+` — no exception for the `tests/` directory anywhere in that file. MyPaint's own copyright holders have explicitly asserted these specific files fall inside the GPL boundary.

## C. What vendoring would and would not mean (plain language, not a recommendation)

1. **Does GPL reach a data file, not just code?** Arguable in the abstract, but MyPaint's own `Licenses.dep5` removes the ambiguity for these specific files: `Files: *` with no test-data carve-out means MyPaint's own maintainers consider these bytes GPL-covered. format-factory cannot rely on a "GPL only covers code" argument for these three files specifically, because MyPaint has already taken the opposite position.
2. Vendoring these files into format-factory's own repository as committed test fixtures is a "distribution" of GPL-2+-covered material. For **static, non-executable binary test-fixture files never linked into, compiled with, or shipped inside format-factory's own product artifacts** (wheels, NuGet packages, installers) — used only internally for CI pixel-diff assertions — the redistribution obligation most plausibly scopes to *those specific files* (keep MyPaint's copyright notice + GPL-2.0 text alongside them), not to "GPL-izing" the surrounding commercial-track product. GPL copyleft is triggered by combining/linking/deriving works from GPL *code* — static test data in a `tests/` directory the product never compiles against is a materially different situation from linking a GPL library into the shipped product.
3. That is a risk judgment, not a certainty — there is no case law directly on point. The answer could depend on operational details (are the fixtures ever included in a published package/installer, referenced in generated example output shipped to customers, or otherwise redistributed beyond internal CI?). This is why it needs a human decision-maker with legal authority.
4. **What it would NOT automatically mean:** it would not require format-factory's own commercial product source to become GPL-licensed. That concerns combining/linking/deriving GPL *code* into a work, not having GPL-covered *bytes* sitting in a tests/ folder the product never compiles against or ships.

**Lowest-risk shape, if the GPL path is chosen:** fixtures live in a clearly separated, clearly labeled directory (e.g. `tests/fixtures/third-party-gpl-mypaint/`), never packaged or shipped inside the product's distributable artifacts, used only for internal CI pixel-diff assertions, with MyPaint's copyright notice + GPL-2.0 text checked in alongside them. Still a judgment call requiring sign-off, not a guarantee against all risk.

## D. Permissively-licensed alternatives found this session (context, not a substitute)

Three small `.ora` fixtures with unambiguous permissive licenses were found in independent third-party projects — none known before this search:
- `image-rs/image-extras` — `tests/images/ora/layer.ora` (Apache-2.0 OR MIT, author explicitly states "I created the test image and license it to match image-extras" — self-authored, not extracted from Krita/MyPaint). **Caveat:** the decoder this fixture exercises only extracts the embedded flattened PNG — does not validate multi-layer compositing, blend modes, or isolated-group rendering, the exact things the blocked obligations need.
- `OliverVea/Olve.OpenRaster` — `Olve.OpenRaster.Test/map_1.ora` (MIT). Has real layers and groups (structurally richer). **Caveat:** provenance/creating-tool unstated by the author — can't rule out this being an unattributed export from a GPL tool.
- `zsgalusz/ora.js` — `tests/testdata/oratest.ora` (MIT, 2013). Small, old, single fixture, provenance unstated.

None of these, alone or combined, substitute for a real rendering/compositing corpus at the depth needed. Worth pulling in as supplementary smoke-test fixtures regardless of the GPL decision (unambiguous licenses), but they do not resolve the underlying gap.

Two systematic format-corpus aggregators (`openpreserve/format-corpus`, CC0; `ForAllSecure/starter-testsuites`, Apache-2.0, covers 100+ formats) were checked exhaustively and contain no OpenRaster material — this avenue is now closed with high confidence, not merely unsearched. Permissively-licensed `.ora`-producing applications (Pinta/MIT, ImageMagick/permissive) were confirmed via full-tree scans to ship no bundled `.ora` corpus of their own.

The `openraster/ora-spec` GitHub org (2 repos, no LICENSE file, all-rights-reserved by default) was re-confirmed to contain no test corpus, matching the finding already made earlier this session.

## E. The decision this needs

A human with business/legal authority needs to decide whether format-factory (commercial track) may:
- **(a)** vendor MyPaint's `tests/bigimage.ora`, `tests/fill_outlines.ora`, `tests/smallimage.ora` (and the two reference PNGs) as GPL-2+-covered test fixtures, isolated and never shipped in product artifacts, per the shape in Section C; or
- **(b)** decline the GPL path, and treat the corpus gap as remaining blocked pending either an original, clean-IP multi-layer/multi-blend-mode/isolated-group `.ora` corpus built in-house, or some other source not yet found.

No agent action can make this decision. This memo exists to make it fast and informed when someone with the authority to make it is available.
