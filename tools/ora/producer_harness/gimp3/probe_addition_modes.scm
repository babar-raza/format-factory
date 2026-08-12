; Probe GIMP 3.x's own Script-Fu constant names for the Addition family,
; matching the earlier GIMP 2.10 discovery discipline
; (probe_layer_modes.scm) rather than assuming 3.x kept the same names.
(gimp-message (string-append "LAYER-MODE-ADDITION=" (number->string LAYER-MODE-ADDITION)))
(gimp-message (string-append "LAYER-MODE-ADDITION-LEGACY=" (number->string LAYER-MODE-ADDITION-LEGACY)))
(gimp-message "probe done")
