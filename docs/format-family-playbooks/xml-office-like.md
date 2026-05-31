# Playbook: XML Office-Like Format

**Applies to:** FODS, FODT, ODS, ODT, and similar flat/zipped XML office formats
**Added:** R85 Train H

---

## Acquisition Inputs
- Format specification (ODF spec, OOXML spec, vendor docs)
- Public samples (Apache-2.0 or compatible)
- Security research (known attack vectors for XML formats)

## Expected Spec Artifacts
- acquisition-packs/{format}/ — gate evidence, corpus samples
- schemas/neutral-model/{format}/ — 5-10 entities, 15-30 mappings, 10-25 rules
- generated-requirements/{format}/ — AI-generated requirements (verified by human)

## Object Model Skeleton (Python)
```
{format}_document = {
  "metadata": {title, author, created, modified},
  "body": <format-specific>,    # sheets for spreadsheet; paragraphs for text
  "styles": [...],              # optional
  "settings": {...}             # optional
}
```

## Parser Strategy
1. Use iterparse (streaming) for large files
2. DTD prohibited; XmlResolver disabled
3. File-size guard (50 MB default)
4. Preserve unknown XML nodes via DOM-bypass strategy
5. Populate both doc["blocks"] and doc["content"] if paragraph APIs needed

## Writer Strategy
1. Write valid XML with proper namespace declarations
2. Preserve round-trip fidelity for unknown nodes
3. Validate output against spec grammar before tests

## Edit Model Strategy
1. Python: neutral model dict — cells/paragraphs are mutable dicts
2. .NET: DOM-backed XDocument — only accessed nodes are read/written
3. Any edit that appends must update ALL content representations (doc["blocks"] + doc["content"])

## Export/Dogfood Strategy
- Spreadsheet: export_to_csv using Format Factory CSV library
- Text: export_to_txt using document_to_text API
- Both .NET and Python: record dogfood_status (IMPLEMENTED / GAP_DOGFOOD_EXTERNAL)

## Tests
- Gate 4: prototype parser (10-20 tests)
- Gate 5: neutral model round-trip (15-25 tests)
- Gate 6: oracle comparison (5-15 tests)
- Gate 7: fuzz/security guard (10-20 tests)
- Gate 8: security review (20+ tests)
- Gate 9-10: full API + package (50+ tests)
- Gate 11: installed workflow + edit + save + export (20+ tests per product)

## Package Artifacts
- pyproject.toml from packaging/python/pyproject.template.toml
- __version__ = "0.1.0.dev0", __track__ = "python-foss", __commercial_ready__ = False
- wheel + sdist via packaging/python/build-local-packages.py

## Examples/Docs
- examples/python/{format}/edit_save_{format}.py
- examples/python/{format}/edit_save_export_{format}.py
- docs/python-foss/{format}-python-foss.md
- release-manifests/python-foss/{format}.yaml

## Evidence Requirements
- final-verdict.md with BUNDLE_VALIDATION: PASS, no PENDING markers
- 3-pass bundle protocol (Pass 1 → commit → Pass 2 → commit → Pass 3)
- sidecar .sha256-proof.json (gitignored, force-added)
- supervisor review package with package artifacts + raw logs
