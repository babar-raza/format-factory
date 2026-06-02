---
visibility: generated
generated_by: codex
---

# Dogfood Enforcement

The R90 PPM-to-PGM tests inspect the adapter source, require `pgm.pgm_parser.write_pgm`, reject
known external image backends, write an output file, reload it with the Format Factory PGM parser,
and verify meaningful grayscale values.
