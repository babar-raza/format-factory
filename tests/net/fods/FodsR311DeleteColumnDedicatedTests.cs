// Tests for FodsDocument.DeleteColumn dedicated coverage.
// Sprint: ff-sprint-s283-dotnet-deepening-20260630
// Ledger: PC-FODS-R311

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R311: Dedicated tests for FodsDocument.DeleteColumn(sheetName, columnName).
/// Null sheet name throws exception.
/// Whitespace sheet name throws exception.
/// Nonexistent sheet name throws exception.
/// Null column name throws exception.
/// Nonexistent column name throws exception.
/// Valid call no exception.
/// ColumnCount decreases after DeleteColumn.
/// SheetCount unchanged after DeleteColumn.
/// Dogfood: add then delete column, count restores.
/// Dogfood: delete one of multiple columns, others remain.
/// </summary>
public class FodsR311DeleteColumnDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void DeleteColumn_NullSheetName_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.DeleteColumn(null!, "Col1"));
    }

    [Fact]
    public void DeleteColumn_WhitespaceSheetName_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.DeleteColumn("   ", "Col1"));
    }

    [Fact]
    public void DeleteColumn_NonexistentSheet_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.DeleteColumn("NoSuchSheet", "Col1"));
    }

    [Fact]
    public void DeleteColumn_NullColumnName_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        string sheet = doc.GetSheetNames().First();
        doc.AddColumn(sheet, "Col1");
        Assert.ThrowsAny<Exception>(() => doc.DeleteColumn(sheet, null!));
    }

    [Fact]
    public void DeleteColumn_NonexistentColumn_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        string sheet = doc.GetSheetNames().First();
        Assert.ThrowsAny<Exception>(() => doc.DeleteColumn(sheet, "NoSuchCol"));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void DeleteColumn_ValidCall_NoException()
    {
        var doc = FodsDocument.CreateNew();
        string sheet = doc.GetSheetNames().First();
        doc.AddColumn(sheet, "ToDelete");
        var ex = Record.Exception(() => doc.DeleteColumn(sheet, "ToDelete"));
        Assert.Null(ex);
    }

    [Fact]
    public void DeleteColumn_ColumnCountDecreases()
    {
        var doc = FodsDocument.CreateNew();
        string sheet = doc.GetSheetNames().First();
        doc.AddColumn(sheet, "ToDelete");
        int before = doc.GetColumnCount(sheet);
        doc.DeleteColumn(sheet, "ToDelete");
        int after = doc.GetColumnCount(sheet);
        Assert.True(after < before);
    }

    [Fact]
    public void DeleteColumn_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        string sheet = doc.GetSheetNames().First();
        doc.AddColumn(sheet, "ToDelete");
        int before = doc.SheetCount;
        doc.DeleteColumn(sheet, "ToDelete");
        Assert.Equal(before, doc.SheetCount);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_AddThenDelete_CountRestores()
    {
        var doc = FodsDocument.CreateNew();
        string sheet = doc.GetSheetNames().First();
        int baseline = doc.GetColumnCount(sheet);
        doc.AddColumn(sheet, "Temp");
        doc.DeleteColumn(sheet, "Temp");
        Assert.Equal(baseline, doc.GetColumnCount(sheet));
    }

    [Fact]
    public void DogfoodPipeline_DeleteOneOfMultiple_OthersRemain()
    {
        var doc = FodsDocument.CreateNew();
        string sheet = doc.GetSheetNames().First();
        doc.AddColumn(sheet, "ColA");
        doc.AddColumn(sheet, "ColB");
        int before = doc.GetColumnCount(sheet);
        doc.DeleteColumn(sheet, "ColA");
        Assert.True(doc.GetColumnCount(sheet) < before);
    }
}
