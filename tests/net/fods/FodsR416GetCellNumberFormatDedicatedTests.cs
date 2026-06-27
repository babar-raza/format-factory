// Tests for FodsDocument.GetCellNumberFormat dedicated coverage.
// Sprint: ff-sprint-s373-dotnet-deepening-20260630
// Ledger: PC-FODS-R416

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R416: Dedicated tests for FodsDocument.GetCellNumberFormat().
/// Null sheet name throws.
/// Whitespace sheet name throws.
/// Non-existent sheet name throws.
/// Negative row index throws.
/// Valid cell returns non-null.
/// SheetCount unchanged after GetCellNumberFormat.
/// Idempotent (called twice same result).
/// Dogfood: SetNumberFormat #,##0.00 then Get.
/// Dogfood: multiple cells each has distinct format.
/// </summary>
public class FodsR416GetCellNumberFormatDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
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
    public void GetCellNumberFormat_NonExistentSheet_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetCellNumberFormat("Missing", 0, 0));
    }

    [Fact]
    public void GetCellNumberFormat_NegativeRow_Throws()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        Assert.ThrowsAny<Exception>(() => doc.GetCellNumberFormat("Data", -1, 0));
    }

    [Fact]
    public void GetCellNumberFormat_ValidCell_ReturnsNonNull()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Finance");
        string fmt = doc.GetCellNumberFormat("Finance", 0, 0);
        Assert.NotNull(fmt);
    }

    [Fact]
    public void GetCellNumberFormat_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        int before = doc.SheetCount;
        _ = doc.GetCellNumberFormat("Data", 0, 0);
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetCellNumberFormat_Idempotent()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Stable");
        string first = doc.GetCellNumberFormat("Stable", 0, 0);
        string second = doc.GetCellNumberFormat("Stable", 0, 0);
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_SetNumberFormatThenGet_ReturnsFormat()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Budget");
        doc.SetCellNumberFormat("Budget", 0, 0, "#,##0.00");
        string fmt = doc.GetCellNumberFormat("Budget", 0, 0);
        Assert.Equal("#,##0.00", fmt);
    }

    [Fact]
    public void DogfoodPipeline_MultipleCells_DistinctFormats()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Report");
        doc.SetCellNumberFormat("Report", 0, 0, "#,##0.00");
        doc.SetCellNumberFormat("Report", 1, 0, "0.00%");
        doc.SetCellNumberFormat("Report", 2, 0, "yyyy-MM-dd");
        Assert.Equal("#,##0.00", doc.GetCellNumberFormat("Report", 0, 0));
        Assert.Equal("0.00%", doc.GetCellNumberFormat("Report", 1, 0));
        Assert.Equal("yyyy-MM-dd", doc.GetCellNumberFormat("Report", 2, 0));
    }
}
