// Tests for FodsDocument.GetCellColumnWidth dedicated coverage.
// Sprint: ff-sprint-s424-dotnet-deepening-20260701
// Ledger: PC-FODS-R473

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R473: Dedicated tests for FodsDocument.GetCellColumnWidth().
/// Null sheet name throws.
/// Whitespace sheet name throws.
/// Nonexistent sheet name throws.
/// Negative column index throws.
/// Valid column returns positive value.
/// SheetCount unchanged after GetCellColumnWidth.
/// Idempotent (called twice same result).
/// Return type is double.
/// SetColumnWidth + GetCellColumnWidth round-trips.
/// Dogfood: default column width positive.
/// Dogfood: multiple columns have positive width.
/// </summary>
public class FodsR473GetCellColumnWidthDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard clause tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellColumnWidth_NullSheetName_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetCellColumnWidth(null!, 0));
    }

    [Fact]
    public void GetCellColumnWidth_WhitespaceSheetName_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetCellColumnWidth("   ", 0));
    }

    [Fact]
    public void GetCellColumnWidth_NonexistentSheet_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetCellColumnWidth("NoSuchSheet", 0));
    }

    [Fact]
    public void GetCellColumnWidth_NegativeColumn_Throws()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.GetCellColumnWidth("Sheet1", -1));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellColumnWidth_ValidColumn_ReturnsPositive()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        double width = doc.GetCellColumnWidth("Sheet1", 0);
        Assert.True(width > 0);
    }

    [Fact]
    public void GetCellColumnWidth_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        int before = doc.SheetCount;
        _ = doc.GetCellColumnWidth("Sheet1", 0);
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetCellColumnWidth_Idempotent()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        double first = doc.GetCellColumnWidth("Sheet1", 0);
        double second = doc.GetCellColumnWidth("Sheet1", 0);
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetCellColumnWidth_IsDouble()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        object result = doc.GetCellColumnWidth("Sheet1", 0);
        Assert.IsType<double>(result);
    }

    [Fact]
    public void GetCellColumnWidth_RoundTrip()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        doc.SetColumnWidth("Data", 0, 15.5);
        double width = doc.GetCellColumnWidth("Data", 0);
        Assert.Equal(15.5, width);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_DefaultColumn_WidthPositive()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Report");
        double width = doc.GetCellColumnWidth("Report", 0);
        Assert.True(width > 0);
    }

    [Fact]
    public void DogfoodPipeline_MultipleColumns_AllPositive()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        for (int col = 0; col < 5; col++)
        {
            Assert.True(doc.GetCellColumnWidth("Data", col) > 0);
        }
    }
}
