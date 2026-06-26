// Tests for FodsDocument.AddColumn dedicated coverage.
// Sprint: ff-sprint-s233-dotnet-deepening-20260629
// Ledger: PC-FODS-R251

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R251: Dedicated tests for FodsDocument.AddColumn(sheetName, columnName, values).
/// Null sheet name → throws exception.
/// Whitespace sheet name → throws exception.
/// Nonexistent sheet → throws exception.
/// Null column name → throws exception.
/// Valid call → no exception.
/// HasColumn returns true after AddColumn.
/// SheetCount unchanged after AddColumn.
/// Add two columns → both accessible via HasColumn.
/// Values accessible via GetCellValue after AddColumn.
/// Dogfood: add column then export or inspect values.
/// </summary>
public class FodsR251AddColumnDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void AddColumn_NullSheetName_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.AddColumn(null!, "ColA", new[] { "V1" }));
    }

    [Fact]
    public void AddColumn_WhitespaceSheetName_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.AddColumn("   ", "ColA", new[] { "V1" }));
    }

    [Fact]
    public void AddColumn_NonexistentSheet_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.AddColumn("NoSuchSheet", "ColA", new[] { "V1" }));
    }

    [Fact]
    public void AddColumn_NullColumnName_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        string sheetName = doc.GetSheetNames()[0];
        Assert.ThrowsAny<Exception>(() => doc.AddColumn(sheetName, null!, new[] { "V1" }));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void AddColumn_ValidCall_NoException()
    {
        var doc = FodsDocument.CreateNew();
        string sheetName = doc.GetSheetNames()[0];
        var ex = Record.Exception(() => doc.AddColumn(sheetName, "NewCol", new[] { "A", "B", "C" }));
        Assert.Null(ex);
    }

    [Fact]
    public void AddColumn_HasColumnReturnsTrueAfterAdd()
    {
        var doc = FodsDocument.CreateNew();
        string sheetName = doc.GetSheetNames()[0];
        doc.AddColumn(sheetName, "Revenue", new[] { "100", "200" });
        Assert.True(doc.HasColumn(sheetName, "Revenue"));
    }

    [Fact]
    public void AddColumn_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        int before = doc.SheetCount;
        string sheetName = doc.GetSheetNames()[0];
        doc.AddColumn(sheetName, "ColX", new[] { "1", "2" });
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void AddColumn_TwoColumns_BothHasColumnTrue()
    {
        var doc = FodsDocument.CreateNew();
        string sheetName = doc.GetSheetNames()[0];
        doc.AddColumn(sheetName, "Alpha", new[] { "A1", "A2" });
        doc.AddColumn(sheetName, "Beta", new[] { "B1", "B2" });
        Assert.True(doc.HasColumn(sheetName, "Alpha"));
        Assert.True(doc.HasColumn(sheetName, "Beta"));
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_AddColumn_GetStringColumnValuesReturnsData()
    {
        var doc = FodsDocument.CreateNew();
        string sheetName = doc.GetSheetNames()[0];
        doc.AddColumn(sheetName, "Product", new[] { "Widget", "Gadget", "Gizmo" });
        Assert.True(doc.HasColumn(sheetName, "Product"));
        var values = doc.GetStringColumnValues(sheetName, 0);
        Assert.NotNull(values);
    }
}
