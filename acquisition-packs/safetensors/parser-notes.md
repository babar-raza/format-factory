# Parser Notes: SafeTensors

## Parsing Strategy
- **Primary module:** struct + json (stdlib)
- **Reuse pattern:** Binary header + JSON metadata pattern (custom binary codec)
- **Estimated LOC:** 250-350

## Detection (Probe)
Read the first 8 bytes as a little-endian uint64 for header size. Validate that header size is reasonable (< file size - 8) and that the subsequent bytes parse as valid JSON with tensor descriptor entries.

## Loading
Read the 8-byte header length, then read and parse the JSON header to get tensor metadata (name, dtype, shape, data_offsets). For each tensor, extract the raw bytes from the data section using the offset pair. Build a structured model mapping tensor names to their metadata and data references.

## Writing
Construct the JSON header from the tensor model, compute data offsets, write the 8-byte header size followed by the JSON header and contiguous tensor data. Write support planned.

## Dependencies
- stdlib only (struct, json modules)
- No new external dependencies required
