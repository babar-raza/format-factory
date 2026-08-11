(define (probe name-str value)
  (gimp-message (string-append name-str "=" (number->string value))))

(probe "HSV_VALUE" LAYER-MODE-HSV-VALUE)
(gimp-message "probe-batch-6 done")
