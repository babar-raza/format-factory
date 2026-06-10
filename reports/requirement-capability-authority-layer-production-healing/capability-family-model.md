# Capability Family Model

Sprint ID: FORMAT-FACTORY-REQUIREMENT-CAPABILITY-AUTHORITY-LAYER-PRODUCTION-BLOCKER-HEALING-001
Owner: Lane B

## Rules (global, apply to all targets)

- **Netpbm must be retained.** Netpbm (.NET commercial) is a required POC target; it may not be removed, deprioritized, or replaced by another format.
- **SVG must not replace Netpbm.** SVG is not an equivalent format family; adding SVG support does not satisfy Netpbm capability requirements.
- **DIF may substitute SYLK only if coverage validates faster.** DIF is a valid SYLK substitute only if DIF required capabilities can be coverage-validated faster than SYLK.
- **Gnumeric counts only if required capabilities are coverage-validated.** Gnumeric is a stretch target; including it in poc-targets without coverage-validated claims is not allowed.

## Target 1: FODS (.NET Commercial)

- **Capability families:** sheet_management, cell_read, cell_write, export, roundtrip
- **Required claim IDs pattern:** fods-net-{family}-{operation} (e.g., fods-net-sheet_management-load, fods-net-cell_write-save)
- **Proof sufficiency level required:** ACCEPTED_FOR_POC
- **dogfood_required:** true (export and save must have DogfoodArtifact)
- **accepted_with_limitations allowed:** true (partial formatting support is acceptable if declared)
- **Expected Mainstream lane:** .NET product implementation lane
- **Expected output artifacts:** src/net/fods/FodsDocument.cs extensions, tests/net/fods/ test files, examples/net/fods/ examples, dogfood output .fods file

## Target 2: FODT (.NET Commercial)

- **Capability families:** document_management, paragraph_read, paragraph_write, heading_management, export
- **Required claim IDs pattern:** fodt-net-{family}-{operation}
- **Proof sufficiency level required:** ACCEPTED_FOR_POC
- **dogfood_required:** true (export must have DogfoodArtifact)
- **accepted_with_limitations allowed:** true (style/macro features may be declared_limited)
- **Expected Mainstream lane:** .NET product implementation lane
- **Expected output artifacts:** src/net/fodt/FodtDocument.cs extensions, tests/net/fodt/ test files, examples/net/fodt/ examples, dogfood output .fodt file

## Target 3: Netpbm .NET Commercial

- **Capability families:** image_load, image_inspect, image_transform, image_save, format_conversion
- **Required claim IDs pattern:** netpbm-net-{family}-{operation}
- **Proof sufficiency level required:** ACCEPTED_FOR_POC
- **dogfood_required:** true (save and convert must have DogfoodArtifact)
- **accepted_with_limitations allowed:** true (binary format variant limitations acceptable if declared)
- **Expected Mainstream lane:** .NET product implementation lane
- **Expected output artifacts:** src/net/netpbm/ extensions, tests/net/netpbm/ test files, examples/net/netpbm/ examples, dogfood output .ppm/.pgm/.pbm files

## Target 4: ZST (Python FOSS)

- **Capability families:** compression, decompression, streaming, level_control
- **Required claim IDs pattern:** zst-py-{family}-{operation}
- **Proof sufficiency level required:** ACCEPTED_FOR_POC
- **dogfood_required:** true (streaming compress+decompress must have DogfoodArtifact with validated output)
- **accepted_with_limitations allowed:** true (dictionary mode may be accepted_with_limitations initially)
- **Expected Mainstream lane:** Python FOSS implementation lane
- **Expected output artifacts:** src/python/zst/ module, tests/python/zst/ test files, examples/python/zst/ examples, dogfood output .zst file

## Target 5: Python Netpbm (Python FOSS)

- **Capability families:** image_read, image_write, format_detection, pixel_manipulation
- **Required claim IDs pattern:** netpbm-py-{family}-{operation}
- **Proof sufficiency level required:** ACCEPTED_FOR_POC
- **dogfood_required:** true (image_write must have DogfoodArtifact)
- **accepted_with_limitations allowed:** true (binary P4/P5/P6 write may be declared_limited initially)
- **Expected Mainstream lane:** Python FOSS implementation lane
- **Expected output artifacts:** src/python/ppm/ or netpbm/ module, tests/python/ppm/ test files, examples/python/ppm/ examples, dogfood output .ppm file

## Target 6: SYLK (Python FOSS)

- **Capability families:** sylk_parse, sylk_write, csv_export, grid_model
- **Required claim IDs pattern:** sylk-py-{family}-{operation}
- **Proof sufficiency level required:** ACCEPTED_FOR_POC
- **dogfood_required:** true (csv_export must have DogfoodArtifact with verified CSV output)
- **accepted_with_limitations allowed:** true (multi-sheet SYLK may be accepted_with_limitations initially)
- **Expected Mainstream lane:** Python FOSS implementation lane
- **Expected output artifacts:** src/python/sylk/ module, tests/python/sylk/ test files, examples/python/sylk/ examples, dogfood output .slk and .csv files

## Target 7: DIF (Python FOSS — substitution for SYLK)

- **Capability families:** dif_parse, dif_write, csv_export, grid_model
- **Required claim IDs pattern:** dif-py-{family}-{operation}
- **Proof sufficiency level required:** ACCEPTED_FOR_POC (same bar as SYLK for substitution to be valid)
- **dogfood_required:** true
- **accepted_with_limitations allowed:** true
- **Expected Mainstream lane:** Python FOSS implementation lane
- **Expected output artifacts:** src/python/dif/ module, tests/python/dif/ test files, examples/python/dif/ examples, dogfood output .dif and .csv files
- **Substitution condition:** DIF substitutes SYLK only if DIF coverage validates equal or faster than SYLK

## Target 8: Gnumeric (Python FOSS — stretch)

- **Capability families:** gnumeric_parse, gnumeric_inspect, csv_export (minimum)
- **Required claim IDs pattern:** gnumeric-py-{family}-{operation}
- **Proof sufficiency level required:** COVERAGE_VALIDATED (accepted_for_poc not required for stretch credit)
- **dogfood_required:** false (stretch target; dogfood recommended but not required for credit)
- **accepted_with_limitations allowed:** true
- **Expected Mainstream lane:** Python FOSS implementation lane (stretch lane)
- **Expected output artifacts:** src/python/gnumeric/ module, tests/python/gnumeric/ test files
- **Stretch condition:** Gnumeric counts toward POC only if required capabilities are coverage-validated. Gnumeric does not replace any required target.
