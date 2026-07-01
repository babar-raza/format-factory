// Tests for FodsDocument.GetCellRotationAngle dedicated coverage.
// Sprint: ff-sprint-s419-dotnet-deepening-20260701
// Ledger: PC-FODS-R468

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R468: Dedicated tests for FodsDocument.GetCellRotationAngle().
/// Null sheet name throws.
/// Whitespace sheet name throws.
/// Nonexistent sheet name throws.
/// Negative row index throws.
/// Valid cell returns non-negative int.
/// SheetCount unchanged after GetCellRotationAngle.
/// Idempotent (called twice same result).
/// Return type is int.
/// SetCellRotationAngle + GetCellRotationAngle round-trips.
/// Dogfood: default cell rotation angle non-negative.
/// Dogfood: multiple cells have non-negative rotation angle.
/// </summary>
public class FodsR468GetCellRotationAngleDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard clause tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellRotationAngle_NullSheetName_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetCellRotationAngle(null!, 0, 0));
    }

    [Fact]
    public void GetCellRotationAngle_WhitespaceSheetName_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetCellRotationAngle("   ", 0, 0));
    }

    [Fact]
    public void GetCellRotationAngle_NonexistentSheet_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetCellRotationAngle("NoSuchSheet", 0, 0));
    }

    [Fact]
    public void GetCellRotationAngle_NegativeRow_Throws()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.GetCellRotationAngle("Sheet1", -1, 0));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellRotationAngle_ValidCell_ReturnsNonNegative()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        int angle = doc.GetCellRotationAngle("Sheet1", 0, 0);
        Assert.True(angle >= 0);
    }

    [Fact]
    public void GetCellRotationAngle_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        int before = doc.SheetCount;
        _ = doc.GetCellRotationAngle("Sheet1", 0, 0);
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetCellRotationAngle_Idempotent()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        int first = doc.GetCellRotationAngle("Sheet1", 0, 0);
        int second = doc.GetCellRotationAngle("Sheet1", 0, 0);
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetCellRotationAngle_IsInt()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        object result = doc.GetCellRotationAngle("Sheet1", 0, 0);
        Assert.IsType<int>(result);
    }

    [Fact]
    public void GetCellRotationAngle_RoundTrip()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        doc.SetCellRotationAngle("Data", 0, 0, 45);
        int angle = doc.GetCellRotationAngle("Data", 0, 0);
        Assert.Equal(45, angle);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_DefaultCell_RotationAngleNonNegative()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Report");
        int angle = doc.GetCellRotationAngle("Report", 0, 0);
        Assert.True(angle >= 0);
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
                Assert.True(doc.GetCellRotationAngle("Data", row, col) >= 0);
            }
        }
    }
}
