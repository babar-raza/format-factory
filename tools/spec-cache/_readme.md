# tools/spec-cache

**Document type:** Directory Orientation — Phase 0 Foundation
**Last reviewed:** 2026-05-03 (run009 — authorization model added; TC-0007 scope clarified)

---

## Purpose

This directory contains the generic specification cache tooling: scripts that download, hash, index, and check format specification documents for use by the acquisition pipeline. Cached specifications are stored in `.local/spec-cache/` (gitignored, local-only). This directory contains only the tools that manage that cache — not the cached content itself.

All tools in this directory are `visibility: internal`. They are acquisition-layer tools that are never released to users or included in any product package.

**Phase 0 scope:** In Phase 0, only `_readme.md` exists. No scripts are created in Phase 0.

**Phase 1 scope (TC-0007):** TC-0007 implements generic tooling only. TC-0007 does NOT require or perform any real specification download. TC-0007 completion proves the tooling works via a local dry-run synthetic test. Real spec acquisition for any format requires a separate explicit execution prompt that names the format, confirms the legal category, and authorizes the download. See `docs/specification-cache.md` for the full authorization model.

---

## Directory Structure

```
tools/spec-cache/
+-- _readme.md              This file (Phase 0)
+-- acquire_spec.py         Download, hash, and index a spec file (Phase 1 — TC-0007; requires --allow-network)
+-- refresh_check.py        Check all indexed specs for staleness without auto-downloading (Phase 1 — TC-0007)
+-- spec_index.py           Read/write spec-index.yaml entries (Phase 1 — TC-0007)
```

In Phase 0, only `_readme.md` exists. All scripts are created in Phase 1 via TC-0007.

---

## Cache Location

The cache itself lives at `.local/spec-cache/` (gitignored):

```
.local/spec-cache/
  <format-id>/
    <version>/
      spec.pdf              (or .html, .xml — the downloaded spec file)
      spec-index.yaml       (provenance and metadata)
      errata/               (errata documents if any)
      schemas/              (normative schema files if part of the spec)
```

`.local/spec-cache/` is excluded from git by the `.local/` pattern in `.gitignore`. Specification files are never committed.

---

## Download Authorization Rules

Spec downloads are NOT automatic. Before any real spec download may occur, all of the following must be satisfied:

1. **Phase 1+ only.** Phase 0 prohibits all downloads.
2. **Explicit taskcard.** A taskcard must exist authorizing acquisition for the specific format and version. TC-0007 covers generic tooling only and does not authorize any real download.
3. **Legal category confirmed.** Categories 1-3 only. Category 5 or 6 is a hard block.
4. **Canonical source URL approved.** Standards body official page only. No mirrors.
5. **Explicit execution prompt authorization.** The execution prompt must name the format, version, canonical URL, and explicitly state that acquisition is authorized.
6. **Local-only storage.** All downloads go to `.local/spec-cache/` (gitignored). Never committed.

If authorization is not present, the agent must log a gap and create or update a spec-acquisition taskcard rather than downloading.

---

## Tool Inventory (Planned — Phase 1)

| Tool | Phase | Taskcard | Purpose |
|---|---|---|---|
| `acquire_spec.py` | Phase 1 | TC-0007 | Download a spec from its canonical URL; requires `--allow-network`; supports `--dry-run` for testing |
| `refresh_check.py` | Phase 1 | TC-0007 | Scan all spec-index.yaml entries for staleness; flag stale entries; never auto-download |
| `spec_index.py` | Phase 1 | TC-0007 | Library module: read/write/validate spec-index.yaml entries; used by acquire and refresh tools |

---

## Security and Legal Requirements for Tools

Tools in this directory handle specification file downloads. Security and legal rules:

- **Authorization required:** `acquire_spec.py` requires `--allow-network <authorization-string>` to perform any network download. Dry-run mode is the default and requires no network access. Running without `--allow-network` must print a clear refusal message.
- **Canonical source only:** All downloads must use the canonical source URL recorded in spec-index.yaml. No third-party mirrors.
- **SHA-256 verification:** After every download, compute SHA-256 and record it. On every subsequent use, verify the hash matches.
- **No redistribution without clearance:** Do not copy cached spec files into committed directories. Set `redistribution_permitted` correctly based on the standards body's terms. Local caching does not imply redistribution rights.
- **No API keys needed:** Specification downloads are public HTTP/HTTPS requests. No credentials are required. If a standards body requires login or payment for access, flag the spec as requiring human action and do not attempt automated download.
- **Copyright:** Specification documents are copyrighted. They may only be used for the purposes covered by the standards body's publication terms (typically: reading and implementing, not redistribution). Quote only minimal necessary excerpts in committed artifacts.
- **Remote LLM restriction:** Full spec documents must not be sent to remote LLM endpoints by default. See `docs/llm-endpoint-strategy.md` for the spec content in prompts rules.

---

## Relationship to Other Documents

- `docs/specification-cache.md` — full specification cache policy and authorization model (this directory's governing document)
- `docs/acquisition-workflow.md` — Stage 2 requires a cached spec before evidence drafting begins; authorization required
- `docs/legal-and-licensing.md` — legal category and four permissions (read, implement, store, redistribute)
- `docs/llm-endpoint-strategy.md` — LLM content quoting spec text must be handled carefully; remote restrictions
- `taskcards/TC-0007-specification-cache.md` — Phase 1 generic tooling implementation scope (no real download required)
