# Changelog

## 0.1.0.dev0 (unreleased)

- First code. Archive container and media-type sentinel: `ORA-CONTAINER-001`,
  `ORA-MIMETYPE-001`. Rejects traversal, absolute and drive-qualified member
  names, backslash separators, duplicate members, compression methods other
  than STORED and DEFLATED, a missing or misplaced `mimetype`, a `mimetype`
  with any surrounding whitespace, a missing `stack.xml`, and archives over the
  caller's entry-count, size or compression-ratio limits.
- Add the typed, recursively-nesting layer stack model (`OraStack`,
  `OraLayer`, `OraText`, `OraNode`) with explicit-vs-defaulted attribute
  tracking, and composite-operation lookup (`composite_op_info`).
- Add atomic transactional editing (`apply_transaction`, `EditStep`,
  `TransactionResult`) that rolls back to the untouched original document if
  any step raises.
- Add raster asset resolution by exact archive member name, reading PNG
  metadata without decoding pixel data (`OraContainer`, `resolve_asset`,
  `resolve_all_assets`).
- Add caller-supplied thumbnail/merged-image replacement, validated against
  the same constraints load-time parsing enforces (`replace_baseline_asset`).
- Add LOSSLESS/CANONICAL preservation modes with pre-commit loss disclosure
  (`dumps`, `PreservationMode`, `check_preservation`).
