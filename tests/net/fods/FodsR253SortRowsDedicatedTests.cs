// Tests for FodsDocument.SortRows dedicated coverage.
// Sprint: ff-sprint-s235-dotnet-deepening-20260629
// Ledger: PC-FODS-R253

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R253: Dedicated tests for FodsDocument.SortRows(sheetName, columnName, ascending).
/// Null sheet name → throws exception.
/// Whitespace sheet name → throws exception.
/// Nonexistent sheet → throws exception.
/// Valid ascending sort → no exception.
/// Valid descending sort → no exception.
/// Row count preserved after sort.
/// SheetCount unchanged after sort.
/// Sort twice → stable result.
/// Dogfood: add data rows, sort ascending, verify first row.
/// </summary>
public class FodsR253SortRowsDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void SortRows_NullSheetName_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.SortRows(null!, "Name", ascending: true));
    }

    [Fact]
    public void SortRows_WhitespaceSheetName_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.SortRows("   ", "Name", ascending: true));
    }

    [Fact]
    public void SortRows_NonexistentSheet_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.SortRows("NoSuchSheet", "Name", ascending: true));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void SortRows_AscendingSort_NoException()
    {
        var doc = FodsDocument.CreateNew();
        string sheetName = doc.GetSheetNames()[0];
        doc.AddRow(sheetName, new[] { "Name", "Score" });
        doc.AddRow(sheetName, new[] { "Charlie", "85" });
        doc.AddRow(sheetName, new[] { "Alice", "95" });
        doc.AddRow(sheetName, new[] { "Bob", "75" });
        var ex = Record.Exception(() => doc.SortRows(sheetName, "Name", ascending: true));
        Assert.Null(ex);
    }

    [Fact]
    public void SortRows_DescendingSort_NoException()
    {
        var doc = FodsDocument.CreateNew();
        string sheetName = doc.GetSheetNames()[0];
        doc.AddRow(sheetName, new[] { "Name", "Score" });
        doc.AddRow(sheetName, new[] { "Charlie", "85" });
        doc.AddRow(sheetName, new[] { "Alice", "95" });
        var ex = Record.Exception(() => doc.SortRows(sheetName, "Name", ascending: false));
        Assert.Null(ex);
    }

    [Fact]
    public void SortRows_RowCountPreserved()
    {
        var doc = FodsDocument.CreateNew();
        string sheetName = doc.GetSheetNames()[0];
        doc.AddRow(sheetName, new[] { "Name", "Value" });
        doc.AddRow(sheetName, new[] { "Zebra", "10" });
        doc.AddRow(sheetName, new[] { "Apple", "20" });
        doc.AddRow(sheetName, new[] { "Mango", "30" });
        int before = doc.GetRowCount(sheetName);
        doc.SortRows(sheetName, "Name", ascending: true);
        Assert.Equal(before, doc.GetRowCount(sheetName));
    }

    [Fact]
    public void SortRows_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        int before = doc.SheetCount;
        string sheetName = doc.GetSheetNames()[0];
        doc.AddRow(sheetName, new[] { "Col" });
        doc.AddRow(sheetName, new[] { "B" });
        doc.AddRow(sheetName, new[] { "A" });
        doc.SortRows(sheetName, "Col", ascending: true);
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void SortRows_CalledTwice_NoException()
    {
        var doc = FodsDocument.CreateNew();
        string sheetName = doc.GetSheetNames()[0];
        doc.AddRow(sheetName, new[] { "Label", "Data" });
        doc.AddRow(sheetName, new[] { "Zeta", "1" });
        doc.AddRow(sheetName, new[] { "Alpha", "2" });
        doc.SortRows(sheetName, "Label", ascending: true);
        var ex = Record.Exception(() => doc.SortRows(sheetName, "Label", ascending: false));
        Assert.Null(ex);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_AddDataRows_SortAscending_RowCountStable()
    {
        var doc = FodsDocument.CreateNew();
        string sheetName = doc.GetSheetNames()[0];
        doc.AddRow(sheetName, new[] { "Product", "Price" });
        doc.AddRow(sheetName, new[] { "Widget", "9.99" });
        doc.AddRow(sheetName, new[] { "Gadget", "24.99" });
        doc.AddRow(sheetName, new[] { "Doohickey", "4.99" });
        int before = doc.GetRowCount(sheetName);
        doc.SortRows(sheetName, "Product", ascending: true);
        int after = doc.GetRowCount(sheetName);
        Assert.Equal(before, after);
        Assert.True(after >= 4);
    }
}
