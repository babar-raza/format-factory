# Next Mainstream Prompt (R113)

## Sprint Focus
Object model deepening + cross-format export maturity.

## Commercial .NET (5+ deliverables, 3+ depth)
1. FODS: RemoveSheet API — delete sheet by name, verify save roundtrip
2. FODS: GetSheetNames API — return list of all sheet names
3. FODT: GetStyles API — extract bold/italic/font-size from paragraphs
4. FODT: GetTableCount/GetTableText — table content extraction
5. Netpbm: Crop(x, y, w, h) — extract sub-region as new image
6. Netpbm: Rotate90/Rotate180/Rotate270 — rotation transforms

## FOSS (4+ deliverables, 2+ products, 2+ roundtrip)
1. PBM: write_pbm roundtrip hardening
2. PGM: write_pgm roundtrip hardening
3. SYLK: sylk_to_csv export + roundtrip
4. DIF: Create sample DIF file for test coverage

## Dogfood (3+ deliverables, 2+ implemented)
1. PGM→PPM colorize dogfood workflow
2. FODS→JSON export→verify dogfood
3. FODT→TXT export→word count dogfood

## Governance Commands (mandatory — these are allowed)
- `python tools/supervisor/validate_product_code_ledger.py`
- `.local/venv/Scripts/python tools/supervisor/autonomous_cycle.py --declaration <path>`
- `.local/venv/Scripts/python tools/supervisor/build_declaration_review_package.py --declaration <path>`
