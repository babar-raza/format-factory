# [Draft, not submitted] jsora: writer emits absolute ZIP member paths

**Project**: jsora
**Version**: 0.3.0 (npm, pinned)
**Component**: `src/index.js`, `_add_layer()`
**Severity**: Spec non-conformance — written `.ora` files fail strict
readers

## Reproduction

Write any multi-layer document via jsora's own public `Project`/layer
API and inspect the resulting ZIP's own member names.

## Expected result

Per the OpenRaster specification and the ZIP format's own established
convention for portable archives, layer data members should use
relative paths (e.g. `data/layer0.png`), matching every other real
OpenRaster producer this investigation examined (format-factory, GIMP,
Krita).

## Actual result

jsora's own `_add_layer()` hardcodes a **leading slash**:

```js
const new_filename = `/data/layer${self._filename_counter}.png`;
```

producing ZIP member names like `/data/layer0.png`. This is intrinsic
to the writer's own code — not a harness misunderstanding or an
alternative valid API usage. format-factory's own `ReadMode.STRICT`
correctly refuses such an archive.

## Root cause

Confirmed by direct source reading of `_add_layer()` in the pinned
0.3.0 release — a single hardcoded template-literal leading `/`, no
configuration option or alternate constructor path found that produces
relative paths instead.

## Proposed issue text

> **Title**: Layer PNG entries are written with absolute ZIP paths
> (`/data/layerN.png`), rejected by strict OpenRaster readers
>
> `_add_layer()` in `src/index.js` builds each layer's own ZIP member
> name as `` `/data/layer${self._filename_counter}.png` `` — with a
> leading slash. Per common ZIP-archive convention (and every other
> OpenRaster producer this project's own cross-implementation testing
> has examined: GIMP, Krita, this project's own writer), member paths
> should be relative (`data/layer0.png`). Strict OpenRaster readers
> that reject absolute paths (a reasonable defense against zip-slip-
> style path traversal) will refuse files jsora produces. Suggested
> fix: drop the leading `/` in the template literal.
