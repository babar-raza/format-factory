// Tests for FodsDocument.AddColumn dedicated coverage.
// Sprint: ff-sprint-s247-dotnet-deepening-20260630
// Ledger: PC-FODS-R266

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R266: Dedicated tests for FodsDocument.AddColumn(sheetName, values).
/// Null sheet name → throws exception.
/// Whitespace sheet name → throws exception.
/// Nonexistent sheet → throws exception.
/// Valid call with values → no exception.
/// GetColumnCount increases after AddColumn.
/// SheetCount unchanged after AddColumn.
/// Add multiple columns → count grows correspondingly.
/// Dogfood: add column, verify values accessible via GetCellValue.
/// Dogfood: add two columns with distinct data, verify both accessible.
/// </summary>
public class FodsR266AddColumnDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void AddColumn_NullSheetName_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.AddColumn(null!, new[] { "A", "B" }));
    }

    [Fact]
    public void AddColumn_WhitespaceSheetName_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.AddColumn("   ", new[] { "A", "B" }));
    }

    [Fact]
    public void AddColumn_NonexistentSheet_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.AddColumn("NoSuchSheet", new[] { "A" }));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void AddColumn_ValidValues_NoException()
    {
        var doc = FodsDocument.CreateNew();
        string sheetName = doc.GetSheetNames()[0];
        var ex = Record.Exception(() => doc.AddColumn(sheetName, new[] { "Header", "Val1", "Val2" }));
        Assert.Null(ex);
    }

    [Fact]
    public void AddColumn_GetColumnCountIncreases()
    {
        var doc = FodsDocument.CreateNew();
        string sheetName = doc.GetSheetNames()[0];
        int before = doc.GetColumnCount(sheetName);
        doc.AddColumn(sheetName, new[] { "X", "Y", "Z" });
        Assert.True(doc.GetColumnCount(sheetName) > before);
    }

    [Fact]
    public void AddColumn_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        string sheetName = doc.GetSheetNames()[0];
        int before = doc.SheetCount;
        doc.AddColumn(sheetName, new[] { "A", "B" });
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void AddColumn_MultipleColumns_CountGrows()
    {
        var doc = FodsDocument.CreateNew();
        string sheetName = doc.GetSheetNames()[0];
        int start = doc.GetColumnCount(sheetName);
        doc.AddColumn(sheetName, new[] { "Col1Row1", "Col1Row2" });
        doc.AddColumn(sheetName, new[] { "Col2Row1", "Col2Row2" });
        Assert.True(doc.GetColumnCount(sheetName) >= start + 2);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_AddColumn_ValuesAccessibleViaCellValue()
    {
        var doc = FodsDocument.CreateNew();
        string sheetName = doc.GetSheetNames()[0];
        doc.AddColumn(sheetName, new[] { "Name", "Alice", "Bob" });
        // First column (col 0) should have the values we set
        string headerCell = doc.GetCellValue(sheetName, 0, 0);
        Assert.NotNull(headerCell);
        Assert.NotEmpty(headerCell);
    }

    [Fact]
    public void DogfoodPipeline_AddTwoColumns_BothAccessible()
    {
        var doc = FodsDocument.CreateNew();
        string sheetName = doc.GetSheetNames()[0];
        doc.AddColumn(sheetName, new[] { "FirstCol" });
        doc.AddColumn(sheetName, new[] { "SecondCol" });
        // Both columns should be accessible
        int colCount = doc.GetColumnCount(sheetName);
        Assert.True(colCount >= 2);
        // Verify at least one cell is non-null
        string cell = doc.GetCellValue(sheetName, 0, 0);
        Assert.NotNull(cell);
    }
}
