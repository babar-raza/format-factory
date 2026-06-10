# Normalization Report — SAL Real Pilot R1
Sprint: FORMAT-FACTORY-SPECIFICATION-AUTHORITY-LAYER-REAL-PILOT-R1-001
Lane: C

---

## Parse Results

All 4 pilot sources parsed successfully using `parse_spec_from_text()`.
Auto-detection selected `markdown` parse method for all (fixtures use `#` headings).

| Source | Method | Sections | Total Lines | Warnings |
|---|---|---|---|---|
| src-zst-rfc8878 | markdown | 6 | ~40 | None |
| src-netpbm-docs | markdown | 5 | ~32 | None |
| src-dif-softarts | markdown | 5 | ~30 | None |
| src-fods-oasis | markdown | 5 | ~30 | None |

---

## Normalization Results

All 4 sources normalized using `normalize_spec()`. Artifacts written to:
`.local/evidences/spec-authority-real-pilot-r1/artifacts/{source_id}-normalized.json`

| Source | Sections Normalized | Artifact Path |
|---|---|---|
| src-zst-rfc8878 | 6 | `.local/evidences/spec-authority-real-pilot-r1/artifacts/src-zst-rfc8878-normalized.json` |
| src-netpbm-docs | 5 | `.local/evidences/spec-authority-real-pilot-r1/artifacts/src-netpbm-docs-normalized.json` |
| src-dif-softarts | 5 | `.local/evidences/spec-authority-real-pilot-r1/artifacts/src-dif-softarts-normalized.json` |
| src-fods-oasis | 5 | `.local/evidences/spec-authority-real-pilot-r1/artifacts/src-fods-oasis-normalized.json` |

---

## Index Results

All 4 sources indexed using `build_index()`.

| Source | Terms | Sections | Index Path |
|---|---|---|---|
| src-zst-rfc8878 | 92 | 6 | `.../src-zst-rfc8878-index.json` |
| src-netpbm-docs | 76 | 5 | `.../src-netpbm-docs-index.json` |
| src-dif-softarts | 76 | 5 | `.../src-dif-softarts-index.json` |
| src-fods-oasis | 64 | 5 | `.../src-fods-oasis-index.json` |

Search test: `search_index("src-zst-rfc8878", "magic frame")` → **4 matching sections** ✓

---

## Digest Results

Content digests computed using `compute_digest()` — stable SHA-256 of section content (excludes timestamps).

| Source | SHA-256 Snapshot | Content Digest |
|---|---|---|
| src-zst-rfc8878 | `c15ec66abc6489c0...` | `3f144d94a3bb7934...` |
| src-netpbm-docs | `cec3030092754c36...` | `a6d410b7255ed2de...` |
| src-dif-softarts | `3065d192e05345a5...` | `bc99a91e7c6d64b3...` |
| src-fods-oasis | `24e5975f6e7e2890...` | `b34b495ff8e69d3e...` |

---

## Defects and Limitations

1. **No PDF parser**: If real ODF 1.3 spec (PDF) were fetched, it could not be parsed directly. Preprocessing step needed. **Classification: KNOWN_LIMITATION** (not a bug in this sprint's scope).

2. **Network fetch deferred**: No HTTP client implemented; `ingest_text_fixture()` used. For Pilot R2, a fetch step is needed to ingest real RFC 8878 text. **Classification: PLANNED_GAP** (documented in handoff).

3. **FODS/FODT partial**: Only structural summary extracted from FODS/FODT fixture. Full ODF 1.3 compliance not attempted. **Classification: STRETCH_PILOT_LIMITATION** (acceptable for this sprint).

No blocking defects — all 4 sources have normalized, indexed, and digest artifacts.
