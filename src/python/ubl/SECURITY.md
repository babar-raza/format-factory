---
visibility: generated
generated_by: codex
---

# Security policy

The stable API parses data only; it does not resolve external entities,
retrieve schemas, execute signatures, or apply jurisdiction-specific rules.
DTD and entity declarations are rejected before XML parsing. Input size,
element count, nesting depth, attribute count, and text size are bounded by
configurable `ResourceLimits`.

Report vulnerabilities privately through the repository security channel.
