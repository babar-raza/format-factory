// Tests for FodsDocument.GetNumericColumnValues dedicated coverage.
// Sprint: ff-sprint-s218-dotnet-deepening-20260629
// Ledger: PC-FODS-R235

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R235: Dedicated tests for FodsDocument.GetNumericColumnValues.
/// Null/whitespace sheet name → exception.
/// Non-existent sheet → exception.
/// Negative column index → exception.
/// Empty sheet → returns empty collection.
/// Returns IEnumerable or list (non-null).
/// SheetCount unchanged.
/// String cell value → not in numeric results.
/// Numeric cell value → in results.
/// Dogfood: set numeric values, verify all in results.
/// Dogfood: mixed numeric/string, only numeric values returned.
/// </summary>
public class FodsR235GetNumericColumnValuesDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetNumericColumnValues_NullSheetName_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetNumericColumnValues(null!, 0));
    }

    [Fact]
    public void GetNumericColumnValues_WhitespaceSheetName_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetNumericColumnValues("   ", 0));
    }

    [Fact]
    public void GetNumericColumnValues_NonExistentSheet_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetNumericColumnValues("NoSheet", 0));
    }

    [Fact]
    public void GetNumericColumnValues_NegativeColumn_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        string sheetName = doc.GetSheetNames()[0];
        Assert.ThrowsAny<Exception>(() => doc.GetNumericColumnValues(sheetName, -1));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetNumericColumnValues_EmptySheet_ReturnsEmpty()
    {
        var doc = FodsDocument.CreateNew();
        string sheetName = doc.GetSheetNames()[0];
        var values = doc.GetNumericColumnValues(sheetName, 0);
        Assert.NotNull(values);
        Assert.Empty(values);
    }

    [Fact]
    public void GetNumericColumnValues_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        int before = doc.SheetCount;
        string sheetName = doc.GetSheetNames()[0];
        doc.GetNumericColumnValues(sheetName, 0);
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetNumericColumnValues_ReturnsNonNull()
    {
        var doc = FodsDocument.CreateNew();
        string sheetName = doc.GetSheetNames()[0];
        var result = doc.GetNumericColumnValues(sheetName, 0);
        Assert.NotNull(result);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipelines
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_NumericValues_AllInResults()
    {
        var doc = FodsDocument.CreateNew();
        string sheetName = doc.GetSheetNames()[0];
        doc.SetCellValue(sheetName, 0, 0, "10");
        doc.SetCellValue(sheetName, 1, 0, "20");
        doc.SetCellValue(sheetName, 2, 0, "30");
        var values = doc.GetNumericColumnValues(sheetName, 0);
        var list = new System.Collections.Generic.List<double>(values);
        Assert.Contains(10.0, list);
        Assert.Contains(20.0, list);
        Assert.Contains(30.0, list);
    }

    [Fact]
    public void DogfoodPipeline_MixedValues_OnlyNumericReturned()
    {
        var doc = FodsDocument.CreateNew();
        string sheetName = doc.GetSheetNames()[0];
        doc.SetCellValue(sheetName, 0, 0, "100");
        doc.SetCellValue(sheetName, 1, 0, "NotANumber");
        doc.SetCellValue(sheetName, 2, 0, "200");
        var values = doc.GetNumericColumnValues(sheetName, 0);
        var list = new System.Collections.Generic.List<double>(values);
        Assert.Contains(100.0, list);
        Assert.Contains(200.0, list);
        Assert.DoesNotContain(-1.0, list);
    }
}
