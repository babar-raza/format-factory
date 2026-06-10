# Multi-Lane Product-First Mega-Train — Preflight

Sprint ID: FORMAT-FACTORY-STANDING-MULTI-LANE-PRODUCT-FIRST-MEGA-TRAIN-001
Run ID: multilane-product-first-mega-train
Baseline package: declaration-review-package(119).zip
SHA-256: 8290a748bab89d1a8e553297f91c87d9b69b2332642b767b96777f72f46a5ed5
Git HEAD at start: e382e5fd8e65bc146c0821602cb8fb1ecfab982c

## Dirty state classification
- `.supervisor/`, `reports/supervisor/`, `reports/no-manual-chain-*`: supervisor-generated files, not this sprint's source work
- `src/python/abw/abw_codec.py`: has uncommitted export_to_json() from prior session — being wired into __init__ this sprint (TC-ABW-JSON-WIRE)
- All other product src/ in working tree: clean (prior session committed)

## Product tasks selected
- TC-TSV-WRITE: write_tsv() for TSV codec — completes read/write roundtrip
- TC-ABW-EDIT: edit_paragraph() for ABW — enables document editing
- TC-ABW-JSON-WIRE: export ABW export_to_json via __init__.py
- TC-FODG-PROBE: probe_fodg() for FODG codec — format detection
- Lane 7: NDJSON minimal kickstart

## Allowed paths per lane
- Lane 1: src/python/tsv/, tests/python/tsv/, examples/python/tsv/
- Lane 1: src/python/abw/, tests/python/abw/
- Lane 6: src/python/fodg/, tests/python/fodg/
- Lane 7: src/python/ndjson/ (new), tests/python/ndjson/ (new)
- Lane 2: playbooks/
- All: reports/multilane-product-first-mega-train/

## Forbidden
- src/net/ (no .NET changes this sprint)
- poc-targets.yaml (propose delta only)
- AGENTS.md, GOVERNANCE.md
- commit, push, Gate approval
