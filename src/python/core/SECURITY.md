---
visibility: generated
generated_by: codex
---

# Security policy

Report suspected vulnerabilities privately through the repository security
advisory channel. Do not include malicious samples or secrets in public issues.

The core package performs no parsing or external I/O. Format libraries must
apply `ResourceLimits` before allocation, decompression, archive extraction,
or detached-resource access. Defaults are intentionally finite and may be
tightened by callers.
