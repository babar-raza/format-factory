// Tests for FodsDocument.GetCellIndentLevel dedicated coverage.
// Sprint: ff-sprint-s418-dotnet-deepening-20260701
// Ledger: PC-FODS-R467

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R467: Dedicated tests for FodsDocument.GetCellIndentLevel().
/// Null sheet name throws.
/// Whitespace sheet name throws.
/// Nonexistent sheet name throws.
/// Negative row index throws.
/// Valid cell returns non-negative value.
/// SheetCount unchanged after GetCellIndentLevel.
/// Idempotent (called twice same result).
/// Return type is int.
/// SetCellIndentLevel + GetCellIndentLevel round-trips.
/// Dogfood: default cell indent level non-negative.
/// Dogfood: multiple cells have non-negative indent level.
/// </summary>
public class FodsR467GetCellIndentLevelDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard clause tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellIndentLevel_NullSheetName_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetCellIndentLevel(null!, 0, 0));
    }

    [Fact]
    public void GetCellIndentLevel_WhitespaceSheetName_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetCellIndentLevel("   ", 0, 0));
    }

    [Fact]
    public void GetCellIndentLevel_NonexistentSheet_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetCellIndentLevel("NoSuchSheet", 0, 0));
    }

    [Fact]
    public void GetCellIndentLevel_NegativeRow_Throws()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.GetCellIndentLevel("Sheet1", -1, 0));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellIndentLevel_ValidCell_ReturnsNonNegative()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        int level = doc.GetCellIndentLevel("Sheet1", 0, 0);
        Assert.True(level >= 0);
    }

    [Fact]
    public void GetCellIndentLevel_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        int before = doc.SheetCount;
        _ = doc.GetCellIndentLevel("Sheet1", 0, 0);
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetCellIndentLevel_Idempotent()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        int first = doc.GetCellIndentLevel("Sheet1", 0, 0);
        int second = doc.GetCellIndentLevel("Sheet1", 0, 0);
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetCellIndentLevel_IsInt()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        object result = doc.GetCellIndentLevel("Sheet1", 0, 0);
        Assert.IsType<int>(result);
    }

    [Fact]
    public void GetCellIndentLevel_RoundTrip()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        doc.SetCellIndentLevel("Data", 0, 0, 3);
        int level = doc.GetCellIndentLevel("Data", 0, 0);
        Assert.Equal(3, level);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_DefaultCell_IndentLevelNonNegative()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Report");
        int level = doc.GetCellIndentLevel("Report", 0, 0);
        Assert.True(level >= 0);
    }

    [Fact]
    public void DogfoodPipeline_MultipleCells_AllNonNegative()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        for (int row = 0; row < 3; row++)
        {
            for (int col = 0; col < 3; col++)
            {
                Assert.True(doc.GetCellIndentLevel("Data", row, col) >= 0);
            }
        }
    }
}
