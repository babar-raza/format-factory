// Tests for FodtDocument.GetTableColumnCount dedicated coverage.
// Sprint: ff-sprint-s342-dotnet-deepening-20260630
// Ledger: PC-FODT-R360

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R360: Dedicated tests for FodtDocument.GetTableColumnCount().
/// Negative table index throws.
/// Out-of-range table index throws.
/// Returns positive value for valid table.
/// ParagraphCount unchanged after GetTableColumnCount.
/// TableCount unchanged after GetTableColumnCount.
/// Idempotent (called twice same result).
/// Table created with 2 cols returns 2.
/// Table created with 5 cols returns 5.
/// Dogfood: table with content returns correct column count.
/// </summary>
public class FodtR360GetTableColumnCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetTableColumnCount_NegativeTableIndex_Throws()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(3, 4);
        Assert.ThrowsAny<Exception>(() => doc.GetTableColumnCount(-1));
    }

    [Fact]
    public void GetTableColumnCount_OutOfRangeTableIndex_Throws()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(3, 4);
        Assert.ThrowsAny<Exception>(() => doc.GetTableColumnCount(10));
    }

    [Fact]
    public void GetTableColumnCount_ValidTable_ReturnsPositive()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(2, 3);
        int count = doc.GetTableColumnCount(0);
        Assert.True(count > 0);
    }

    [Fact]
    public void GetTableColumnCount_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Body content");
        doc.AddTable(2, 3);
        int before = doc.ParagraphCount;
        _ = doc.GetTableColumnCount(0);
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void GetTableColumnCount_TableCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(2, 3);
        int before = doc.TableCount;
        _ = doc.GetTableColumnCount(0);
        Assert.Equal(before, doc.TableCount);
    }

    [Fact]
    public void GetTableColumnCount_CalledTwice_SameResult()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(3, 4);
        int first = doc.GetTableColumnCount(0);
        int second = doc.GetTableColumnCount(0);
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetTableColumnCount_TwoColumnTable_ReturnsTwo()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(3, 2);
        int count = doc.GetTableColumnCount(0);
        Assert.Equal(2, count);
    }

    [Fact]
    public void GetTableColumnCount_FiveColumnTable_ReturnsFive()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(2, 5);
        int count = doc.GetTableColumnCount(0);
        Assert.Equal(5, count);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_TableWithContent_CorrectColumnCount()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(2, 3);
        doc.SetTableCellValue(0, 0, 0, "Col1");
        doc.SetTableCellValue(0, 0, 1, "Col2");
        doc.SetTableCellValue(0, 0, 2, "Col3");
        int count = doc.GetTableColumnCount(0);
        Assert.Equal(3, count);
    }
}
