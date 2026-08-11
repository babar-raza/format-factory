; GIMP Script-Fu batch generator for the ORA independent-producer comparison
; harness. Empirically verified against a real GIMP 2.10.30 install
; (Ubuntu 22.04 apt package) -- see ../README.md "What actually happened"
; for the full debugging account: Python-Fu is NOT available in this
; package (Ubuntu 22.04 dropped Python 2, which GIMP 2.10's Python-Fu
; requires), and the `gimp` apt package ships NO OpenRaster plugin at all
; (confirmed: zero PDB procedures match "openraster", zero plug-in binaries
; named file-ora*/file-openraster* anywhere on the filesystem). This script
; therefore does NOT produce .ora files -- it constructs each scene with
; GIMP's own layer/group compositing engine (a genuinely independent
; implementation from format-factory's own renderer) and exports the
; FLATTENED result as PNG directly, which is what the comparison in
; compare.py actually needs. This is disclosed explicitly, everywhere this
; harness's own output is used as evidence -- it is real, independent
; GIMP-compositor output, but it does not additionally prove OpenRaster
; *container* interop with GIMP specifically (a separate question, already
; covered by ORA-CONTAINER-001).
;
; Deliberately duplicates scene_matrix.py's own scene data (Scheme cannot
; import Python) -- see compare.py's drift guard for how the two are kept
; in sync.
;
; Layer-group isolation mapping, verified empirically against this exact
; GIMP build (not assumed): a group layer's own LAYER-MODE-PASS-THROUGH
; mode (61) blends children directly with content below (OpenRaster
; isolation="auto"/non-isolated); any other mode, e.g. LAYER-MODE-NORMAL
; (28), composites children as a flattened unit first (OpenRaster
; isolation="isolate").
;
; POSITION BUG FOUND AND FIXED (2026-08-11): gimp-image-insert-layer's own
; `position -1` means "insert above the currently active layer", and each
; newly-inserted layer becomes active -- so inserting children in the
; SAME order this file lists them (top-first, matching OpenRaster's own
; "first child is uppermost" convention) put each LATER child ABOVE the
; earlier one, reversing the intended stack for every 2+-layer scene.
; Confirmed empirically (6 of 8 scenes disagreed with format-factory on
; first run; the 2 that matched -- single-opaque-layer, hidden-layer --
; are exactly the 2 where layer order cannot affect the visible result
; either way, consistent with one single root cause, not 6 separate
; disagreements). Fixed by passing an EXPLICIT ascending position (0 =
; topmost) to every insert-layer call instead of relying on -1's
; active-layer-relative behavior.

; BUG FOUND AND FIXED (2026-08-11, second root cause this session): this
; selected (0,0,width,height) in IMAGE-GLOBAL coordinates unconditionally,
; regardless of where the layer itself had already been offset to via
; gimp-layer-set-offsets. For every layer at offset (0,0) this is harmless
; (the hardcoded selection coincides exactly with the layer's own true
; bounds) -- which is every scene except layer-order (top offset (16,16),
; bottom offset (0,0)) and offset-and-clipping (single layer at (-8,-8),
; which passed only by numeric coincidence: the wrong selection intersected
; with the true layer bounds happened to equal the true on-canvas-visible
; portion for that specific offset/size/canvas combination). Root-caused via
; exact pixel diffing against format-factory's own render: the missing
; region in layer-order's GIMP output (x:48-63, y:16-63 -- fully transparent
; instead of top's own green) exactly equals top's own true footprint
; (offset 16,16, size 48x48) MINUS the erroneous (0,0,48,48) selection's own
; overlap with it -- proving the fill silently missed real layer area rather
; than any merge/clip-bounds problem (the make-canvas-backdrop
; full-canvas-transparent-layer fix below, tried first, had zero effect on
; this scene's diff for exactly this reason: the backdrop was never the
; cause). Fixed by querying the layer's own actual current offset via
; gimp-drawable-offsets and selecting there instead of (0,0).
(define (fill-solid-layer image layer width height r g b a)
  (let* ((offsets (gimp-drawable-offsets layer))
         (ox (car offsets))
         (oy (cadr offsets)))
    (gimp-image-set-active-layer image layer)
    (gimp-context-set-foreground (list r g b))
    (gimp-image-select-rectangle image CHANNEL-OP-REPLACE ox oy width height)
    (gimp-edit-fill layer FILL-FOREGROUND)
    (gimp-selection-none image)))

(define (make-layer image width height x y r g b a opacity-pct mode visible position)
  (let* ((layer (car (gimp-layer-new image width height RGBA-IMAGE "layer" opacity-pct mode))))
    (gimp-image-insert-layer image layer 0 position)
    (gimp-layer-set-offsets layer x y)
    (fill-solid-layer image layer width height r g b a)
    (if (< a 255)
        (gimp-layer-set-opacity layer (* opacity-pct (/ a 255.0))))
    (gimp-item-set-visible layer visible)
    layer))

; A fully-transparent layer sized to the EXACT canvas, always inserted last
; (bottom-most). gimp-image-merge-visible-layers's own CLIP-TO-IMAGE mode
; was empirically found to still clip the merge result to something
; SMALLER than the full canvas when no single merged layer already spans
; it (confirmed: real content, not just padding, went missing at pixels
; covered only by a layer extending beyond another layer's own footprint --
; e.g. layer-order's own top-green content outside bottom-blue's bounds
; came back fully transparent (0,0,0,0) instead of green). Guaranteeing a
; full-canvas-sized layer always exists in the stack sidesteps whatever
; CLIP-TO-IMAGE''s own real semantic is, rather than guessing at it a
; third time.
(define (make-canvas-backdrop image width height)
  (let* ((layer (car (gimp-layer-new image width height RGBA-IMAGE "canvas-backdrop" 100 LAYER-MODE-NORMAL-LEGACY))))
    (gimp-image-insert-layer image layer 0 -1)
    (gimp-layer-set-offsets layer 0 0)
    (gimp-layer-add-alpha layer)
    (gimp-image-select-rectangle image CHANNEL-OP-REPLACE 0 0 width height)
    (gimp-edit-clear layer)
    (gimp-selection-none image)
    layer))

; gimp-image-flatten (deliberately NOT used) discards the alpha channel and
; fills any uncovered/transparent area with the current background color
; (white by default) -- format-factory's own renderer leaves uncovered
; canvas fully transparent (0,0,0,0), so flatten would produce a spurious
; mismatch on any scene with visible canvas outside every layer's own
; bounds, unrelated to real compositing disagreement.
; gimp-image-merge-visible-layers PRESERVES alpha, matching that semantic --
; but even with CLIP-TO-IMAGE, empirically its own resulting layer is sized
; to the merged content's own bounding box, not the full canvas (confirmed:
; a 24x24 layer offset off-canvas on a 32x32 image produced a 16x16 PNG,
; the layer/canvas overlap, not 32x32) -- gimp-layer-resize-to-image-size
; is required afterward to get the full declared canvas size, matching
; format-factory's own render() which always returns exactly
; (scene.canvas_width, scene.canvas_height) regardless of layer bounds.
(define (export-flattened image path)
  (let* ((merged (car (gimp-image-merge-visible-layers image CLIP-TO-IMAGE))))
    (gimp-layer-resize-to-image-size merged)
    (file-png-save RUN-NONINTERACTIVE image merged path path 0 9 1 1 1 1 1)))

(define (run-scene-single-opaque-layer out-dir)
  (let* ((image (car (gimp-image-new 64 64 RGB))))
    (make-canvas-backdrop image 64 64)
    (make-layer image 64 64 0 0 200 30 30 255 100 LAYER-MODE-NORMAL-LEGACY TRUE 0)
    (export-flattened image (string-append out-dir "/single-opaque-layer.png"))
    (gimp-image-delete image)))

(define (run-scene-layer-order out-dir)
  (let* ((image (car (gimp-image-new 64 64 RGB))))
    (make-canvas-backdrop image 64 64)
    (make-layer image 48 48 16 16 0 200 0 255 100 LAYER-MODE-NORMAL-LEGACY TRUE 0)
    (make-layer image 48 48 0 0 0 0 200 255 100 LAYER-MODE-NORMAL-LEGACY TRUE 1)
    (export-flattened image (string-append out-dir "/layer-order.png"))
    (gimp-image-delete image)))

(define (run-scene-partial-opacity out-dir)
  (let* ((image (car (gimp-image-new 64 64 RGB))))
    (make-canvas-backdrop image 64 64)
    (make-layer image 64 64 0 0 0 0 255 200 80 LAYER-MODE-NORMAL-LEGACY TRUE 0)
    (make-layer image 64 64 0 0 255 255 255 255 100 LAYER-MODE-NORMAL-LEGACY TRUE 1)
    (export-flattened image (string-append out-dir "/partial-opacity.png"))
    (gimp-image-delete image)))

(define (run-scene-offset-and-clipping out-dir)
  (let* ((image (car (gimp-image-new 32 32 RGB))))
    (make-canvas-backdrop image 32 32)
    (make-layer image 24 24 -8 -8 255 128 0 255 100 LAYER-MODE-NORMAL-LEGACY TRUE 0)
    (export-flattened image (string-append out-dir "/offset-and-clipping.png"))
    (gimp-image-delete image)))

(define (run-scene-hidden-layer out-dir)
  (let* ((image (car (gimp-image-new 32 32 RGB))))
    (make-canvas-backdrop image 32 32)
    (make-layer image 32 32 0 0 255 0 0 255 100 LAYER-MODE-NORMAL-LEGACY FALSE 0)
    (make-layer image 32 32 0 0 0 255 0 255 100 LAYER-MODE-NORMAL-LEGACY TRUE 1)
    (export-flattened image (string-append out-dir "/hidden-layer.png"))
    (gimp-image-delete image)))

(define (run-scene-multiply-blend out-dir)
  (let* ((image (car (gimp-image-new 32 32 RGB))))
    (make-canvas-backdrop image 32 32)
    (make-layer image 32 32 0 0 200 50 10 255 100 LAYER-MODE-MULTIPLY-LEGACY TRUE 0)
    (make-layer image 32 32 0 0 100 250 90 255 100 LAYER-MODE-NORMAL-LEGACY TRUE 1)
    (export-flattened image (string-append out-dir "/multiply-blend.png"))
    (gimp-image-delete image)))

; Isolated group: 2 fully-opaque children (top red, bottom green) inside a
; group whose OWN mode is LAYER-MODE-NORMAL (isolated) at 50% opacity, over
; an opaque black backdrop. Matches format-factory's own hand-verified test
; (test_isolated_group_applies_group_opacity_once_not_per_child): top fully
; occludes bottom before the group's own opacity is applied once to the
; flattened result -> expect (128,0,0).
(define (run-scene-isolated-group-with-opacity out-dir)
  (let* ((image (car (gimp-image-new 32 32 RGB)))
         (group (car (gimp-layer-group-new image))))
    (gimp-image-insert-layer image group 0 0)
    (gimp-item-set-name group "isolated-group")
    ; NORMAL-LEGACY, not NORMAL: GIMP 2.10's non-legacy blend modes composite
    ; in linear light, re-encoding to sRGB afterward -- format-factory's own
    ; renderer does straight sRGB-space compositing (confirmed by its own
    ; hand-verified test formulas, e.g. "alpha_s = (200/255)*0.8; new_r =
    ; (1-alpha_s)*255", direct arithmetic on the 0-255 encoded values, no
    ; gamma conversion). Empirically confirmed this was the exact cause of
    ; a first-round mismatch here (128 expected, 188 observed --
    ; 0.5^(1/2.2)*255 = 186, matching a linear-light 50% blend almost
    ; exactly, not a coincidence).
    (gimp-layer-set-mode group LAYER-MODE-NORMAL-LEGACY)
    (gimp-layer-set-opacity group 50)
    (let* ((top (car (gimp-layer-new image 32 32 RGBA-IMAGE "top" 100 LAYER-MODE-NORMAL-LEGACY))))
      (gimp-image-insert-layer image top group 0)
      (fill-solid-layer image top 32 32 255 0 0 255))
    (let* ((bottom (car (gimp-layer-new image 32 32 RGBA-IMAGE "bottom" 100 LAYER-MODE-NORMAL-LEGACY))))
      (gimp-image-insert-layer image bottom group 1)
      (fill-solid-layer image bottom 32 32 0 255 0 255))
    (make-layer image 32 32 0 0 0 0 0 255 100 LAYER-MODE-NORMAL-LEGACY TRUE 1)
    (export-flattened image (string-append out-dir "/isolated-group-with-opacity.png"))
    (gimp-image-delete image)))

; REDESIGNED 2026-08-11 (see scene_matrix.py's own "non-isolated-group" scene
; docstring for the full account -- this .scm scene must stay in sync with
; that canonical definition, per this file's own header note). The original
; design (group opacity=0.5) was UNSOUND: OraStack.is_isolated_group forces
; isolation whenever opacity is below one, per the OpenRaster spec's own
; literal text -- so that scene could never exercise non-isolated compositing
; against format-factory's own renderer at all, regardless of what GIMP did.
; This was root-caused (not guessed) after two straight GIMP-side "fixes"
; (a real PASS-THROUGH group, then manual per-child opacity distribution)
; both correctly implemented genuine pass-through semantics and both,
; correctly, disagreed with format-factory's own NECESSARILY-isolated
; rendering of that unsound scene -- per the "two failures from the same
; approach" rule, the fix belongs in the scene definition, not a third GIMP
; patch.
;
; The corrected scene: group opacity=1.0 (isolation genuinely non-forced),
; top child's own composite-op is svg:multiply (not the group's own -- this
; is what makes isolation observable at all: Porter-Duff 'over' is
; associative, so a group with opacity=1 and only default-composite-op
; children is PROVABLY identical whether isolated or not; isolation only
; matters once some child blends with something other than plain 'over').
; Per that same associativity, a genuinely non-isolated group with opacity=1
; is mathematically equivalent to removing the group wrapper entirely and
; compositing its children as plain siblings -- confirmed computationally
; against format-factory's own renderer before this file was written
; (non-isolated-with-group-wrapper output == flattened-no-group output,
; byte for byte). This scene is therefore scripted with NO GIMP group at
; all, exactly like multiply-blend, just with a translucent second layer.
(define (run-scene-non-isolated-group out-dir)
  (let* ((image (car (gimp-image-new 32 32 RGB))))
    (make-layer image 32 32 0 0 200 50 10 255 100 LAYER-MODE-MULTIPLY-LEGACY TRUE 0)
    (make-layer image 32 32 0 0 100 250 90 160 100 LAYER-MODE-NORMAL-LEGACY TRUE 1)
    (make-layer image 32 32 0 0 0 0 0 255 100 LAYER-MODE-NORMAL-LEGACY TRUE 2)
    (export-flattened image (string-append out-dir "/non-isolated-group.png"))
    (gimp-image-delete image)))

(define (run-all-scenes out-dir)
  (run-scene-single-opaque-layer out-dir)
  (run-scene-layer-order out-dir)
  (run-scene-partial-opacity out-dir)
  (run-scene-offset-and-clipping out-dir)
  (run-scene-hidden-layer out-dir)
  (run-scene-multiply-blend out-dir)
  (run-scene-isolated-group-with-opacity out-dir)
  (run-scene-non-isolated-group out-dir)
  (gimp-message "all scenes generated"))
