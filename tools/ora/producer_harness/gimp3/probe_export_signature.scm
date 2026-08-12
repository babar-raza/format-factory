; Probe file-openraster-export/load's own real PDB argument signature in
; GIMP 3.x's new GimpExportProcedure/GimpLoadProcedure API, rather than
; assuming the classic 2.10-style (run-mode image drawable filename
; raw-name) signature still applies.
(let* ((image (car (gimp-image-new 4 4 RGB)))
       (layer (car (gimp-layer-new image "l" 4 4 RGBA-IMAGE 100 LAYER-MODE-NORMAL))))
  (gimp-image-insert-layer image layer 0 -1)
  (gimp-context-set-foreground (list 200 30 30))
  (gimp-image-select-rectangle image CHANNEL-OP-REPLACE 0 0 4 4)
  (gimp-drawable-edit-fill layer FILL-FOREGROUND)
  (gimp-selection-none image)
  (file-openraster-export RUN-NONINTERACTIVE image "/out/probe-export.ora")
  (gimp-image-delete image))
(gimp-message "export probe done")
(gimp-quit 0)
