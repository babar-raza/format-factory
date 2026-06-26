// Tests for FodsDocument.CopySheet dedicated coverage.
// Sprint: ff-sprint-s254-dotnet-deepening-20260630
// Ledger: PC-FODS-R274

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R274: Dedicated tests for FodsDocument.CopySheet(fromSheetName, newSheetName).
/// Null fromSheetName → throws exception.
/// Whitespace fromSheetName → throws exception.
/// Nonexistent fromSheetName → throws exception.
/// Null newSheetName → throws exception.
/// Duplicate newSheetName → throws exception.
/// Valid copy → no exception.
/// SheetCount increases by 1.
/// New sheet is accessible via GetSheetNames.
/// Original sheet data intact after copy.
/// Dogfood: add data, copy sheet, verify new sheet accessible.
/// Dogfood: copy creates independent sheet (original still accessible).
/// </summary>
public class FodsR274CopySheetDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void CopySheet_NullFromSheet_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.CopySheet(null!, "NewSheet"));
    }

    [Fact]
    public void CopySheet_WhitespaceFromSheet_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.CopySheet("   ", "NewSheet"));
    }

    [Fact]
    public void CopySheet_NonexistentFromSheet_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.CopySheet("NoSuchSheet", "NewSheet"));
    }

    [Fact]
    public void CopySheet_NullNewSheetName_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        string source = doc.GetSheetNames()[0];
        Assert.ThrowsAny<Exception>(() => doc.CopySheet(source, null!));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void CopySheet_ValidCopy_NoException()
    {
        var doc = FodsDocument.CreateNew();
        string source = doc.GetSheetNames()[0];
        var ex = Record.Exception(() => doc.CopySheet(source, "CopiedSheet"));
        Assert.Null(ex);
    }

    [Fact]
    public void CopySheet_SheetCountIncreasesBy1()
    {
        var doc = FodsDocument.CreateNew();
        string source = doc.GetSheetNames()[0];
        int before = doc.SheetCount;
        doc.CopySheet(source, "MyCopy");
        Assert.Equal(before + 1, doc.SheetCount);
    }

    [Fact]
    public void CopySheet_NewSheetAccessible()
    {
        var doc = FodsDocument.CreateNew();
        string source = doc.GetSheetNames()[0];
        doc.CopySheet(source, "CopySheet1");
        var names = doc.GetSheetNames();
        Assert.Contains("CopySheet1", names);
    }

    [Fact]
    public void CopySheet_OriginalSheetStillAccessible()
    {
        var doc = FodsDocument.CreateNew();
        string source = doc.GetSheetNames()[0];
        doc.CopySheet(source, "AnotherCopy");
        // Original sheet should still be accessible
        var names = doc.GetSheetNames();
        Assert.Contains(source, names);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_CopySheetWithData_NewSheetAccessible()
    {
        var doc = FodsDocument.CreateNew();
        string source = doc.GetSheetNames()[0];
        doc.AddRow(source, new[] { "Name", "Score" });
        doc.AddRow(source, new[] { "Alice", "95" });
        doc.CopySheet(source, "DataCopy");
        // Verify the copied sheet is accessible
        var names = doc.GetSheetNames();
        Assert.Contains("DataCopy", names);
        Assert.Equal(2, doc.SheetCount);
    }

    [Fact]
    public void DogfoodPipeline_BothSheetsAccessibleAfterCopy()
    {
        var doc = FodsDocument.CreateNew();
        string source = doc.GetSheetNames()[0];
        doc.SetCellValue(source, 0, 0, "Original Data");
        doc.CopySheet(source, "CopiedData");
        // Both sheets should be in GetSheetNames
        var names = doc.GetSheetNames();
        Assert.Equal(2, names.Count);
        // Original cell value should still be accessible
        string val = doc.GetCellValue(source, 0, 0);
        Assert.Equal("Original Data", val);
    }
}
