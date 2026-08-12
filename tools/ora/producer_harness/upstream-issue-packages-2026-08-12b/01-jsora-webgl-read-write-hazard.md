# [Draft, not submitted] jsora: multi-layer rendering produces corrupted output (WebGL read/write-same-resource hazard)

**Project**: jsora
**Version**: 0.3.0 (npm, pinned)
**Component**: `src/index.js` / `render.js`, `render_to_canvas()` and its
own progressive-compositing loop
**Severity**: Correctness — any scene with 2+ layers renders garbage

## Reproduction (one command)

Using the exact evidence already gathered and committed in this
repository at `tools/ora/producer_harness/jsora/`:

```
node tools/ora/producer_harness/jsora/run_upstream_tutorial.js
```

This runs jsora's own real, unmodified upstream tutorial
(`examples/tutorial.html` at pinned GitLab commit
`12659e50727a7fbb2c6bb470f24231b2322fbad0`) via jsora's own intended
`project.load()` + `Renderer.make_merged_image()` workflow — no
format-factory fixtures, no adaptation of jsora's own code.

## Expected result

Per jsora's own documented workflow and the OpenRaster spec's own
compositing model: a rendered canvas showing the correctly-composited
multi-layer scene (each layer's own real pixel content, correctly
ordered and blended).

## Actual result

Visibly corrupted/garbled canvas output — see
`tools/ora/producer_harness/jsora/evidence-2026-08-12b/upstream-tutorial-render.png`
(committed, real screenshot from the real upstream tutorial run).

## Root cause (confirmed, not hypothesized)

`render_to_canvas()` binds every GPU.js kernel to a single shared WebGL
canvas/context (`self.gpu = new gpujs.GPU({canvas, context: gl})`), and
its own progressive-compositing loop
(`canvas = self._render_two(canvas, rendered_group, current_group)`)
repeatedly re-reads that SAME canvas as a texture input while a kernel is
simultaneously configured to render new output back into it — a
read/write-same-resource hazard, undefined behavior per the
WebGL2/OpenGL ES specification.

Confirmed via 4 independent lines of evidence (full detail in
`tools/ora/producer_harness/jsora/ROOT-CAUSE-jsora-upstream-defect-2026-08-12b.md`):

1. Direct reading of `render.js`'s own kernel-binding and compositing
   loop.
2. `page.addInitScript()`-based instrumentation of
   `document.createElement`/`getContext`/`drawImage`/`texImage2D`/
   `readPixels`/`viewport` (injected before jsora's own bundle loads,
   zero jsora bytes touched) — decisive trace line:
   `texImage2D glcanvas=canvas0 source=canvas0(32x32)`.
3. A diagnostic-only one-byte patch of an unrelated typo
   (`svr:src-over` → `svg:src-over` in the minified bundle) produced
   byte-identical garbled output, disproving that hypothesis before
   accepting the WebGL-hazard explanation.
4. jsora's own real, unmodified upstream tutorial reproduces the same
   corruption class using jsora's own intended workflow (this package's
   own reproduction command above).

Single-opaque-full-canvas-layer scenes are unaffected because the
Normal/Source-Over blend formula becomes algebraically independent of
`backdrop` when the upper layer is fully opaque across the whole canvas
— masking the hazard's garbage/stale backdrop content mathematically.
This explains why simple single-layer round-trips can appear correct
while multi-layer scenes reliably corrupt.

## Proposed issue text

> **Title**: Multi-layer rendering produces corrupted output — WebGL
> read/write-same-resource hazard in `render_to_canvas()`
>
> `render_to_canvas()`'s progressive-compositing loop repeatedly reads
> the shared output canvas as a texture input (via `texImage2D`) while a
> GPU.js kernel bound to that same canvas/context is configured to write
> new output back into it in the same pass. This is undefined behavior
> per the WebGL2 spec (reading and writing the same resource in one
> draw/dispatch). Reproducible with the project's own `examples/
> tutorial.html` using any 2+-layer `.ora` file — the merged output is
> visibly garbled rather than showing the correctly-composited scene.
> Single fully-opaque top-layer scenes mask the bug because Source-Over
> compositing becomes independent of the (corrupted) backdrop in that
> case, which may explain why this has not been caught by simpler
> smoke tests. Suggested fix direction: render each compositing step to
> a fresh (or ping-ponged) offscreen canvas/texture rather than reading
> back from the same resource a kernel is writing to.
