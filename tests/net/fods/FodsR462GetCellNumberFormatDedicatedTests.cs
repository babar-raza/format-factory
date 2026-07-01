// Tests for FodsDocument.GetCellNumberFormat dedicated coverage.
// Sprint: ff-sprint-s413-dotnet-deepening-20260701
// Ledger: PC-FODS-R462

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R462: Dedicated tests for FodsDocument.GetCellNumberFormat().
/// Null sheet name throws.
/// Whitespace sheet name throws.
/// Nonexistent sheet name throws.
/// Negative row index throws.
/// Valid cell returns non-null string.
/// SheetCount unchanged after GetCellNumberFormat.
/// Idempotent (called twice same result).
/// Return type is string.
/// SetNumberFormat + GetCellNumberFormat round-trips.
/// Dogfood: default cell number format non-null.
/// Dogfood: multiple cells have non-null number format.
/// </summary>
public class FodsR462GetCellNumberFormatDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard clause tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellNumberFormat_NullSheetName_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetCellNumberFormat(null!, 0, 0));
    }

    [Fact]
    public void GetCellNumberFormat_WhitespaceSheetName_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetCellNumberFormat("   ", 0, 0));
    }

    [Fact]
    public void GetCellNumberFormat_NonexistentSheet_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetCellNumberFormat("NoSuchSheet", 0, 0));
    }

    [Fact]
    public void GetCellNumberFormat_NegativeRow_Throws()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.GetCellNumberFormat("Sheet1", -1, 0));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellNumberFormat_ValidCell_ReturnsNonNull()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string fmt = doc.GetCellNumberFormat("Sheet1", 0, 0);
        Assert.NotNull(fmt);
    }

    [Fact]
    public void GetCellNumberFormat_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        int before = doc.SheetCount;
        _ = doc.GetCellNumberFormat("Sheet1", 0, 0);
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetCellNumberFormat_Idempotent()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string first = doc.GetCellNumberFormat("Sheet1", 0, 0);
        string second = doc.GetCellNumberFormat("Sheet1", 0, 0);
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetCellNumberFormat_IsString()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        object result = doc.GetCellNumberFormat("Sheet1", 0, 0);
        Assert.IsType<string>(result);
    }

    [Fact]
    public void GetCellNumberFormat_RoundTrip()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        doc.SetCellNumberFormat("Data", 0, 0, "0.00");
        string fmt = doc.GetCellNumberFormat("Data", 0, 0);
        Assert.Equal("0.00", fmt);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_DefaultCell_NumberFormatNonNull()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Report");
        string fmt = doc.GetCellNumberFormat("Report", 0, 0);
        Assert.NotNull(fmt);
    }

    [Fact]
    public void DogfoodPipeline_MultipleCells_AllNonNull()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        for (int row = 0; row < 3; row++)
        {
            for (int col = 0; col < 3; col++)
            {
                string fmt = doc.GetCellNumberFormat("Data", row, col);
                Assert.NotNull(fmt);
            }
        }
    }
}
