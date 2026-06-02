# R89 Netpbm .NET Product Deepening (Train J)

See: reports/r89/train-hij-dotnet-product-deepening.md for full details.

## New APIs
- GetChannelStats() — per-channel (R,G,B) statistics for PPM
- Rotate90Cw() — 90-degree clockwise rotation, returns new image
- Crop(top, left, height, width) — extract rectangular sub-region

## Tests
NetpbmR89ProductDeepeningTests.cs: 23 new tests (stats + rotate + crop)
Netpbm .NET total: 94 passed (was 71, +23)

## Status: COMPLETE
