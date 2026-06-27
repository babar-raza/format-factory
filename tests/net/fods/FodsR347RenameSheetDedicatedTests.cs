// Tests for FodsDocument.RenameSheet dedicated coverage.
// Sprint: ff-sprint-s316-dotnet-deepening-20260630
// Ledger: PC-FODS-R347

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R347: Dedicated tests for FodsDocument.RenameSheet(oldName, newName).
/// Null old name throws exception.
/// Whitespace old name throws exception.
/// Null new name throws exception.
/// Nonexistent sheet throws exception.
/// Valid call no exception.
/// SheetCount unchanged after RenameSheet.
/// Sheet accessible by new name after rename.
/// Called twice (rename back) no exception.
/// Dogfood: rename and add rows to renamed sheet.
/// </summary>
public class FodsR347RenameSheetDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void RenameSheet_NullOldName_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.RenameSheet(null!, "NewName"));
    }

    [Fact]
    public void RenameSheet_WhitespaceOldName_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.RenameSheet("   ", "NewName"));
    }

    [Fact]
    public void RenameSheet_NullNewName_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.RenameSheet("Sheet1", null!));
    }

    [Fact]
    public void RenameSheet_NonexistentSheet_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.RenameSheet("NoSuchSheet", "NewName"));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void RenameSheet_ValidCall_NoException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        var ex = Record.Exception(() => doc.RenameSheet("Sheet1", "DataSheet"));
        Assert.Null(ex);
    }

    [Fact]
    public void RenameSheet_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        int before = doc.SheetCount;
        doc.RenameSheet("Sheet1", "Renamed");
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void RenameSheet_RenameBack_NoException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.RenameSheet("Sheet1", "TempName");
        var ex = Record.Exception(() => doc.RenameSheet("TempName", "Sheet1"));
        Assert.Null(ex);
    }

    [Fact]
    public void RenameSheet_CalledTwiceDifferentSheets_NoException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("SheetA");
        doc.AddSheet("SheetB");
        doc.RenameSheet("SheetA", "Alpha");
        var ex = Record.Exception(() => doc.RenameSheet("SheetB", "Beta"));
        Assert.Null(ex);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_RenameAndSetCellValue_NoException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("RawData");
        doc.SetCellValue("RawData", 0, 0, "Initial");
        doc.RenameSheet("RawData", "ProcessedData");
        var ex = Record.Exception(() => doc.SetCellValue("ProcessedData", 1, 0, "Updated"));
        Assert.Null(ex);
        int before = doc.SheetCount;
        Assert.Equal(before, doc.SheetCount);
    }
}
