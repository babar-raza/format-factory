// Tests for FodsDocument.SortRows dedicated coverage.
// Sprint: ff-sprint-s175-dotnet-deepening-20260628
// Ledger: PC-FODS-R182

using System.Linq;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R182: Dedicated tests for FodsDocument.SortRows(sheetName, sortColumn, ascending).
/// Sorts rows in-place on the named sheet by the given column index.
/// null/whitespace sheetName throws ArgumentException.
/// Nonexistent sheet throws InvalidOperationException.
/// Negative sortColumn throws ArgumentOutOfRangeException.
/// 0 or 1 rows: no-op (does not throw).
/// ascending=true (default): smallest first; ascending=false: largest first.
/// Numeric values sort numerically; non-numeric sort lexicographically.
/// Covers: null/whitespace guard; nonexistent guard; negative column guard;
/// empty sheet no-op; single-row no-op; ascending sort; descending sort;
/// numeric sort; dogfood pipeline with SetCellValue.
/// </summary>
public class FodsR182SortRowsDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Theory]
    [InlineData(null)]
    [InlineData("")]
    [InlineData("   ")]
    public void SortRows_NullOrWhitespaceSheetName_ThrowsArgumentException(string sheetName)
    {
        var doc = FodsDocument.CreateNew();
        Assert.Throws<ArgumentException>(() => doc.SortRows(sheetName, 0));
    }

    [Fact]
    public void SortRows_NonexistentSheet_ThrowsInvalidOperationException()
    {
        var doc = FodsDocument.CreateNew();
        Assert.Throws<InvalidOperationException>(() => doc.SortRows("NoSuchSheet", 0));
    }

    [Fact]
    public void SortRows_NegativeSortColumn_ThrowsArgumentOutOfRangeException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        Assert.Throws<ArgumentOutOfRangeException>(() => doc.SortRows("Data", -1));
    }

    // -------------------------------------------------------------------------
    // No-op cases
    // -------------------------------------------------------------------------

    [Fact]
    public void SortRows_EmptySheet_NoOp()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Empty");
        // No exception expected
        doc.SortRows("Empty", 0);
        Assert.Equal(0, doc.GetRowCount("Empty"));
    }

    [Fact]
    public void SortRows_SingleRow_NoOp()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        doc.SetCellValue(0, 0, "OnlyRow");
        doc.SortRows("Data", 0);
        Assert.Equal("OnlyRow", doc.GetCellValue("Data", 0, 0));
    }

    // -------------------------------------------------------------------------
    // Sort order tests
    // -------------------------------------------------------------------------

    [Fact]
    public void SortRows_AscendingNumeric_SmallestFirst()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        doc.SetCellValue(0, 0, "300");
        doc.SetCellValue(1, 0, "100");
        doc.SetCellValue(2, 0, "200");
        doc.SortRows("Data", 0, ascending: true);
        Assert.Equal("100", doc.GetCellValue("Data", 0, 0));
        Assert.Equal("200", doc.GetCellValue("Data", 1, 0));
        Assert.Equal("300", doc.GetCellValue("Data", 2, 0));
    }

    [Fact]
    public void SortRows_DescendingNumeric_LargestFirst()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        doc.SetCellValue(0, 0, "100");
        doc.SetCellValue(1, 0, "300");
        doc.SetCellValue(2, 0, "200");
        doc.SortRows("Data", 0, ascending: false);
        Assert.Equal("300", doc.GetCellValue("Data", 0, 0));
        Assert.Equal("200", doc.GetCellValue("Data", 1, 0));
        Assert.Equal("100", doc.GetCellValue("Data", 2, 0));
    }

    [Fact]
    public void SortRows_LexicographicAscending_AlphaOrder()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        doc.SetCellValue(0, 0, "Charlie");
        doc.SetCellValue(1, 0, "Alice");
        doc.SetCellValue(2, 0, "Bob");
        doc.SortRows("Data", 0, ascending: true);
        Assert.Equal("Alice", doc.GetCellValue("Data", 0, 0));
        Assert.Equal("Bob", doc.GetCellValue("Data", 1, 0));
        Assert.Equal("Charlie", doc.GetCellValue("Data", 2, 0));
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_SortByColumn_RowDataMaintained()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Report");
        // Row 0: name=Zara, score=90
        doc.SetCellValue(0, 0, "Zara");
        doc.SetCellValue(0, 1, "90");
        // Row 1: name=Alice, score=70
        doc.SetCellValue(1, 0, "Alice");
        doc.SetCellValue(1, 1, "70");
        doc.SortRows("Report", 0, ascending: true);
        // After sort by col 0 ascending: Alice first
        Assert.Equal("Alice", doc.GetCellValue("Report", 0, 0));
        Assert.Equal("70", doc.GetCellValue("Report", 0, 1));
        Assert.Equal("Zara", doc.GetCellValue("Report", 1, 0));
        Assert.Equal("90", doc.GetCellValue("Report", 1, 1));
    }
}
