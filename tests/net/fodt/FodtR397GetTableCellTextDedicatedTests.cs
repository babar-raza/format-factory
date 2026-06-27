// Tests for FodtDocument.GetTableCellText dedicated coverage.
// Sprint: ff-sprint-s379-dotnet-deepening-20260630
// Ledger: PC-FODT-R397

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R397: Dedicated tests for FodtDocument.GetTableCellText().
/// Negative table index throws.
/// Out-of-range table index throws.
/// Negative row index throws.
/// Out-of-range row index throws.
/// Negative column index throws.
/// Valid cell returns non-null.
/// TableCount unchanged after GetTableCellText.
/// Idempotent (called twice same result).
/// Dogfood: SetTableCellText then Get.
/// Dogfood: multiple cells distinct text.
/// </summary>
public class FodtR397GetTableCellTextDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetTableCellText_NegativeTableIndex_Throws()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(2, 2);
        Assert.ThrowsAny<Exception>(() => doc.GetTableCellText(-1, 0, 0));
    }

    [Fact]
    public void GetTableCellText_OutOfRangeTableIndex_Throws()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(2, 2);
        Assert.ThrowsAny<Exception>(() => doc.GetTableCellText(doc.TableCount, 0, 0));
    }

    [Fact]
    public void GetTableCellText_NegativeRowIndex_Throws()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(2, 2);
        Assert.ThrowsAny<Exception>(() => doc.GetTableCellText(0, -1, 0));
    }

    [Fact]
    public void GetTableCellText_OutOfRangeRowIndex_Throws()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(2, 2);
        Assert.ThrowsAny<Exception>(() => doc.GetTableCellText(0, 5, 0));
    }

    [Fact]
    public void GetTableCellText_NegativeColumnIndex_Throws()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(2, 2);
        Assert.ThrowsAny<Exception>(() => doc.GetTableCellText(0, 0, -1));
    }

    [Fact]
    public void GetTableCellText_ValidCell_ReturnsNonNull()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(3, 3);
        string text = doc.GetTableCellText(0, 0, 0);
        Assert.NotNull(text);
    }

    [Fact]
    public void GetTableCellText_TableCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(2, 2);
        int before = doc.TableCount;
        _ = doc.GetTableCellText(0, 0, 0);
        Assert.Equal(before, doc.TableCount);
    }

    [Fact]
    public void GetTableCellText_Idempotent()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(2, 2);
        string first = doc.GetTableCellText(0, 0, 0);
        string second = doc.GetTableCellText(0, 0, 0);
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_SetTextThenGet_ReturnsText()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(3, 3);
        doc.SetTableCellText(0, 0, 0, "Revenue");
        string text = doc.GetTableCellText(0, 0, 0);
        Assert.Equal("Revenue", text);
    }

    [Fact]
    public void DogfoodPipeline_MultipleCells_DistinctText()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(2, 3);
        doc.SetTableCellText(0, 0, 0, "Product");
        doc.SetTableCellText(0, 0, 1, "Price");
        doc.SetTableCellText(0, 0, 2, "Units");
        Assert.Equal("Product", doc.GetTableCellText(0, 0, 0));
        Assert.Equal("Price", doc.GetTableCellText(0, 0, 1));
        Assert.Equal("Units", doc.GetTableCellText(0, 0, 2));
    }
}
