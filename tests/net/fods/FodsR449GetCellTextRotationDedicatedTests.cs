// Tests for FodsDocument.GetCellTextRotation dedicated coverage.
// Sprint: ff-sprint-s400-dotnet-deepening-20260701
// Ledger: PC-FODS-R449

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R449: Dedicated tests for FodsDocument.GetCellTextRotation().
/// Null/whitespace sheet name throws.
/// Nonexistent sheet name throws.
/// Negative row index throws.
/// Valid cell returns non-negative value.
/// SheetCount unchanged after GetCellTextRotation.
/// Idempotent (called twice same result).
/// SetTextRotation+GetCellTextRotation round-trips.
/// Dogfood: default cell text rotation non-negative.
/// Dogfood: multiple cells all return non-negative.
/// </summary>
public class FodsR449GetCellTextRotationDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellTextRotation_NullSheetName_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetCellTextRotation(null!, 0, 0));
    }

    [Fact]
    public void GetCellTextRotation_WhitespaceSheetName_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetCellTextRotation("   ", 0, 0));
    }

    [Fact]
    public void GetCellTextRotation_NonexistentSheet_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetCellTextRotation("NoSuchSheet", 0, 0));
    }

    [Fact]
    public void GetCellTextRotation_NegativeRow_Throws()
    {
        var doc = FodsDocument.CreateNew();
        string sheetName = doc.GetSheetName(0);
        Assert.ThrowsAny<Exception>(() => doc.GetCellTextRotation(sheetName, -1, 0));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellTextRotation_ValidCell_ReturnsNonNegative()
    {
        var doc = FodsDocument.CreateNew();
        string sheetName = doc.GetSheetName(0);
        int rotation = doc.GetCellTextRotation(sheetName, 0, 0);
        Assert.True(rotation >= 0);
    }

    [Fact]
    public void GetCellTextRotation_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        int before = doc.SheetCount;
        string sheetName = doc.GetSheetName(0);
        _ = doc.GetCellTextRotation(sheetName, 0, 0);
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetCellTextRotation_Idempotent()
    {
        var doc = FodsDocument.CreateNew();
        string sheetName = doc.GetSheetName(0);
        int first = doc.GetCellTextRotation(sheetName, 0, 0);
        int second = doc.GetCellTextRotation(sheetName, 0, 0);
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetCellTextRotation_AfterSet_RoundTrips()
    {
        var doc = FodsDocument.CreateNew();
        string sheetName = doc.GetSheetName(0);
        doc.SetCellTextRotation(sheetName, 0, 0, 45);
        int rotation = doc.GetCellTextRotation(sheetName, 0, 0);
        Assert.Equal(45, rotation);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_DefaultCell_TextRotationNonNegative()
    {
        var doc = FodsDocument.CreateNew();
        string sheetName = doc.GetSheetName(0);
        int rotation = doc.GetCellTextRotation(sheetName, 0, 0);
        Assert.True(rotation >= 0);
    }

    [Fact]
    public void DogfoodPipeline_MultipleCells_AllNonNegative()
    {
        var doc = FodsDocument.CreateNew();
        string sheetName = doc.GetSheetName(0);
        for (int row = 0; row < 3; row++)
        {
            for (int col = 0; col < 3; col++)
            {
                Assert.True(doc.GetCellTextRotation(sheetName, row, col) >= 0);
            }
        }
    }
}
