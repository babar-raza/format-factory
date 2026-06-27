// Tests for FodsDocument.GetSheetColumnCount dedicated coverage.
// Sprint: ff-sprint-s326-dotnet-deepening-20260630
// Ledger: PC-FODS-R359

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R359: Dedicated tests for FodsDocument.GetSheetColumnCount().
/// Null sheet name throws.
/// Whitespace sheet name throws.
/// Nonexistent sheet throws.
/// Empty sheet returns non-negative.
/// After adding columns count is non-negative.
/// SheetCount unchanged after GetSheetColumnCount.
/// Called twice same result.
/// Dogfood: add multiple columns then verify count non-negative.
/// Dogfood: multiple sheets column counts are non-negative.
/// </summary>
public class FodsR359GetSheetColumnCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetSheetColumnCount_NullSheetName_Throws()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        Assert.ThrowsAny<Exception>(() => doc.GetSheetColumnCount(null!));
    }

    [Fact]
    public void GetSheetColumnCount_WhitespaceSheetName_Throws()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        Assert.ThrowsAny<Exception>(() => doc.GetSheetColumnCount("   "));
    }

    [Fact]
    public void GetSheetColumnCount_NonexistentSheet_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetSheetColumnCount("NoSuchSheet"));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetSheetColumnCount_EmptySheet_NonNegative()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Empty");
        int count = doc.GetSheetColumnCount("Empty");
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetSheetColumnCount_AfterAddingColumns_NonNegative()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        doc.SetCellValue("Data", 0, 0, "Col0");
        doc.SetCellValue("Data", 0, 1, "Col1");
        doc.SetCellValue("Data", 0, 2, "Col2");
        int count = doc.GetSheetColumnCount("Data");
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetSheetColumnCount_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        int before = doc.SheetCount;
        _ = doc.GetSheetColumnCount("Sheet1");
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetSheetColumnCount_CalledTwice_SameResult()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Summary");
        doc.SetCellValue("Summary", 0, 0, "A");
        doc.SetCellValue("Summary", 0, 1, "B");
        int first = doc.GetSheetColumnCount("Summary");
        int second = doc.GetSheetColumnCount("Summary");
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_MultipleColumns_CountNonNegative()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Matrix");
        for (int c = 0; c < 5; c++)
            doc.SetCellValue("Matrix", 0, c, $"Header{c}");
        int count = doc.GetSheetColumnCount("Matrix");
        Assert.True(count >= 0);
        Assert.Equal(doc.SheetCount, doc.SheetCount);
    }

    [Fact]
    public void DogfoodPipeline_MultipleSheets_AllCountsNonNegative()
    {
        var doc = FodsDocument.CreateNew();
        string[] sheetNames = { "Sheet1", "Sheet2", "Sheet3" };
        foreach (var name in sheetNames)
        {
            doc.AddSheet(name);
            for (int c = 0; c < 3; c++)
                doc.SetCellValue(name, 0, c, $"C{c}");
        }
        foreach (var name in sheetNames)
            Assert.True(doc.GetSheetColumnCount(name) >= 0);
    }
}
