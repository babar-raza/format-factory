; GIMP 3.x svg:plus spike. Fixture matches the exact discriminating
; Porter-Duff scene already committed this session (destination
; (230,60,40) alpha 153/255 at (0,0)-(20,20); source (40,120,230) alpha
; 128/255 at (12,12)-(32,32), on a 32x32 canvas -- composite_matrix.py's
; own PORTER_DUFF_SCENES / composite-porterduff-lighter.ora).
;
; Path A: native creation with GIMP 3.x's own current (non-legacy)
; Addition mode (LAYER-MODE-ADDITION=33, confirmed via
; probe_addition_modes.scm to be the exact constant file-openraster.py's
; own layermodes_map maps svg:plus to), exported through GIMP's own writer.
; KNOWN, already-confirmed GIMP 3.0.4 defect (see
; probe_export_signature.scm's own real output): the exported <image>
; element omits the required 'version' attribute -- STRICT mode correctly
; refuses it; not a format-factory or fixture defect, not patched around.
;
; Path B: import the canonical strict .ora fixture already committed this
; session, render, export PNG -- the primary test for whether GIMP 3.x's
; own rendering of svg:plus agrees with the independent oracle.

(define (fill-solid-layer image layer x y width height r g b)
  (gimp-context-set-foreground (list r g b))
  (gimp-image-select-rectangle image CHANNEL-OP-REPLACE x y width height)
  (gimp-drawable-edit-fill layer FILL-FOREGROUND)
  (gimp-selection-none image))

(define (make-layer image name x y width height r g b alpha-pct mode)
  (let* ((layer (car (gimp-layer-new image name width height RGBA-IMAGE alpha-pct mode))))
    (gimp-image-insert-layer image layer 0 -1)
    (gimp-layer-set-offsets layer x y)
    (fill-solid-layer image layer 0 0 width height r g b)
    layer))

; ---- Path A: native creation, GIMP's own non-legacy Addition mode ----
(let* ((image (car (gimp-image-new 32 32 RGB))))
  (make-layer image "dest" 0 0 20 20 230 60 40 (* 100 (/ 153.0 255.0)) LAYER-MODE-NORMAL)
  (make-layer image "src" 12 12 20 20 40 120 230 (* 100 (/ 128.0 255.0)) LAYER-MODE-ADDITION)
  (file-openraster-export RUN-NONINTERACTIVE image "/out/gimp3-native-svg-plus.ora")
  (gimp-image-delete image)
  (gimp-message "path A: native export done"))

; ---- Path B: import canonical strict .ora, render, export PNG ----
; gimp-image-merge-visible-layers (NOT gimp-image-flatten -- flatten
; destroys the alpha channel by compositing onto an opaque background
; color, which would corrupt exactly the data this spike needs to check)
(let* ((image (car (file-openraster-load RUN-NONINTERACTIVE "/out/composite-porterduff-lighter.ora")))
       (drawable (car (gimp-image-merge-visible-layers image CLIP-TO-IMAGE))))
  (file-png-export RUN-NONINTERACTIVE image "/out/gimp3-reopen-svg-plus.png")
  (gimp-image-delete image)
  (gimp-message "path B: reopen+render done"))

(gimp-message "svg:plus spike complete")
(gimp-quit 0)
