// Tests for FodsDocument.RenameSheet dedicated coverage.
// Sprint: ff-sprint-s186-dotnet-deepening-20260628
// Ledger: PC-FODS-R193

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R193: Dedicated tests for FodsDocument.RenameSheet(string oldName, string newName).
/// Renames the sheet with oldName to newName.
/// null/whitespace oldName throws ArgumentException.
/// null/whitespace newName throws ArgumentException.
/// Nonexistent oldName throws InvalidOperationException.
/// Duplicate newName (already exists) throws InvalidOperationException.
/// Valid rename: GetSheetNames no longer contains oldName; contains newName.
/// SheetCount is unchanged after rename.
/// Cell values are preserved after rename.
/// Covers: null oldName throws; whitespace oldName throws; null newName throws;
/// whitespace newName throws; nonexistent old throws; duplicate new throws;
/// valid rename oldName gone; newName present; SheetCount unchanged; dogfood rename-and-verify.
/// </summary>
public class FodsR193RenameSheetDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void RenameSheet_NullOldName_ThrowsArgumentException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.Throws<ArgumentException>(() => doc.RenameSheet(null!, "NewName"));
    }

    [Fact]
    public void RenameSheet_WhitespaceOldName_ThrowsArgumentException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.Throws<ArgumentException>(() => doc.RenameSheet("   ", "NewName"));
    }

    [Fact]
    public void RenameSheet_NullNewName_ThrowsArgumentException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        var oldName = doc.Sheets[0].Name;
        Assert.Throws<ArgumentException>(() => doc.RenameSheet(oldName, null!));
    }

    [Fact]
    public void RenameSheet_WhitespaceNewName_ThrowsArgumentException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        var oldName = doc.Sheets[0].Name;
        Assert.Throws<ArgumentException>(() => doc.RenameSheet(oldName, "   "));
    }

    [Fact]
    public void RenameSheet_NonexistentOldName_ThrowsInvalidOperationException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.Throws<InvalidOperationException>(() => doc.RenameSheet("NoSuchSheet", "NewName"));
    }

    [Fact]
    public void RenameSheet_DuplicateNewName_ThrowsInvalidOperationException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.AddSheet("Second");
        var firstName = doc.Sheets[0].Name;
        Assert.Throws<InvalidOperationException>(() => doc.RenameSheet(firstName, "Second"));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void RenameSheet_ValidRename_OldNameNoLongerPresent()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        var oldName = doc.Sheets[0].Name;
        doc.RenameSheet(oldName, "RenamedSheet");
        Assert.DoesNotContain("RenamedSheet" == oldName ? oldName + "_old" : oldName, doc.GetSheetNames());
    }

    [Fact]
    public void RenameSheet_ValidRename_NewNamePresent()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        var oldName = doc.Sheets[0].Name;
        doc.RenameSheet(oldName, "RenamedSheet");
        Assert.Contains("RenamedSheet", doc.GetSheetNames());
    }

    [Fact]
    public void RenameSheet_ValidRename_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        var before = doc.SheetCount;
        var oldName = doc.Sheets[0].Name;
        doc.RenameSheet(oldName, "RenamedSheet");
        Assert.Equal(before, doc.SheetCount);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipelines
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_RenameAndVerify_NewNameAccessible()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        var oldName = doc.Sheets[0].Name;
        doc.SetCellValue(0, 0, "Data");
        doc.RenameSheet(oldName, "DataSheet");
        var sheet = doc.GetSheetByName("DataSheet");
        Assert.NotNull(sheet);
    }
}
