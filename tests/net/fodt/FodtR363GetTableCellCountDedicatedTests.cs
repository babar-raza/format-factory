// Tests for FodtDocument.GetTableCellCount dedicated coverage.
// Sprint: ff-sprint-s345-dotnet-deepening-20260630
// Ledger: PC-FODT-R363

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R363: Dedicated tests for FodtDocument.GetTableCellCount().
/// Negative table index throws.
/// Out-of-range table index throws.
/// Valid table returns positive count.
/// ParagraphCount unchanged after GetTableCellCount.
/// TableCount unchanged after GetTableCellCount.
/// Idempotent (called twice same result).
/// 2x3 table returns 6 cells.
/// 4x5 table returns 20 cells.
/// Dogfood: table with content correct cell count.
/// </summary>
public class FodtR363GetTableCellCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetTableCellCount_NegativeTableIndex_Throws()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(3, 3, "Grid");
        Assert.ThrowsAny<Exception>(() => doc.GetTableCellCount(-1));
    }

    [Fact]
    public void GetTableCellCount_OutOfRangeTableIndex_Throws()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(3, 3, "Grid");
        Assert.ThrowsAny<Exception>(() => doc.GetTableCellCount(10));
    }

    [Fact]
    public void GetTableCellCount_ValidTable_ReturnsPositive()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(2, 4, "Report");
        int count = doc.GetTableCellCount(0);
        Assert.True(count > 0);
    }

    [Fact]
    public void GetTableCellCount_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Introduction");
        doc.AddTable(3, 3, "Data");
        int before = doc.ParagraphCount;
        _ = doc.GetTableCellCount(0);
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void GetTableCellCount_TableCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(2, 2, "Summary");
        int before = doc.TableCount;
        _ = doc.GetTableCellCount(0);
        Assert.Equal(before, doc.TableCount);
    }

    [Fact]
    public void GetTableCellCount_CalledTwice_SameResult()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(3, 4, "Stable");
        int first = doc.GetTableCellCount(0);
        int second = doc.GetTableCellCount(0);
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetTableCellCount_TwoByThreeTable_ReturnsSix()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(2, 3, "Small");
        int count = doc.GetTableCellCount(0);
        Assert.Equal(6, count);
    }

    [Fact]
    public void GetTableCellCount_FourByFiveTable_ReturnsTwenty()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(4, 5, "Large");
        int count = doc.GetTableCellCount(0);
        Assert.Equal(20, count);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_TableWithContent_ReturnsCorrectCount()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(3, 3, "Employee Data");
        doc.SetTableCellValue(0, 0, 0, "Name");
        doc.SetTableCellValue(0, 0, 1, "Department");
        doc.SetTableCellValue(0, 0, 2, "Salary");
        doc.SetTableCellValue(0, 1, 0, "Alice");
        doc.SetTableCellValue(0, 1, 1, "Engineering");
        doc.SetTableCellValue(0, 1, 2, "95000");
        doc.SetTableCellValue(0, 2, 0, "Bob");
        doc.SetTableCellValue(0, 2, 1, "Marketing");
        doc.SetTableCellValue(0, 2, 2, "82000");
        int count = doc.GetTableCellCount(0);
        Assert.Equal(9, count);
    }
}
