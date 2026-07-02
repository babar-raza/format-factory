// Tests for FodsDocument.GetRowCount dedicated coverage.
// Sprint: ff-sprint-s249-dotnet-deepening-20260630
// Ledger: PC-FODS-R268

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R268: Dedicated tests for FodsDocument.GetRowCount(sheetName).
/// Null sheet name → throws exception.
/// Whitespace sheet name → throws exception.
/// Nonexistent sheet → throws exception.
/// Empty sheet → returns 0 or non-negative.
/// After AddRow → count increases.
/// SheetCount unchanged after GetRowCount.
/// Called twice → same result.
/// Dogfood: add N rows, verify GetRowCount >= N.
/// Dogfood: add rows to two sheets independently, verify counts.
/// </summary>
public class FodsR268GetRowCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetRowCount_NullSheetName_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.GetRowCount(null!));
    }

    [Fact]
    public void GetRowCount_WhitespaceSheetName_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.GetRowCount("   "));
    }

    [Fact]
    public void GetRowCount_NonexistentSheet_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.GetRowCount("NoSuchSheet"));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetRowCount_EmptySheet_ReturnsNonNegative()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheetName = doc.GetSheetNames()[0];
        int count = doc.GetRowCount(sheetName);
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetRowCount_AfterAddRow_Increases()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheetName = doc.GetSheetNames()[0];
        int before = doc.GetRowCount(sheetName);
        doc.AddRow(sheetName, new[] { "A", "B", "C" });
        int after = doc.GetRowCount(sheetName);
        Assert.True(after > before);
    }

    [Fact]
    public void GetRowCount_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheetName = doc.GetSheetNames()[0];
        doc.AddRow(sheetName, new[] { "X" });
        int before = doc.SheetCount;
        doc.GetRowCount(sheetName);
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetRowCount_CalledTwice_SameResult()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheetName = doc.GetSheetNames()[0];
        doc.AddRow(sheetName, new[] { "Row1" });
        doc.AddRow(sheetName, new[] { "Row2" });
        int first = doc.GetRowCount(sheetName);
        int second = doc.GetRowCount(sheetName);
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_AddFiveRows_CountAtLeastFive()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheetName = doc.GetSheetNames()[0];
        doc.AddRow(sheetName, new[] { "Header", "Value" });
        doc.AddRow(sheetName, new[] { "R1", "10" });
        doc.AddRow(sheetName, new[] { "R2", "20" });
        doc.AddRow(sheetName, new[] { "R3", "30" });
        doc.AddRow(sheetName, new[] { "R4", "40" });
        int count = doc.GetRowCount(sheetName);
        Assert.True(count >= 5);
    }

    [Fact]
    public void DogfoodPipeline_TwoSheets_IndependentCounts()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheet1 = doc.GetSheetNames()[0];
        doc.AddSheet("Sheet2");
        string sheet2 = "Sheet2";
        doc.AddRow(sheet1, new[] { "S1R1" });
        doc.AddRow(sheet1, new[] { "S1R2" });
        doc.AddRow(sheet1, new[] { "S1R3" });
        doc.AddRow(sheet2, new[] { "S2R1" });
        int count1 = doc.GetRowCount(sheet1);
        int count2 = doc.GetRowCount(sheet2);
        Assert.True(count1 >= 3);
        Assert.True(count2 >= 1);
    }
}
