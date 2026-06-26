// Tests for FodsDocument.AddColumn dedicated coverage.
// Sprint: ff-sprint-s269-dotnet-deepening-20260630
// Ledger: PC-FODS-R295

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R295: Dedicated tests for FodsDocument.AddColumn(sheetName, header).
/// Null sheet name throws exception.
/// Whitespace sheet name throws exception.
/// Nonexistent sheet name throws exception.
/// Valid call no exception.
/// GetColumnCount increases after AddColumn.
/// SheetCount unchanged after AddColumn.
/// Called twice column count increases by 2.
/// Dogfood: add column with header, column count grows.
/// Dogfood: two sheets independent column counts.
/// </summary>
public class FodsR295AddColumnDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void AddColumn_NullSheetName_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.AddColumn(null!, "Header"));
    }

    [Fact]
    public void AddColumn_WhitespaceSheetName_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.AddColumn("   ", "Header"));
    }

    [Fact]
    public void AddColumn_NonexistentSheet_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.AddColumn("DoesNotExist", "Header"));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void AddColumn_ValidSheet_NoException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        var ex = Record.Exception(() => doc.AddColumn("Sheet1", "Name"));
        Assert.Null(ex);
    }

    [Fact]
    public void AddColumn_GetColumnCountIncreases()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        int before = doc.GetColumnCount("Sheet1");
        doc.AddColumn("Sheet1", "Age");
        int after = doc.GetColumnCount("Sheet1");
        Assert.True(after > before);
    }

    [Fact]
    public void AddColumn_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        int sheetsBefore = doc.SheetCount;
        doc.AddColumn("Sheet1", "Col");
        Assert.Equal(sheetsBefore, doc.SheetCount);
    }

    [Fact]
    public void AddColumn_CalledTwice_CountIncreasesByTwo()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        int before = doc.GetColumnCount("Sheet1");
        doc.AddColumn("Sheet1", "Col1");
        doc.AddColumn("Sheet1", "Col2");
        int after = doc.GetColumnCount("Sheet1");
        Assert.Equal(before + 2, after);
    }

    [Fact]
    public void AddColumn_EmptyHeader_NoException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        var ex = Record.Exception(() => doc.AddColumn("Sheet1", ""));
        Assert.Null(ex);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_AddColumnWithHeader_CountGrows()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Employees");
        int start = doc.GetColumnCount("Employees");
        doc.AddColumn("Employees", "Name");
        doc.AddColumn("Employees", "Department");
        doc.AddColumn("Employees", "Salary");
        int end = doc.GetColumnCount("Employees");
        Assert.Equal(start + 3, end);
    }

    [Fact]
    public void DogfoodPipeline_TwoSheets_IndependentColumnCounts()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.AddSheet("Sheet2");
        doc.AddColumn("Sheet1", "A");
        doc.AddColumn("Sheet2", "X");
        doc.AddColumn("Sheet2", "Y");
        int count1 = doc.GetColumnCount("Sheet1");
        int count2 = doc.GetColumnCount("Sheet2");
        Assert.NotEqual(count1, count2);
    }
}
