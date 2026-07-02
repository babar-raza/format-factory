---
version: "1.0"
last-updated: "2026-07-01"
phase-available: "all"
gate-required: null
created-by: TC-CERT-I-020
spec_qname_required: "false"
product_track: "governance"
---

# /certification-generate-security-tests

Generate security test stubs (path traversal, malformed input, oversized payloads, etc.)
for a format.

**WARNING: Mutates test files in place — use with caution. Review output before committing.**

## What It Does

1. Analyzes the format's source for security-relevant entry points
2. Generates test stubs for OWASP-style attack patterns relevant to file parsing
3. Appends stubs to the format's security test file

## Usage

```bash
python tools/certification/generate_security_tests.py \
  --format fods \
  --src-path src/python/fods \
  --test-path tests/python/fods
```

## Layer

L28 Certification Audit Layer (`plans/layers/certification-audit-layer.md`)

## Allowed Paths

- `tools/certification/generate_security_tests.py`
- `reports/` — evidence output (write)

## Forbidden Paths

- `src/net/**` — no .NET product source mutation
- `src/python/**` — no Python product source mutation
- `plans/strategic/**` — strategic plans are read-only

## Stop Conditions

- Stop if security tests cannot be generated
- Stop if focused tests do not pass after changes

## Output Format

- Generated artifact written to the configured output path
- Confirmation message: file path and size
- Validation result confirming the output is well-formed
