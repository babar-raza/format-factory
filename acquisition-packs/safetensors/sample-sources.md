# Sample Sources: SafeTensors

## Synthetic Samples (planned)
Samples will be generated synthetically using Python stdlib.
- Valid samples: 3 (planned for Gate 3)
- Invalid samples: 1 (planned for Gate 3)
- Generation method: struct.pack for the 8-byte header size + json.dumps for the metadata header + raw bytes for tensor data

## External Reference Samples
- None required for Gate 3 (synthetic samples sufficient for initial testing)

## Provenance
All samples are project-owned, Apache-2.0 licensed, synthetic.
