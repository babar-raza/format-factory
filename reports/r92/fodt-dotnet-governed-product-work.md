---
sprint: R92
generated_by: r92-worker
---

# FODT .NET Governed Product Work (Train M)

Sprint: FORMAT-FACTORY-R92-DECLARATION-MATERIALIZER-WORK-ITEM-GRADING-ACCELERATION-POC-MAINSTREAM-MEGA-TRAIN-001

## Objective

Advance FODT .NET toward commercial POC readiness by adding heading enumeration capability.

## Work Done

### API Added: `GetHeadingParagraphs()`

- **Skill used:** `/add-dotnet-api`
- **File:** `src/net/fodt/FodtDocument.cs`
- **Returns:** `IReadOnlyList<FodtParagraph>` of all heading paragraphs (text:h elements) in document order
- **Pre-change SHA:** `88e721ec0f58bbfa9f98beed5d4754177b1efe59d958bc2926de04c7e9ed5404`
- **Post-change SHA:** `96892fbd20c6ebf5c61f483d852cce226ee89a5fdabd79b5e189604acd90eb84`

### Tests Added

File: `tests/net/fodt/FodtR92GetHeadingParagraphsTests.cs`

| Test | Assertion |
|------|-----------|
| GetHeadingParagraphs_ReturnsOnlyHeadings | All returned items have IsHeading == true |
| GetHeadingParagraphs_CountMatchesExpected | Fixture has 4 headings (H1, H2, H3, H1) |
| GetHeadingParagraphs_TextsAreNonEmpty | All heading texts are non-whitespace |
| GetHeadingParagraphs_PreservesDocumentOrder | First = "Chapter One", Last = "Chapter Two" |
| GetHeadingParagraphs_OutlineLevelsAreCorrect | Levels match: 1, 2, 3, 1 |
| GetHeadingParagraphs_SubsetOfAllParagraphs | Headings count < Paragraphs count |
| GetHeadingParagraphs_StableAcrossMultipleCalls | Same results on repeated calls |
| GetHeadingParagraphs_ReturnsReadOnlyList | Return type is IReadOnlyList |

### Ledger Entry

- **ID:** `R92-GOVERNED-DOTNET-FODT-GETHEADINGPARAGRAPHS-001`
- **Classification:** `GOVERNED_PRODUCT_CHANGE`
- **Ledger validator:** PASS

## Test Result

```
193 passed, 0 failed (184 baseline + 8 new + 1 previously pending)
```

## POC Capability Impact

`GetHeadingParagraphs()` enables:
- Document structure analysis (extract table of contents)
- Navigation by outline level
- Heading-based content segmentation

Combined with `OutlineLevel` on `FodtParagraph`, this supports full document outline extraction.

## Status: COMPLETE — GOVERNED_PRODUCT_CHANGE ACCEPTED
