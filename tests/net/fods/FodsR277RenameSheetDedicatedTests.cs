// Tests for FodsDocument.RenameSheet dedicated coverage.
// Sprint: ff-sprint-s256-dotnet-deepening-20260630
// Ledger: PC-FODS-R277

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R277: Dedicated tests for FodsDocument.RenameSheet(oldName, newName).
/// Null old name → throws exception.
/// Whitespace old name → throws exception.
/// Nonexistent old name → throws exception.
/// Null new name → throws exception.
/// Valid rename → no exception.
/// SheetCount unchanged after rename.
/// Renamed sheet accessible via new name.
/// Old name no longer in GetSheetNames.
/// New name present in GetSheetNames.
/// Dogfood: rename then add data to renamed sheet.
/// Dogfood: two sheets, rename one, other unchanged.
/// </summary>
public class FodsR277RenameSheetDedicatedTests
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
    public void RenameSheet_NonexistentOldName_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.RenameSheet("DoesNotExist", "NewName"));
    }

    [Fact]
    public void RenameSheet_NullNewName_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.RenameSheet("Sheet1", null!));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void RenameSheet_ValidRename_NoException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        var ex = Record.Exception(() => doc.RenameSheet("Sheet1", "Renamed"));
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
    public void RenameSheet_OldNameNoLongerInSheetNames()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("OldName");
        doc.RenameSheet("OldName", "NewName");
        Assert.DoesNotContain("OldName", doc.GetSheetNames());
    }

    [Fact]
    public void RenameSheet_NewNamePresentInSheetNames()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("OldName");
        doc.RenameSheet("OldName", "NewName");
        Assert.Contains("NewName", doc.GetSheetNames());
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_RenameAndAddData_DataAccessibleViaNewName()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("OriginalName");
        doc.RenameSheet("OriginalName", "RenamedSheet");
        // Add a row to the renamed sheet — should not throw
        var ex = Record.Exception(() => doc.AddRow("RenamedSheet", new[] { "val1", "val2" }));
        Assert.Null(ex);
    }

    [Fact]
    public void DogfoodPipeline_TwoSheets_RenameOne_OtherUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Alpha");
        doc.AddSheet("Beta");
        doc.RenameSheet("Alpha", "AlphaRenamed");
        // Beta should still be accessible
        var names = doc.GetSheetNames();
        Assert.Contains("Beta", names);
        Assert.Contains("AlphaRenamed", names);
        Assert.DoesNotContain("Alpha", names);
    }
}
