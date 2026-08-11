# Third-party GPL-2+ OpenRaster fixtures — MyPaint

**These 3 files are NOT format-factory project content.** They are vendored,
unmodified, third-party test fixtures from the MyPaint painting application,
used only as an independently-produced OpenRaster corpus for interoperability
and archive-conformance testing.

Vendoring approved by the repository owner (Babar Raza) on 2026-08-10, via
explicit structured approval, scoped exactly to this shape: isolated,
clearly-labeled directory; never shipped inside product distribution
artifacts; used only for internal test assertions. See
`reports/format-contract-layer/ora-corpus-license-decision-memo.md` for the
full research and decision record.

## Source

- Upstream project: MyPaint (<https://mypaint.org/>, <https://github.com/mypaint/mypaint>)
- Files acquired from: `github.com/mypaint/mypaint`, path `tests/`
- Pinned commit: `35aa9d33cd3deba6cafea6d8fc901b5a1d161ceb` (master, as of 2026-08-10)
- Acquisition method: `gh api "repos/mypaint/mypaint/contents/tests/<file>?ref=<pinned-commit>"`,
  base64-decoded, written byte-for-byte with no modification.

## Files

| File | Bytes | SHA-256 |
|---|---|---|
| `bigimage.ora` | 128487 | `108e04c36df1e84ca0f13dc35cbd86d92a23f4fb5862cf1c2cae46d309555f83` |
| `fill_outlines.ora` | 188920 | `3909051829882337597e2a4f430c5dea3a179f9c9c97cbdb4e9e9e4a9d5fb09f` |
| `smallimage.ora` | 64316 | `8eab0f0fe41fcb10b851125e7e1db0afa5dd9c428733d978b0c0a23f11a1c702` |

Byte counts match the independent research memo's own cited figures exactly
(`ora-corpus-license-decision-memo.md`, Section A).

## License

Per MyPaint's own machine-readable `Licenses.dep5` (Debian DEP5 format),
fetched from the same pinned commit:

```
Files: *
Copyright: Copyright 2005-2016 Martin Renold and the MyPaint Development Team
License: GPL-2+
```

MyPaint's own maintainers declare a blanket `Files: *` copyright/license
statement with **no test-data carve-out** — these specific files under
`tests/` are explicitly GPL-2+ covered, not merely "code." The full GPL-2.0
license text is vendored alongside this notice as `LICENSE-GPL-2.0.txt`
(fetched from MyPaint's own `COPYING` file at the same pinned commit).

## Scope boundary (binding)

- These files live under `tests/python/ora/fixtures/` — outside
  `src/python/ora/src/`, the only tree `src/python/ora/pyproject.toml`'s
  `[tool.setuptools.packages.find]` includes (`where = ["src"]`,
  `include = ["format_factory.ora*"]`). `src/python/ora/MANIFEST.in` does not
  reference this directory either. They are therefore excluded from both the
  wheel and sdist by construction, not by an added exclusion rule.
- Used only for internal pytest assertions in
  `tests/python/ora/test_obligation_container_and_mimetype.py` and
  `tests/python/ora/test_obligation_stack_and_document.py`.
- Never redistributed as part of any format-factory release artifact.

## What was actually found when these files were tested (2026-08-10)

None of the 3 files load successfully through format-factory's own
spec-conformant OpenRaster reader — each fails a different, genuine,
independently-verified real-world conformance check before rendering is ever
reached (confirmed via Python's `zipfile.ZipFile.namelist()` true
central-directory order, not `unzip -l`'s display order, which does not
necessarily reflect it):

- `bigimage.ora`: first true archive member is `data/`, not `mimetype`.
- `fill_outlines.ora`: first true archive member is `Thumbnails/`, not
  `mimetype`.
- `smallimage.ora`: loads past the container check (its `mimetype` member
  genuinely is first), but its `stack.xml` root `<image>` element omits the
  required `version` attribute.

This means the original hope for this vendoring effort — a pixel-level
render/composite comparison against a real independent producer, closing or
narrowing ORA-RENDER-001 / ORA-COMPOSITE-001 / ORA-ISOLATION-001 /
ORA-BASELINEASSET-001's shared "agrees with at least two independent
producers" release gate — is **not achieved by these files**: none of them
can be rendered by a strictly spec-conformant reader at all. This is
disclosed honestly rather than worked around by loosening container/stack
validation to fit this specific corpus (which would weaken already-verified,
already-implemented archive-safety obligations for the sake of one
convenience corpus).

What these files *do* provide, and what they are used for instead: genuine,
real-world (not hand-crafted synthetic) evidence that format-factory's
strict conformance checks correctly identify and reject actual non-conformant
output from a real, independently-developed, widely-used OpenRaster-producing
application — strengthening the existing archive/stack validation obligations
(already `implemented`) with a real adversarial input class the synthetic
fixtures alone did not cover. See the companion tests in
`test_obligation_container_and_mimetype.py` and
`test_obligation_stack_and_document.py`.

## Update (2026-08-11, FF6 Track 2)

`ReadMode.TOLERANT` was extended to cover both defect classes found above
(mimetype-not-first-member; missing `version` attribute) — all 3 files now
load and render successfully under `ReadMode.TOLERANT`, while `STRICT` mode
remains byte-for-byte unchanged (every finding above still holds under
`STRICT`). See `test_obligation_compatibility_reader.py`.

This does **not** change the finding above regarding pixel-level render
comparison: only `fill_outlines.ora` embeds a `mergedimage.png`, and it is
64×64 pixels — a thumbnail, not the document's real 3456×3008 canvas — so it
still cannot serve as full-resolution ground truth. `bigimage.ora` and
`smallimage.ora` have no `mergedimage.png` at all. The render/composite/
isolation release gate's own "at least two independent producers" text
remains unmet by these 3 files specifically. A real independent producer
(GIMP) was separately acquired and executed this same session, achieving
one full pixel-comparison producer via a controlled scene matrix instead —
see `tools/ora/producer_harness/PROVENANCE-gimp-execution-2026-08-11.md`.
