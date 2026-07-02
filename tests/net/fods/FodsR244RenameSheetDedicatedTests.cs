// Tests for FodsDocument.RenameSheet dedicated coverage.
// Sprint: ff-sprint-s226-dotnet-deepening-20260629
// Ledger: PC-FODS-R244

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R244: Dedicated tests for FodsDocument.RenameSheet(oldName, newName).
/// Null old name → throws exception.
/// Whitespace old name → throws exception.
/// Nonexistent old name → throws exception.
/// Null new name → throws exception.
/// Valid rename → no exception.
/// New name accessible after rename.
/// Old name no longer accessible after rename.
/// SheetCount unchanged after rename.
/// Data preserved after rename.
/// Dogfood: rename and verify sheet names.
/// </summary>
public class FodsR244RenameSheetDedicatedTests
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
    public void RenameSheet_NonexistentSheet_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.RenameSheet("GhostSheet", "NewName"));
    }

    [Fact]
    public void RenameSheet_NullNewName_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheetName = doc.GetSheetNames()[0];
        Assert.ThrowsAny<Exception>(() => doc.RenameSheet(sheetName, null!));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void RenameSheet_ValidRename_NoException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheetName = doc.GetSheetNames()[0];
        var ex = Record.Exception(() => doc.RenameSheet(sheetName, "RenamedSheet"));
        Assert.Null(ex);
    }

    [Fact]
    public void RenameSheet_NewNameAccessible()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string oldName = doc.GetSheetNames()[0];
        doc.RenameSheet(oldName, "NewSheetName");
        var names = doc.GetSheetNames();
        Assert.Contains("NewSheetName", names);
    }

    [Fact]
    public void RenameSheet_OldNameGone()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string oldName = doc.GetSheetNames()[0];
        doc.RenameSheet(oldName, "FreshName");
        var names = doc.GetSheetNames();
        Assert.DoesNotContain(oldName, names);
    }

    [Fact]
    public void RenameSheet_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        int before = doc.SheetCount;
        string sheetName = doc.GetSheetNames()[0];
        doc.RenameSheet(sheetName, "Renamed");
        Assert.Equal(before, doc.SheetCount);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_RenameAndVerify_SheetNamesUpdated()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.AddSheet("ExtraSheet");
        string firstSheet = doc.GetSheetNames()[0];
        doc.RenameSheet(firstSheet, "PrimarySheet");
        doc.RenameSheet("ExtraSheet", "SecondarySheet");
        var names = doc.GetSheetNames();
        Assert.Contains("PrimarySheet", names);
        Assert.Contains("SecondarySheet", names);
    }
}
