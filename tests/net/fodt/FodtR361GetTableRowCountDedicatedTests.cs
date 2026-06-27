// Tests for FodtDocument.GetTableRowCount dedicated coverage.
// Sprint: ff-sprint-s343-dotnet-deepening-20260630
// Ledger: PC-FODT-R361

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R361: Dedicated tests for FodtDocument.GetTableRowCount().
/// Negative table index throws.
/// Out-of-range table index throws.
/// Returns positive value for valid table.
/// ParagraphCount unchanged after GetTableRowCount.
/// TableCount unchanged after GetTableRowCount.
/// Idempotent (called twice same result).
/// Table created with 3 rows returns 3.
/// Table created with 7 rows returns 7.
/// Dogfood: table with content returns correct row count.
/// </summary>
public class FodtR361GetTableRowCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetTableRowCount_NegativeTableIndex_Throws()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(3, 4);
        Assert.ThrowsAny<Exception>(() => doc.GetTableRowCount(-1));
    }

    [Fact]
    public void GetTableRowCount_OutOfRangeTableIndex_Throws()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(3, 4);
        Assert.ThrowsAny<Exception>(() => doc.GetTableRowCount(10));
    }

    [Fact]
    public void GetTableRowCount_ValidTable_ReturnsPositive()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(4, 3);
        int count = doc.GetTableRowCount(0);
        Assert.True(count > 0);
    }

    [Fact]
    public void GetTableRowCount_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Body content");
        doc.AddTable(3, 2);
        int before = doc.ParagraphCount;
        _ = doc.GetTableRowCount(0);
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void GetTableRowCount_TableCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(3, 2);
        int before = doc.TableCount;
        _ = doc.GetTableRowCount(0);
        Assert.Equal(before, doc.TableCount);
    }

    [Fact]
    public void GetTableRowCount_CalledTwice_SameResult()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(5, 3);
        int first = doc.GetTableRowCount(0);
        int second = doc.GetTableRowCount(0);
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetTableRowCount_ThreeRowTable_ReturnsThree()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(3, 2);
        int count = doc.GetTableRowCount(0);
        Assert.Equal(3, count);
    }

    [Fact]
    public void GetTableRowCount_SevenRowTable_ReturnsSeven()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(7, 2);
        int count = doc.GetTableRowCount(0);
        Assert.Equal(7, count);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_TableWithContent_CorrectRowCount()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(4, 2);
        doc.SetTableCellValue(0, 0, 0, "Header 1");
        doc.SetTableCellValue(0, 1, 0, "Row 1");
        doc.SetTableCellValue(0, 2, 0, "Row 2");
        doc.SetTableCellValue(0, 3, 0, "Row 3");
        int count = doc.GetTableRowCount(0);
        Assert.Equal(4, count);
    }
}
