# Parser Notes: Nearly Raw Raster Data

## Parsing Strategy
- **Primary module:** struct (stdlib) for binary data, text parsing for header
- **Reuse pattern:** Text-header + binary-data pattern (custom binary codec)
- **Estimated LOC:** 250-350

## Detection (Probe)
Read the first line of the file and check for the magic string `NRRD0001` through `NRRD0005`. For detached headers, check `.nhdr` extension with the same magic line.

## Loading
Parse the text header line-by-line, extracting key-value pairs separated by `: `. Required fields: `type`, `dimension`, `sizes`. Determine encoding from the `encoding` field. For `raw` encoding, read the binary data directly after the blank line separating header from data. For `gzip`/`bzip2`/`zlib`, decompress before interpreting. Build a structured model with header metadata and an N-dimensional array reference.

## Writing
Construct the text header from the model metadata, write the header lines followed by a blank line, then write the raw (or compressed) binary data. Write support planned.

## Dependencies
- stdlib only (struct, gzip, bz2, zlib modules)
- No new external dependencies required
