# Changelog

## 0.1.0.dev0 (unreleased)

- First code. Archive container and media-type sentinel: `ORA-CONTAINER-001`,
  `ORA-MIMETYPE-001`. Rejects traversal, absolute and drive-qualified member
  names, backslash separators, duplicate members, compression methods other
  than STORED and DEFLATED, a missing or misplaced `mimetype`, a `mimetype`
  with any surrounding whitespace, a missing `stack.xml`, and archives over the
  caller's entry-count, size or compression-ratio limits.
