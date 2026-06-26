// Tests for FodsDocument.CopySheet dedicated coverage.
// Sprint: ff-sprint-s180-dotnet-deepening-20260628
// Ledger: PC-FODS-R187

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R187: Dedicated tests for FodsDocument.CopySheet(sourceName, newName).
/// Creates a deep copy of the source sheet with a new name.
/// null/whitespace sourceName throws ArgumentException.
/// null/whitespace newName throws ArgumentException.
/// Nonexistent source throws InvalidOperationException.
/// Duplicate new name throws InvalidOperationException.
/// Valid copy: SheetCount incremented; new sheet findable; data copied.
/// Covers: null source throws; whitespace source throws; null new throws;
/// nonexistent source throws; duplicate new name throws;
/// valid copy increments SheetCount; new sheet findable by name;
/// copy has same data; original sheet unchanged; dogfood pipeline.
/// </summary>
public class FodsR187CopySheetDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Theory]
    [InlineData(null)]
    [InlineData("")]
    [InlineData("   ")]
    public void CopySheet_NullOrWhitespaceSourceName_ThrowsArgumentException(string source)
    {
        var doc = FodsDocument.CreateNew();
        Assert.Throws<ArgumentException>(() => doc.CopySheet(source, "NewSheet"));
    }

    [Theory]
    [InlineData(null)]
    [InlineData("")]
    [InlineData("   ")]
    public void CopySheet_NullOrWhitespaceNewName_ThrowsArgumentException(string newName)
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Source");
        Assert.Throws<ArgumentException>(() => doc.CopySheet("Source", newName));
    }

    [Fact]
    public void CopySheet_NonexistentSource_ThrowsInvalidOperationException()
    {
        var doc = FodsDocument.CreateNew();
        Assert.Throws<InvalidOperationException>(() => doc.CopySheet("NoSuchSheet", "Copy"));
    }

    [Fact]
    public void CopySheet_DuplicateNewName_ThrowsInvalidOperationException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Source");
        doc.AddSheet("Existing");
        Assert.Throws<InvalidOperationException>(() => doc.CopySheet("Source", "Existing"));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void CopySheet_ValidCopy_SheetCountIncrements()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Original");
        var before = doc.SheetCount;
        doc.CopySheet("Original", "Duplicate");
        Assert.Equal(before + 1, doc.SheetCount);
    }

    [Fact]
    public void CopySheet_ValidCopy_NewSheetFindable()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Original");
        doc.CopySheet("Original", "Copy");
        Assert.NotNull(doc.GetSheetByName("Copy"));
    }

    [Fact]
    public void CopySheet_ValidCopy_DataCopiedToNewSheet()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Source");
        doc.SetCellValue("Source", 0, 0, "CopiedData");
        doc.CopySheet("Source", "Dest");
        Assert.Equal("CopiedData", doc.GetCellValue("Dest", 0, 0));
    }

    [Fact]
    public void CopySheet_ValidCopy_OriginalSheetUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Source");
        doc.SetCellValue("Source", 0, 0, "OriginalData");
        doc.CopySheet("Source", "Dest");
        Assert.Equal("OriginalData", doc.GetCellValue("Source", 0, 0));
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_CopyModifyOriginal_CopyUnaffected()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("A");
        doc.SetCellValue("A", 0, 0, "Shared");
        doc.CopySheet("A", "B");
        // Modify original after copy
        doc.SetCellValue("A", 0, 0, "Modified");
        // The copy retains the old value
        Assert.Equal("Shared", doc.GetCellValue("B", 0, 0));
    }
}
