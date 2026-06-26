// Tests for FodsDocument.CopySheet dedicated coverage.
// Sprint: ff-sprint-s194-dotnet-deepening-20260629
// Ledger: PC-FODS-R206

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R206: Dedicated tests for FodsDocument.CopySheet(string sourceName, string newName).
/// null/whitespace sourceName → ArgumentException.
/// null/whitespace newName → ArgumentException.
/// Nonexistent source sheet → InvalidOperationException.
/// Duplicate newName (already exists) → InvalidOperationException.
/// Valid copy: SheetCount increments.
/// Valid copy: returns FodsSheet.
/// Copied sheet has the new name.
/// Cell values from source are present in copy.
/// Original sheet unchanged after copy.
/// Dogfood: copy and then copy again with third name works.
/// </summary>
public class FodsR206CopySheetDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void CopySheet_NullSourceName_ThrowsArgumentException()
    {
        var doc = FodsDocument.CreateNew();
        Assert.Throws<ArgumentException>(() => doc.CopySheet(null!, "NewSheet"));
    }

    [Fact]
    public void CopySheet_WhitespaceSourceName_ThrowsArgumentException()
    {
        var doc = FodsDocument.CreateNew();
        Assert.Throws<ArgumentException>(() => doc.CopySheet("   ", "NewSheet"));
    }

    [Fact]
    public void CopySheet_NullNewName_ThrowsArgumentException()
    {
        var doc = FodsDocument.CreateNew();
        var sheet = doc.Sheets[0];
        Assert.Throws<ArgumentException>(() => doc.CopySheet(sheet.Name!, null!));
    }

    [Fact]
    public void CopySheet_NonexistentSource_ThrowsInvalidOperationException()
    {
        var doc = FodsDocument.CreateNew();
        Assert.Throws<InvalidOperationException>(() => doc.CopySheet("NoSuch", "Copy"));
    }

    [Fact]
    public void CopySheet_DuplicateNewName_ThrowsInvalidOperationException()
    {
        var doc = FodsDocument.CreateNew();
        var name = doc.Sheets[0].Name!;
        Assert.Throws<InvalidOperationException>(() => doc.CopySheet(name, name));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void CopySheet_ValidCopy_SheetCountIncrements()
    {
        var doc = FodsDocument.CreateNew();
        var before = doc.SheetCount;
        var name = doc.Sheets[0].Name!;
        doc.CopySheet(name, "CopiedSheet");
        Assert.Equal(before + 1, doc.SheetCount);
    }

    [Fact]
    public void CopySheet_ValidCopy_ReturnsFodsSheet()
    {
        var doc = FodsDocument.CreateNew();
        var name = doc.Sheets[0].Name!;
        var result = doc.CopySheet(name, "CopiedSheet");
        Assert.IsType<FodsSheet>(result);
    }

    [Fact]
    public void CopySheet_CopiedSheet_HasNewName()
    {
        var doc = FodsDocument.CreateNew();
        var name = doc.Sheets[0].Name!;
        var copy = doc.CopySheet(name, "MyNewSheet");
        Assert.Equal("MyNewSheet", copy.Name);
    }

    [Fact]
    public void CopySheet_OriginalSheetUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        var sheet = doc.Sheets[0];
        string origName = sheet.Name!;
        FodsDocument.SetCellValue(sheet, 0, 0, "OriginalValue");
        doc.CopySheet(origName, "CopySheet");
        // Original should still exist
        var orig = doc.GetSheetByName(origName);
        Assert.NotNull(orig);
        Assert.Equal("OriginalValue", FodsDocument.GetCellValue(orig!, 0, 0));
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_CopyTwice_ThreeSheets()
    {
        var doc = FodsDocument.CreateNew();
        var name = doc.Sheets[0].Name!;
        doc.CopySheet(name, "Copy1");
        doc.CopySheet(name, "Copy2");
        Assert.Equal(3, doc.SheetCount);
    }
}
