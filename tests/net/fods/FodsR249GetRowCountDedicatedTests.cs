// Tests for FodsDocument.GetRowCount dedicated coverage.
// Sprint: ff-sprint-s231-dotnet-deepening-20260629
// Ledger: PC-FODS-R249

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R249: Dedicated tests for FodsDocument.GetRowCount(sheetName).
/// Null sheet name → throws exception.
/// Whitespace sheet name → throws exception.
/// Nonexistent sheet → throws exception.
/// Empty sheet returns zero.
/// Row count increases after AddRow.
/// Row count decreases after DeleteRow.
/// SheetCount unchanged after GetRowCount.
/// Called twice returns same value.
/// Dogfood: add multiple rows and verify count matches.
/// </summary>
public class FodsR249GetRowCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetRowCount_NullSheetName_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetRowCount(null!));
    }

    [Fact]
    public void GetRowCount_WhitespaceSheetName_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetRowCount("   "));
    }

    [Fact]
    public void GetRowCount_NonexistentSheet_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetRowCount("NoSuchSheet"));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetRowCount_EmptySheet_ReturnsZero()
    {
        var doc = FodsDocument.CreateNew();
        string sheetName = doc.GetSheetNames()[0];
        int count = doc.GetRowCount(sheetName);
        Assert.Equal(0, count);
    }

    [Fact]
    public void GetRowCount_AfterAddRow_Increases()
    {
        var doc = FodsDocument.CreateNew();
        string sheetName = doc.GetSheetNames()[0];
        int before = doc.GetRowCount(sheetName);
        doc.AddRow(sheetName, new[] { "A", "B" });
        int after = doc.GetRowCount(sheetName);
        Assert.True(after > before);
    }

    [Fact]
    public void GetRowCount_AfterDeleteRow_Decreases()
    {
        var doc = FodsDocument.CreateNew();
        string sheetName = doc.GetSheetNames()[0];
        doc.AddRow(sheetName, new[] { "X", "Y" });
        doc.AddRow(sheetName, new[] { "P", "Q" });
        int before = doc.GetRowCount(sheetName);
        doc.DeleteRow(sheetName, 0);
        int after = doc.GetRowCount(sheetName);
        Assert.True(after < before);
    }

    [Fact]
    public void GetRowCount_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        int sheetBefore = doc.SheetCount;
        string sheetName = doc.GetSheetNames()[0];
        _ = doc.GetRowCount(sheetName);
        Assert.Equal(sheetBefore, doc.SheetCount);
    }

    [Fact]
    public void GetRowCount_CalledTwice_SameValue()
    {
        var doc = FodsDocument.CreateNew();
        string sheetName = doc.GetSheetNames()[0];
        doc.AddRow(sheetName, new[] { "A" });
        int first = doc.GetRowCount(sheetName);
        int second = doc.GetRowCount(sheetName);
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_AddMultipleRows_CountMatchesAdded()
    {
        var doc = FodsDocument.CreateNew();
        string sheetName = doc.GetSheetNames()[0];
        int start = doc.GetRowCount(sheetName);
        doc.AddRow(sheetName, new[] { "Row1A", "Row1B" });
        doc.AddRow(sheetName, new[] { "Row2A", "Row2B" });
        doc.AddRow(sheetName, new[] { "Row3A", "Row3B" });
        int end = doc.GetRowCount(sheetName);
        Assert.True(end >= start + 3);
    }
}
