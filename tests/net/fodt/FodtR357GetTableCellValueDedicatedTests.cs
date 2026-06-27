// Tests for FodtDocument.GetTableCellValue dedicated coverage.
// Sprint: ff-sprint-s339-dotnet-deepening-20260630
// Ledger: PC-FODT-R357

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R357: Dedicated tests for FodtDocument.GetTableCellValue().
/// Negative table index throws.
/// Out-of-range table index throws.
/// Negative row index throws.
/// Negative column index throws.
/// Valid cell returns non-null.
/// ParagraphCount unchanged after GetTableCellValue.
/// TableCount unchanged after GetTableCellValue.
/// Idempotent (called twice same result).
/// After SetTableCellValue returns correct value.
/// Dogfood: multiple cells in same table each return correct value.
/// </summary>
public class FodtR357GetTableCellValueDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetTableCellValue_NegativeTableIndex_Throws()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(2, 2);
        Assert.ThrowsAny<Exception>(() => doc.GetTableCellValue(-1, 0, 0));
    }

    [Fact]
    public void GetTableCellValue_OutOfRangeTableIndex_Throws()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(2, 2);
        Assert.ThrowsAny<Exception>(() => doc.GetTableCellValue(5, 0, 0));
    }

    [Fact]
    public void GetTableCellValue_NegativeRowIndex_Throws()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(2, 2);
        Assert.ThrowsAny<Exception>(() => doc.GetTableCellValue(0, -1, 0));
    }

    [Fact]
    public void GetTableCellValue_NegativeColumnIndex_Throws()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(2, 2);
        Assert.ThrowsAny<Exception>(() => doc.GetTableCellValue(0, 0, -1));
    }

    [Fact]
    public void GetTableCellValue_ValidCell_ReturnsNonNull()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(3, 3);
        string? value = doc.GetTableCellValue(0, 0, 0);
        Assert.NotNull(value);
    }

    [Fact]
    public void GetTableCellValue_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Some content");
        doc.AddTable(2, 2);
        int before = doc.ParagraphCount;
        _ = doc.GetTableCellValue(0, 0, 0);
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void GetTableCellValue_TableCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(2, 2);
        int before = doc.TableCount;
        _ = doc.GetTableCellValue(0, 0, 0);
        Assert.Equal(before, doc.TableCount);
    }

    [Fact]
    public void GetTableCellValue_CalledTwice_SameResult()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(2, 2);
        doc.SetTableCellValue(0, 0, 0, "Stable Value");
        string? first = doc.GetTableCellValue(0, 0, 0);
        string? second = doc.GetTableCellValue(0, 0, 0);
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetTableCellValue_AfterSetTableCellValue_ReturnsValue()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(3, 3);
        doc.SetTableCellValue(0, 1, 1, "Target Cell");
        string? value = doc.GetTableCellValue(0, 1, 1);
        Assert.NotNull(value);
        Assert.Equal("Target Cell", value);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_MultipleCellsInTable_EachReturnsCorrectValue()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(2, 3);
        doc.SetTableCellValue(0, 0, 0, "Name");
        doc.SetTableCellValue(0, 0, 1, "Age");
        doc.SetTableCellValue(0, 0, 2, "City");
        doc.SetTableCellValue(0, 1, 0, "Alice");
        doc.SetTableCellValue(0, 1, 1, "30");
        doc.SetTableCellValue(0, 1, 2, "Berlin");
        Assert.Equal("Name", doc.GetTableCellValue(0, 0, 0));
        Assert.Equal("Age", doc.GetTableCellValue(0, 0, 1));
        Assert.Equal("Alice", doc.GetTableCellValue(0, 1, 0));
        Assert.Equal("Berlin", doc.GetTableCellValue(0, 1, 2));
    }
}
