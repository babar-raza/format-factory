# R108 POC Gap Selection

## Selection Criteria
- Depth-first: save/export/roundtrip over shallow getters
- Object-model completion: workflows that prove real usage
- No stale R98 gaps

## Selected Gaps

### FODS .NET
- **SaveAfterEdit roundtrip proof:** Load, edit cells, save to temp, reload and verify. Tests full DOM persistence.

### FODT .NET
- **SaveAfterReplace roundtrip proof:** Load, replace text in paragraphs, save, reload, verify text persists.

### Netpbm .NET
- **Threshold (PGM to PBM conversion):** Convert grayscale image to binary based on threshold value. Returns PBM format.

### Python/FOSS
- **PBM probe/parse hardening:** Additional edge-case tests for pbm module.
- **SYLK installed-workflow verification:** Verify sylk module works from installed package.
- **ZST frame inspection tests:** Test probe_frame and validate_file functions.
