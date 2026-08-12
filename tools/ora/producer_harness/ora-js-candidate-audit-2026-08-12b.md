# `ora.js` (zsgalusz) — source/lineage audit and rejection

Per this session's own continuation directive §7: jsora's own README
explicitly references `ora.js` (by name) as a library its own author
considered and rejected before writing jsora, "due to perceived
limitations in layer/group structure support and maintenance status."
Evaluated here directly against primary sources, not taken on the
prior author's own word.

## Identity (GitHub API, fetched directly)

- Repository: `github.com/zsgalusz/ora.js`
- Description: "A JavaScript library for OpenRaster images"
- Created: 2013-07-27; **last code push: 2013-08-20** — over 12 years
  stale as of this session's own current date (2026-08-12)
- License: LICENSE file fetched and read directly — the body text is
  **verbatim standard MIT license** (permission grant, "AS IS" warranty
  disclaimer). GitHub's own automatic license detector reports
  `"Other"/NOASSERTION` rather than `MIT`, almost certainly because the
  copyright line's own author name contains a non-ASCII diacritic
  ("Zsuzsanna G\xfclusz" — the raw fetch shows a literal encoding-
  mangled byte) that breaks the detector's exact-match heuristic — the
  license terms themselves are unambiguous MIT, not actually ambiguous.
- Runtime: browser JavaScript, vanilla ES5, no build step, no external
  runtime dependency framework (vendors its own `zip.js`/`deflate.js`/
  `inflate.js`/`blender.js` directly in-repo rather than depending on
  jszip or gpu.js)
- 4 stargazers, 2 forks, 0 open issues

## Capability audit (direct source reading, not inferred)

Fetched `ora-blending.js` (the file name itself signals this is the
compositing implementation) directly via GitHub's raw content endpoint
and read it in full.

**Its own `self.blending` export object, quoted exactly:**
```js
self.blending = {
    normal: sourceOverFilter, multiply: multiplyFilter, screen: screenFilter,
    overlay: overlayFilter, dodge: dodgeFilter, burn: burnFilter,
    darken: darkenFilter, lighten: lightenFilter, plus: plusFilter,
    difference: differenceFilter, hardLight: hardLightFilter, softLight: softLightFilter,
    'svg:src-over': sourceOverFilter, 'svg:multiply': multiplyFilter,
    'svg:screen': screenFilter, 'svg:overlay': overlayFilter,
    'svg:color-dodge': dodgeFilter, 'svg:color-burn': burnFilter,
    'svg:darken': darkenFilter, 'svg:lighten': lightenFilter,
    'svg:plus': plusFilter, 'svg:difference': differenceFilter,
    'svg:hard-light': hardLightFilter, 'svg:soft-light': softLightFilter,
    //'svg:color'
    //'svg:luminosity'
    //'svg:hue'
    //'svg:saturation'
    blend: applyBlending
};
```

**Finding 1 — the 4 non-separable blend functions are explicitly
commented out, not implemented.** `svg:color`, `svg:luminosity`,
`svg:hue`, `svg:saturation` appear only as commented-out lines — the
author's own disclosed to-do list, never completed (matches the 2013
abandonment date).

**Finding 2 — zero Porter-Duff-operator support, not even attempted.**
`svg:dst-in`, `svg:dst-out`, `svg:src-atop`, `svg:dst-atop` do not
appear anywhere in this file, commented or otherwise. `ora.js` has no
Porter-Duff-operator concept at all — the same structural limitation
already confirmed for GIMP (both 2.10 and current 3.x) this session.

**Finding 3 — `svg:plus` is present but cannot provide correct Porter-
Duff Lighter evidence, for a precisely identified architectural reason.**
`applyBlending()`'s own outer compositing wrapper is quoted in full
above: `blendAlpha = srcA + dstA - dstA * srcA` — this is the standard
**Source-Over** alpha-compositing formula, applied **unconditionally**,
regardless of which named `filter` function is selected. Only the
per-channel *color* formula changes between `normal`/`multiply`/`plus`/
etc.; the *alpha* channel is always computed via Source-Over. The true
Porter-Duff Lighter formula requires `alpha_o = min(alpha_s + alpha_b,
1.0)` (additive, not Source-Over's `alpha_s + alpha_b·(1−alpha_s)`) —
`ora.js`'s own architecture has no path to this, the same class of
defect already found and disclosed for GIMP's own layer-mode system
this session (a "blend function" selector with no accompanying
Porter-Duff-operator selector).

## Lineage independence

No code sharing with jsora confirmed: different runtime approach
entirely (vanilla ES5 vs. jsora's gpu.js/WebGL2 kernel compositor),
different vendored dependencies (`zip.js`/`deflate.js`/`inflate.js` vs.
`jszip`), different author. Genuinely independent implementation in
principle — rejected on capability grounds, not lineage grounds.

## Verdict: REJECTED, before any container work, per directive §7 point 6

`ora.js` cannot represent **any** of this obligation's own 11 remaining
deficient operations:
- The 4 missing Porter-Duff operators (`svg:dst-in`/`svg:dst-out`/
  `svg:src-atop`/`svg:dst-atop`): not implemented at all.
- `svg:plus` (Lighter): implemented, but architecturally incapable of
  the correct additive-alpha formula — would only ever reproduce the
  same class of Source-Over-alpha mismatch already confirmed for GIMP.
- The 4 non-separable operations (`svg:hue`/`svg:saturation`/
  `svg:color`/`svg:luminosity`): explicitly commented out, unimplemented.

Every operation `ora.js` **does** correctly attempt (`multiply`,
`screen`, `overlay`, `color-dodge`, `color-burn`, `darken`, `lighten`,
`difference`, `hard-light`, `soft-light`, `src-over`/Normal) is an
operation this project **already has coverage for** — 9 with two
independent producers already, `overlay`/`soft-light` with Krita-only
coverage already. A fully working `ora.js` harness would therefore add
**zero new coverage** even in the best possible case. No container was
built; this rejection is decided entirely from the real, primary source.
