# Security Policy — Parser Threat Model

**Document type:** Policy — Phase 0 Foundation
**Last reviewed:** 2026-05-04 (run014: global audit — content verified consistent with current governance)
**Authority:** This document defines the security requirements for all parsers, converters, and validators produced by format-factory.

---

## Purpose

File format parsers are a primary attack surface. A parser that accepts untrusted input (user-supplied files) must be hardened against a class of attacks that have historically caused critical vulnerabilities in widely deployed software. This document defines the threat model, required mitigations, and security review expectations that govern all format-factory parser implementations.

This document is written before any parser code exists. It must be read and applied by any agent or developer writing prototype or product code.

---

## Scope

This policy applies to:
- All prototype parsers in `prototypes/by-format/`
- All product parsers in `src/python/{format}/` (Python FOSS) and `src/net/{format}/` (.NET product)
- All commercial-tier parsers within `src/net/{format}/` (when created)
- All validation scripts in `tools/validation/`

---

## Threat Category 1: XML External Entities (XXE)

**Description:** XML parsers that resolve external entity references can be exploited to read local files, perform server-side request forgery (SSRF), or cause denial of service. This is OWASP A05:2017 and remains relevant for any XML-based format (ODF, OOXML, SVG, etc.).

**Required mitigations:**
- Python: Disable external entity processing in all XML parsers. Use `defusedxml` for any untrusted XML input, or disable `resolve_entities` explicitly in `lxml`.
- .NET: Use `XmlReaderSettings` with `DtdProcessing = DtdProcessing.Prohibit` and `XmlResolver = null` for all untrusted input.
- Never use the built-in XML parsers with default settings on untrusted file input.

**Prototype requirement:** Every prototype that parses XML must demonstrate in its README that external entity resolution is disabled.

---

## Threat Category 2: DTD and Entity Expansion (Billion Laughs / XML Bomb)

**Description:** A malformed XML file can define recursive or deeply nested entity expansions that cause the parser to expand gigabytes of data from a small file (the "billion laughs" attack). This is a denial-of-service vector.

**Required mitigations:**
- Python: `defusedxml` prevents this by default. If `lxml` is used directly, set `huge_tree=False` and `resolve_entities=False`.
- .NET: `XmlReaderSettings.MaxCharactersFromEntities` must be set to a reasonable limit (e.g., 10,000 characters).
- All parsers must enforce a maximum in-memory document size.

---

## Threat Category 3: Zip Bombs and Decompression Limits

**Description:** A compressed format (ODS, XLSX, DOCX are ZIP-based) may contain files that expand to gigabytes when decompressed. Even a plain gzip or zstd stream can be a decompression bomb.

**Required mitigations:**
- Limit the total uncompressed size of any ZIP archive processed. Suggested default limit: 500 MB total, 100 MB per entry.
- Check the uncompressed size before extracting (where the format provides it — note that ZIP central directory sizes can be spoofed).
- Stream decompression rather than loading the entire archive into memory.
- Apply limits to gzip, zstd, bzip2, and other compression layers as they appear in format families.

**Note:** FODS (the first pilot) is a flat XML file and does not have a ZIP layer. This mitigation is not blocking for Phase 3 prototypes but is required before any zipped format (ODS, XLSX) reaches product.

---

## Threat Category 4: Path Traversal in Archive Formats

**Description:** Archive-based formats (ZIP, ODS, XLSX) may contain entries with filenames like `../../etc/passwd` or `C:\Windows\system32`. An extractor that writes these files naively will overwrite arbitrary files on the host system.

**Required mitigations:**
- Normalize and validate all entry paths before extraction.
- Reject any entry whose resolved path escapes the intended extraction directory.
- In Python: use `zipfile.Path` or explicitly check `os.path.realpath` on each extracted path.
- In .NET: validate `ZipArchiveEntry.FullName` against the target directory before writing.
- Never use extraction utilities that do not perform path sanitization.

---

## Threat Category 5: Malformed File Handling

**Description:** Real-world files frequently deviate from specification. A parser that assumes well-formed input will crash, hang, or produce incorrect results on malformed files. Crashes can be exploited if the parser runs in a privileged context.

**Required mitigations:**
- Parse defensively. Check every length field, offset, and count before using it.
- Return structured error results rather than raising unhandled exceptions on malformed input.
- Log the specific malformation (with the file offset or XPath location) for diagnostic purposes.
- Fuzz testing (Gate 7) must include truncated files, corrupt headers, out-of-range length fields, and invalid Unicode sequences.

---

## Threat Category 6: Memory Limits

**Description:** A parser that loads an entire file into memory without limits can be exhausted by a large or malformed file.

**Required mitigations:**
- Set a maximum file size for in-memory parsing. Suggested default: 256 MB for text formats, 100 MB for uncompressed binary.
- Use streaming parsing where possible (e.g., `iterparse` in Python's ElementTree for XML).
- If streaming is not possible, reject files above the configured limit with a clear error.
- Document the memory model in each prototype's README.

---

## Threat Category 7: Recursion Limits

**Description:** Some formats support nested structures (nested styles, nested comments, nested elements). A deeply nested document can cause a stack overflow in a recursive parser.

**Required mitigations:**
- Set a maximum recursion depth for all recursive parsing functions.
- Convert recursive algorithms to iterative algorithms for production parsers.
- Python: `sys.setrecursionlimit` is global and unreliable — use explicit depth counters instead.
- .NET: Be aware of stack depth when processing deeply nested XML or binary tree structures.

---

## Threat Category 8: Future Binary Parser Safety

These categories are not relevant for the FODS pilot (XML only) but must be addressed when any binary format is adopted:

- **Integer overflow in length/offset arithmetic:** Cast to 64-bit integers before arithmetic on 32-bit or 16-bit fields.
- **Out-of-bounds reads:** Validate all offsets against the file or buffer size before reading.
- **Uninitialized memory:** .NET managed code avoids this; Python is generally safe. Document any `ctypes` or `struct` usage carefully.
- **Format string vulnerabilities:** Not typically applicable to Python or .NET managed code, but must be checked if C extensions are used.

---

## Fuzzing Expectations (Gate 7)

Gate 7 (Fuzz/Malformed Testing Complete) requires:

1. A minimum fuzz iteration count for the format being tested. Suggested minimum: 10,000 iterations for XML formats, 100,000 for binary formats.
2. Fuzz seeds in `tests/fuzz/<format-id>/` covering: minimal valid file, minimal empty file, truncated file, file with illegal values in key fields, file with oversized length fields.
3. All crashes documented in `reports/security/<format-id>.md` with: crash input (or characterization), stack trace, root cause analysis, proposed mitigation.
4. No unmitigated crashes that could result in arbitrary code execution, uncontrolled memory exhaustion, or file system writes outside the intended output directory.

---

## Security Review Requirement (Gate 8)

Gate 8 (Security Review Complete) requires a human security reviewer to:

1. Verify that all threat categories applicable to the format have been addressed.
2. Confirm that mitigations are documented and implemented (or explicitly deferred with a reason for prototype-only work).
3. Sign off on `reports/security/<format-id>.md` by populating the `sign-off` field with their name and date.
4. Document any residual risks that are accepted rather than mitigated.

The security reviewer may be the project lead in Phase 3. A dedicated security reviewer is recommended once the project reaches Gate 10.

---

## Relationship to Other Documents

- See `docs/gates.md` for Gate 7 and Gate 8 pass criteria.
- See `docs/acquisition-workflow.md` for where fuzzing and security review fit in the workflow.
- See `acquisition-packs/_template/parser-notes.md` for the template that documents parser strategy (which informs security design).
- See `reports/_readme.md` for where security reports are stored.
