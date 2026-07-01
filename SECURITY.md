# Security Policy

## Supported Versions

| Format | Track | Status |
|--------|-------|--------|
| FODS (Python) | FOSS | Pre-release — actively maintained |
| FODT (Python) | FOSS | Pre-release — actively maintained |
| ZST (Python) | FOSS | Pre-release — actively maintained |
| Netpbm: PBM, PGM, PPM (Python) | FOSS | Pre-release — actively maintained |
| All other formats | FOSS | Pre-release — best effort |

## Reporting a Vulnerability

To report a security vulnerability, please open a GitHub issue using the **Security Vulnerability** template, or email the maintainer directly.

When reporting, include:

- **Format affected** (e.g., FODS, FODT, ZST)
- **Description** of the vulnerability
- **Steps to reproduce** the issue
- **Expected vs. actual behavior**
- **Impact assessment** (data exposure, denial of service, code execution, etc.)

We aim to:
- Acknowledge reports within **48 hours**
- Provide a fix timeline within **7 days**
- Release a patch within **30 days** for confirmed vulnerabilities

## Security Architecture

All parsers produced by this project conform to the threat model defined in [`docs/governance/security.md`](docs/governance/security.md). The threat model covers eight categories:

1. **XXE (XML External Entity)** — External entity injection via XML parsers
2. **DTD Entity Expansion** — Billion laughs and related amplification attacks
3. **Zip Bombs** — Decompression-based resource exhaustion (for container formats)
4. **Path Traversal** — Malicious file paths escaping intended directories
5. **Malformed Input Handling** — Graceful failure on corrupt or adversarial files
6. **Memory Limits** — Bounded memory allocation to prevent OOM conditions
7. **Recursion Limits** — Stack depth guards for nested structures
8. **Binary Parser Safety** — Bounds checking for binary format readers

## Gate 8: Security Review

Every format must pass **Gate 8 (Security Review)** before reaching product status. Gate 8 requires:

- Threat model coverage assessment against all 8 categories
- Parser fuzzing results (Gate 7 prerequisite)
- Human security review sign-off

Gate approvals are recorded in [`registry/format-registry.yaml`](registry/format-registry.yaml) and cannot be granted by automated agents.
