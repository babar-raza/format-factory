// Tests for FodsDocument.SortRows dedicated coverage.
// Sprint: ff-sprint-s246-dotnet-deepening-20260630
// Ledger: PC-FODS-R265

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R265: Dedicated tests for FodsDocument.SortRows(sheetName, columnIndex, ascending).
/// Null sheet name → throws exception.
/// Whitespace sheet name → throws exception.
/// Nonexistent sheet → throws exception.
/// Valid ascending call → no exception.
/// Valid descending call → no exception.
/// SheetCount unchanged after sort.
/// Called twice → same result (idempotent on sorted data).
/// Dogfood: add rows with known values, sort ascending, verify order.
/// Dogfood: sort descending, verify order reversed.
/// </summary>
public class FodsR265SortRowsDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void SortRows_NullSheetName_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.SortRows(null!, 0, true));
    }

    [Fact]
    public void SortRows_WhitespaceSheetName_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.SortRows("   ", 0, true));
    }

    [Fact]
    public void SortRows_NonexistentSheet_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.SortRows("NoSuchSheet", 0, true));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void SortRows_ValidAscending_NoException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheetName = doc.GetSheetNames()[0];
        doc.AddRow(sheetName, new[] { "B" });
        doc.AddRow(sheetName, new[] { "A" });
        var ex = Record.Exception(() => doc.SortRows(sheetName, 0, true));
        Assert.Null(ex);
    }

    [Fact]
    public void SortRows_ValidDescending_NoException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheetName = doc.GetSheetNames()[0];
        doc.AddRow(sheetName, new[] { "A" });
        doc.AddRow(sheetName, new[] { "B" });
        var ex = Record.Exception(() => doc.SortRows(sheetName, 0, false));
        Assert.Null(ex);
    }

    [Fact]
    public void SortRows_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheetName = doc.GetSheetNames()[0];
        doc.AddRow(sheetName, new[] { "C" });
        doc.AddRow(sheetName, new[] { "A" });
        doc.AddRow(sheetName, new[] { "B" });
        int before = doc.SheetCount;
        doc.SortRows(sheetName, 0, true);
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void SortRows_CalledTwice_SameResult()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheetName = doc.GetSheetNames()[0];
        doc.AddRow(sheetName, new[] { "C" });
        doc.AddRow(sheetName, new[] { "A" });
        doc.AddRow(sheetName, new[] { "B" });
        doc.SortRows(sheetName, 0, true);
        string firstVal = doc.GetCellValue(sheetName, 0, 0);
        doc.SortRows(sheetName, 0, true);
        string secondVal = doc.GetCellValue(sheetName, 0, 0);
        Assert.Equal(firstVal, secondVal);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_SortAscending_FirstValueIsSmallest()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheetName = doc.GetSheetNames()[0];
        doc.AddRow(sheetName, new[] { "Charlie" });
        doc.AddRow(sheetName, new[] { "Alice" });
        doc.AddRow(sheetName, new[] { "Bob" });
        doc.SortRows(sheetName, 0, true);
        string first = doc.GetCellValue(sheetName, 0, 0);
        Assert.NotNull(first);
        // Alice < Bob < Charlie alphabetically
        Assert.Equal("Alice", first);
    }

    [Fact]
    public void DogfoodPipeline_SortDescending_FirstValueIsLargest()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheetName = doc.GetSheetNames()[0];
        doc.AddRow(sheetName, new[] { "Alice" });
        doc.AddRow(sheetName, new[] { "Charlie" });
        doc.AddRow(sheetName, new[] { "Bob" });
        doc.SortRows(sheetName, 0, false);
        string first = doc.GetCellValue(sheetName, 0, 0);
        Assert.NotNull(first);
        Assert.Equal("Charlie", first);
    }
}
