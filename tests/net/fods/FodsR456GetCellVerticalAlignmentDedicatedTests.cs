// Tests for FodsDocument.GetCellVerticalAlignment dedicated coverage.
// Sprint: ff-sprint-s407-dotnet-deepening-20260701
// Ledger: PC-FODS-R456

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R456: Dedicated tests for FodsDocument.GetCellVerticalAlignment().
/// Null/whitespace sheet name throws.
/// Nonexistent sheet name throws.
/// Negative row index throws.
/// Valid cell returns non-null.
/// SheetCount unchanged after GetCellVerticalAlignment.
/// Idempotent (called twice same result).
/// Is string type.
/// SetVerticalAlignment+Get round-trips.
/// Dogfood: default cell vertical alignment non-null.
/// Dogfood: multiple cells all non-null.
/// </summary>
public class FodsR456GetCellVerticalAlignmentDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellVerticalAlignment_NullSheetName_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetCellVerticalAlignment(null!, 0, 0));
    }

    [Fact]
    public void GetCellVerticalAlignment_WhitespaceSheetName_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetCellVerticalAlignment("   ", 0, 0));
    }

    [Fact]
    public void GetCellVerticalAlignment_NonexistentSheet_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetCellVerticalAlignment("NoSuchSheet", 0, 0));
    }

    [Fact]
    public void GetCellVerticalAlignment_NegativeRow_Throws()
    {
        var doc = FodsDocument.CreateNew();
        string sheetName = doc.GetSheetName(0);
        Assert.ThrowsAny<Exception>(() => doc.GetCellVerticalAlignment(sheetName, -1, 0));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellVerticalAlignment_ValidCell_ReturnsNonNull()
    {
        var doc = FodsDocument.CreateNew();
        string sheetName = doc.GetSheetName(0);
        string alignment = doc.GetCellVerticalAlignment(sheetName, 0, 0);
        Assert.NotNull(alignment);
    }

    [Fact]
    public void GetCellVerticalAlignment_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        int before = doc.SheetCount;
        string sheetName = doc.GetSheetName(0);
        _ = doc.GetCellVerticalAlignment(sheetName, 0, 0);
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetCellVerticalAlignment_Idempotent()
    {
        var doc = FodsDocument.CreateNew();
        string sheetName = doc.GetSheetName(0);
        string first = doc.GetCellVerticalAlignment(sheetName, 0, 0);
        string second = doc.GetCellVerticalAlignment(sheetName, 0, 0);
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetCellVerticalAlignment_IsString()
    {
        var doc = FodsDocument.CreateNew();
        string sheetName = doc.GetSheetName(0);
        object alignment = doc.GetCellVerticalAlignment(sheetName, 0, 0);
        Assert.IsType<string>(alignment);
    }

    [Fact]
    public void GetCellVerticalAlignment_AfterSet_RoundTrips()
    {
        var doc = FodsDocument.CreateNew();
        string sheetName = doc.GetSheetName(0);
        doc.SetCellVerticalAlignment(sheetName, 0, 0, "top");
        string alignment = doc.GetCellVerticalAlignment(sheetName, 0, 0);
        Assert.Equal("top", alignment);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_DefaultCell_AlignmentNonNull()
    {
        var doc = FodsDocument.CreateNew();
        string sheetName = doc.GetSheetName(0);
        string alignment = doc.GetCellVerticalAlignment(sheetName, 0, 0);
        Assert.NotNull(alignment);
    }

    [Fact]
    public void DogfoodPipeline_MultipleCells_AllNonNull()
    {
        var doc = FodsDocument.CreateNew();
        string sheetName = doc.GetSheetName(0);
        for (int row = 0; row < 3; row++)
        {
            for (int col = 0; col < 3; col++)
            {
                Assert.NotNull(doc.GetCellVerticalAlignment(sheetName, row, col));
            }
        }
    }
}
