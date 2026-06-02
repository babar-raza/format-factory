# R89 FODT .NET Product Deepening (Train I)

See: reports/r89/train-hij-dotnet-product-deepening.md for full details.

## New APIs
- CharCount — character count across paragraphs
- SearchText(query, comparison) — find all occurrences with position tuples
- ReplaceText(oldText, newText, comparison) — text replacement in paragraph nodes

## Tests
FodtR89TextSearchTests.cs: 9 new tests (CharCount + SearchText)
FODT .NET total: 176 passed (was 167, +9)

## Status: COMPLETE
