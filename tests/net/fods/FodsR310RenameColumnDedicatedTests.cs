// Tests for FodsDocument.RenameColumn dedicated coverage.
// Sprint: ff-sprint-s282-dotnet-deepening-20260630
// Ledger: PC-FODS-R310

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R310: Dedicated tests for FodsDocument.RenameColumn(sheetName, oldName, newName).
/// Null sheet name throws exception.
/// Whitespace sheet name throws exception.
/// Nonexistent sheet name throws exception.
/// Null old name throws exception.
/// Null new name throws exception.
/// Nonexistent column throws exception.
/// Valid call no exception.
/// SheetCount unchanged after RenameColumn.
/// ColumnCount unchanged after RenameColumn.
/// Dogfood: add column, rename, no exception.
/// </summary>
public class FodsR310RenameColumnDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void RenameColumn_NullSheetName_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.RenameColumn(null!, "OldCol", "NewCol"));
    }

    [Fact]
    public void RenameColumn_WhitespaceSheetName_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.RenameColumn("   ", "OldCol", "NewCol"));
    }

    [Fact]
    public void RenameColumn_NonexistentSheet_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.RenameColumn("NoSuchSheet", "OldCol", "NewCol"));
    }

    [Fact]
    public void RenameColumn_NullOldName_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheet = doc.GetSheetNames().First();
        doc.AddColumn(sheet, "Col1");
        Assert.ThrowsAny<Exception>(() => doc.RenameColumn(sheet, null!, "NewCol"));
    }

    [Fact]
    public void RenameColumn_NullNewName_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheet = doc.GetSheetNames().First();
        doc.AddColumn(sheet, "Col1");
        Assert.ThrowsAny<Exception>(() => doc.RenameColumn(sheet, "Col1", null!));
    }

    [Fact]
    public void RenameColumn_NonexistentColumn_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheet = doc.GetSheetNames().First();
        Assert.ThrowsAny<Exception>(() => doc.RenameColumn(sheet, "NoSuchCol", "NewCol"));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void RenameColumn_ValidCall_NoException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheet = doc.GetSheetNames().First();
        doc.AddColumn(sheet, "OldName");
        var ex = Record.Exception(() => doc.RenameColumn(sheet, "OldName", "NewName"));
        Assert.Null(ex);
    }

    [Fact]
    public void RenameColumn_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheet = doc.GetSheetNames().First();
        doc.AddColumn(sheet, "Col1");
        int before = doc.SheetCount;
        doc.RenameColumn(sheet, "Col1", "ColRenamed");
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void RenameColumn_ColumnCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheet = doc.GetSheetNames().First();
        doc.AddColumn(sheet, "Col1");
        int before = doc.GetColumnCount(sheet);
        doc.RenameColumn(sheet, "Col1", "ColRenamed");
        Assert.Equal(before, doc.GetColumnCount(sheet));
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_AddColumnThenRename_NoException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheet = doc.GetSheetNames().First();
        doc.AddColumn(sheet, "OriginalName");
        var ex = Record.Exception(() => doc.RenameColumn(sheet, "OriginalName", "UpdatedName"));
        Assert.Null(ex);
    }
}
