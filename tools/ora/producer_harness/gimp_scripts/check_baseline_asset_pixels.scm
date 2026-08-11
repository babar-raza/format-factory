; Workstream B3 (ORA-BASELINEASSET-001 visual-assurance amendment): load a
; real format-factory-generated mergedimage.png through GIMP's own PNG
; decoder and read back every pixel via gimp-drawable-get-pixel, so the
; comparison is against what GIMP itself decoded, not format-factory's own
; decode_png() a second time. Prints one CSV line per pixel:
; "<scene-id>,<x>,<y>,<r>,<g>,<b>,<a>".

(define (dump-pixels scene-id path width height)
  (let* ((image (car (gimp-file-load RUN-NONINTERACTIVE path path)))
         (drawable (car (gimp-image-get-active-drawable image))))
    (let loopy ((y 0))
      (if (< y height)
          (begin
            (let loopx ((x 0))
              (if (< x width)
                  (let* ((px (gimp-drawable-get-pixel drawable x y))
                         (v (cadr px)))
                    (gimp-message (string-append
                      scene-id "," (number->string x) "," (number->string y) ","
                      (number->string (vector-ref v 0)) ","
                      (number->string (vector-ref v 1)) ","
                      (number->string (vector-ref v 2)) ","
                      (if (= (car px) 4) (number->string (vector-ref v 3)) "255")))
                    (loopx (+ x 1)))))
            (loopy (+ y 1)))))
    (gimp-image-delete image)))

(dump-pixels "multiply-blend" "/out/mergedimage-multiply-blend.png" 32 32)
(dump-pixels "layer-order" "/out/mergedimage-layer-order.png" 64 64)
(gimp-message "baseline-asset pixel dump done")
