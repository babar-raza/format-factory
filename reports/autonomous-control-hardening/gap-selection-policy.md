# Gap Selection Policy

## Priority Order (highest first)

1. FODS CSV export/dogfood (commercial required)
2. FODS same-format save if required
3. FODT Markdown export/dogfood (commercial required)
4. FODT TXT export/dogfood (commercial required)
5. FODT same-format save if required
6. Netpbm same-format save/write (commercial required)
7. Netpbm pipeline/dogfood proof
8. ZST streaming/roundtrip/package/import proof (FOSS required)
9. SYLK parse/write/CSV export/roundtrip (FOSS required)
10. DIF parse/write_dif/CSV export/roundtrip (FOSS required)
11. Python Netpbm PBM/PGM/PPM parse/write/roundtrip (FOSS required)
12. Gnumeric read/export/import proof (FOSS required)

## Rules
- Lower-priority gap allowed only if: (a) it unblocks a POC-closing gap, OR
  (b) it satisfies Requirement Authority gap queue, OR (c) all higher gaps done
- If lower-priority selected: mark as SUPPORTING_DELTA, not closure delta
- Continue to POC-closing gap on next iteration

## POC-Closing vs Supporting
- POC-closing: directly closes a required target in poc-readiness-required-set.json
- Supporting: internal API that enables or deepens but doesn't close the required target

## Status as of Iteration 2
FODS: ExportSheetToCsvFile + FilterRows (SUPPORTING_DELTA — complements existing CSV export)
FODT: ExportToOutlineJson + FindParagraphsByStyle (SUPPORTING_DELTA — analytical)
Netpbm: DrawRectangle + GetBrightnessMap (SUPPORTING_DELTA — adds drawing/analysis)
SYLK: write_sylk roundtrip + CSV deepening (POC-CLOSING — SYLK parse+write+export)
ZST: file roundtrip + probe workflow (POC-CLOSING — ZST roundtrip + probe)
