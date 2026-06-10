# R106 Product Truth Map

## FODS .NET (375 tests)
- **Load/Save:** Load, Save
- **Sheet ops:** GetSheetNames, GetRowCount, InsertRow, DeleteRows, ClearSheet
- **Cell ops:** GetCellValue, SetCellValue, GetColumnHeaders (3 overloads), GetColumnValues
- **Export:** ExportSheetToHtml, ExportSheetToJson
- **Status:** 23 APIs, all test-proven

## FODT .NET (363 tests)
- **Load/Save:** Load, Save
- **Paragraph ops:** ParagraphCount, HeadingCount, AppendParagraph, RemoveParagraph, RemoveAllParagraphs, GetParagraphTexts
- **Text ops:** WordCount, CharCount, GetTextBetweenParagraphs, GetParagraphText
- **Export:** ExportToHtml, ExportToMarkdown, SearchText
- **Status:** 21 APIs, all test-proven

## Netpbm .NET (291 tests)
- **Core:** Load (P1-P6), Save, Clone, binary write (P4/P5/P6)
- **Transform:** Crop, Resize, FlipHorizontal, FlipVertical, FlipDiagonal, Rotate90/180/270
- **Image ops:** ToGrayscale, AdjustBrightness, AdjustContrast, Invert, MergeHorizontal, MergeVertical, CopyRegion, Overlay
- **Query:** GetBrightness
- **Status:** 25 APIs, all test-proven

## Python FOSS
- **ZST:** compress/decompress/roundtrip (2903 tests across all Python formats)
- **PBM:** parse/write P1/P4
- **PGM:** parse/write P2/P5
- **PPM:** parse/write P3/P6, grayscale conversion, color stats
- **SYLK:** parse/write, csv export
- **DIF:** parse, csv export
- **FODS:** parse, workbook ops, csv export
- **FODT:** parse, document ops, text export
