# Python FOSS Security Model

**Date:** 2026-05-17
**Status:** ALPHA FOSS PREVIEW

## Security Principles

1. **No network access** — All parsing is offline. No DNS, HTTP, or socket calls.
2. **Size guards** — All codecs reject inputs exceeding configured size limits.
3. **XXE-safe XML parsing** — `xml.etree.ElementTree` does not resolve external entities by default.
4. **No code execution** — No eval, no formula evaluation, no macro execution.
5. **No external DTD loading** — DOCTYPE declarations are stripped (ABW) or ignored.
6. **No subprocess calls** — No system commands invoked during parsing.

## Per-Format Security Limits

### ZST

| Guard | Value | Purpose |
|-------|-------|---------|
| DEFAULT_MAX_OUTPUT_BYTES | 256 MiB | Decompression bomb protection |
| DEFAULT_MAX_WINDOW_BYTES | 2 GiB | Window size limit |
| Input guard | probe_frame accepts bytes (no network) | |

**Known risk:** .tar.zst files may contain embedded archives — not parsed, documented.

### FODP / FODG

| Guard | Value | Purpose |
|-------|-------|---------|
| MAX_FILE_SIZE | 64 MiB | XML bomb / large file protection |
| XML parser | xml.etree.ElementTree | XXE-safe |
| Entity expansion | Not resolved | |

### Gnumeric

| Guard | Value | Purpose |
|-------|-------|---------|
| MAX_FILE_SIZE | 64 MiB (compressed) | Prevents decompression bomb |
| Gzip decompression | stdlib gzip | No C library with known CVEs |
| XML parser | xml.etree.ElementTree | XXE-safe |

Note: Gnumeric files are gzip-compressed XML. The compressed size guard is applied before decompression.

### ABW

| Guard | Value | Purpose |
|-------|-------|---------|
| MAX_FILE_SIZE | 64 MiB | Large file protection |
| DOCTYPE stripping | Lines starting with `<!DOCTYPE` removed | Prevents DTD injection |
| XML parser | xml.etree.ElementTree | XXE-safe |
| DTD server | http://www.abisource.com/awml.dtd — UNREACHABLE | Server down; parser ignores |

## Threat Model

| Threat | Mitigation |
|--------|------------|
| Decompression bomb | Size guards (ZST: 256 MiB output; others: 64 MiB input) |
| XML billion-laughs | xml.etree.ElementTree has entity expansion limits |
| XXE (XML External Entity) | xml.etree.ElementTree does not load external entities |
| DTD injection | ABW: DOCTYPE stripped; others: no DOCTYPE processing |
| Path traversal | No file system writes |
| Command injection | No subprocess calls |
| Network exfiltration | No network calls in any codec |

## Known Limitations

- No audit against formal security standards (OWASP, NIST)
- No fuzzing beyond Gate 7 prototype testing
- Alpha quality — not hardened for adversarial inputs in production
- Do not use these packages to parse untrusted files from the internet without additional sandboxing
