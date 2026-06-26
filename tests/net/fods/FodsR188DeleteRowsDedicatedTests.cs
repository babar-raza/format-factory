// Tests for FodsDocument.DeleteRows dedicated coverage.
// Sprint: ff-sprint-s181-dotnet-deepening-20260628
// Ledger: PC-FODS-R188

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R188: Dedicated tests for FodsDocument.DeleteRows(sheetName, startRow, count).
/// Removes 'count' rows starting at startRow (zero-based) from the named sheet.
/// null/whitespace sheetName throws ArgumentException.
/// count &lt; 0 throws ArgumentOutOfRangeException.
/// count == 0 is a no-op (does not throw).
/// Nonexistent sheet throws InvalidOperationException.
/// startRow &lt; 0 or startRow+count &gt; rows.Count throws ArgumentOutOfRangeException.
/// Valid delete reduces GetRowCount by count; remaining rows shift up.
/// Covers: null/whitespace guard; count=-1 throws; count=0 no-op; nonexistent throws;
/// negative startRow throws; valid delete reduces row count; remaining rows correct;
/// delete all rows; dogfood pipeline.
/// </summary>
public class FodsR188DeleteRowsDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Theory]
    [InlineData(null)]
    [InlineData("")]
    [InlineData("   ")]
    public void DeleteRows_NullOrWhitespaceSheetName_ThrowsArgumentException(string sheetName)
    {
        var doc = FodsDocument.CreateNew();
        Assert.Throws<ArgumentException>(() => doc.DeleteRows(sheetName, 0, 1));
    }

    [Fact]
    public void DeleteRows_NegativeCount_ThrowsArgumentOutOfRangeException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        Assert.Throws<ArgumentOutOfRangeException>(() => doc.DeleteRows("Data", 0, -1));
    }

    [Fact]
    public void DeleteRows_NonexistentSheet_ThrowsInvalidOperationException()
    {
        var doc = FodsDocument.CreateNew();
        Assert.Throws<InvalidOperationException>(() => doc.DeleteRows("NoSheet", 0, 1));
    }

    [Fact]
    public void DeleteRows_NegativeStartRow_ThrowsArgumentOutOfRangeException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        doc.SetCellValue("Data", 0, 0, "Row0");
        Assert.Throws<ArgumentOutOfRangeException>(() => doc.DeleteRows("Data", -1, 1));
    }

    // -------------------------------------------------------------------------
    // No-op case
    // -------------------------------------------------------------------------

    [Fact]
    public void DeleteRows_CountZero_NoOp()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        doc.SetCellValue("Data", 0, 0, "Row0");
        var before = doc.GetRowCount("Data");
        doc.DeleteRows("Data", 0, 0);
        Assert.Equal(before, doc.GetRowCount("Data"));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void DeleteRows_ValidDelete_ReducesRowCount()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        doc.SetCellValue("Data", 0, 0, "Row0");
        doc.SetCellValue("Data", 1, 0, "Row1");
        doc.SetCellValue("Data", 2, 0, "Row2");
        var before = doc.GetRowCount("Data");
        doc.DeleteRows("Data", 0, 1);
        Assert.Equal(before - 1, doc.GetRowCount("Data"));
    }

    [Fact]
    public void DeleteRows_DeleteFirst_RemainingRowsShiftUp()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        doc.SetCellValue("Data", 0, 0, "First");
        doc.SetCellValue("Data", 1, 0, "Second");
        doc.DeleteRows("Data", 0, 1);
        Assert.Equal("Second", doc.GetCellValue("Data", 0, 0));
    }

    [Fact]
    public void DeleteRows_DeleteAll_RowCountBecomesZero()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        doc.SetCellValue("Data", 0, 0, "A");
        doc.SetCellValue("Data", 1, 0, "B");
        var count = doc.GetRowCount("Data");
        doc.DeleteRows("Data", 0, count);
        Assert.Equal(0, doc.GetRowCount("Data"));
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_AddRowsDeleteMiddle_BoundaryRowsPreserved()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Report");
        doc.SetCellValue("Report", 0, 0, "Header");
        doc.SetCellValue("Report", 1, 0, "ToDelete");
        doc.SetCellValue("Report", 2, 0, "Footer");
        doc.DeleteRows("Report", 1, 1);
        Assert.Equal("Header", doc.GetCellValue("Report", 0, 0));
        Assert.Equal("Footer", doc.GetCellValue("Report", 1, 0));
    }
}
