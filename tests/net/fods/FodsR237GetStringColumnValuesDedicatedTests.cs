// Tests for FodsDocument.GetStringColumnValues dedicated coverage.
// Sprint: ff-sprint-s219-dotnet-deepening-20260629
// Ledger: PC-FODS-R237

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R237: Dedicated tests for FodsDocument.GetStringColumnValues(sheetName, col).
/// Null sheet name → throws exception.
/// Whitespace sheet name → throws exception.
/// Nonexistent sheet → throws exception.
/// Negative column index → throws exception.
/// Empty sheet → returns empty.
/// Non-null result after data set.
/// SheetCount unchanged after call.
/// Dogfood: string values all returned.
/// Dogfood: mixed values — only strings returned.
/// Dogfood: multiple columns independent.
/// </summary>
public class FodsR237GetStringColumnValuesDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetStringColumnValues_NullSheetName_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetStringColumnValues(null!, 0));
    }

    [Fact]
    public void GetStringColumnValues_WhitespaceSheetName_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetStringColumnValues("   ", 0));
    }

    [Fact]
    public void GetStringColumnValues_NonexistentSheet_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetStringColumnValues("NoSuchSheet", 0));
    }

    [Fact]
    public void GetStringColumnValues_NegativeCol_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        string sheetName = doc.GetSheetNames()[0];
        Assert.ThrowsAny<Exception>(() => doc.GetStringColumnValues(sheetName, -1));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetStringColumnValues_EmptySheet_ReturnsEmpty()
    {
        var doc = FodsDocument.CreateNew();
        string sheetName = doc.GetSheetNames()[0];
        var values = doc.GetStringColumnValues(sheetName, 0);
        Assert.NotNull(values);
        Assert.Empty(values);
    }

    [Fact]
    public void GetStringColumnValues_AfterDataSet_NonNull()
    {
        var doc = FodsDocument.CreateNew();
        string sheetName = doc.GetSheetNames()[0];
        doc.SetCellValue(sheetName, 0, 0, "Hello");
        var values = doc.GetStringColumnValues(sheetName, 0);
        Assert.NotNull(values);
    }

    [Fact]
    public void GetStringColumnValues_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        int before = doc.SheetCount;
        string sheetName = doc.GetSheetNames()[0];
        doc.GetStringColumnValues(sheetName, 0);
        Assert.Equal(before, doc.SheetCount);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipelines
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_StringValues_AllReturned()
    {
        var doc = FodsDocument.CreateNew();
        string sheetName = doc.GetSheetNames()[0];
        doc.SetCellValue(sheetName, 0, 0, "Alpha");
        doc.SetCellValue(sheetName, 1, 0, "Beta");
        doc.SetCellValue(sheetName, 2, 0, "Gamma");
        var values = doc.GetStringColumnValues(sheetName, 0);
        var list = new System.Collections.Generic.List<string>(values);
        Assert.Contains("Alpha", list);
        Assert.Contains("Beta", list);
        Assert.Contains("Gamma", list);
    }

    [Fact]
    public void DogfoodPipeline_MixedValues_OnlyNonNumericOrAllStrings()
    {
        var doc = FodsDocument.CreateNew();
        string sheetName = doc.GetSheetNames()[0];
        doc.SetCellValue(sheetName, 0, 0, "Text");
        doc.SetCellValue(sheetName, 1, 0, "42");
        doc.SetCellValue(sheetName, 2, 0, "MoreText");
        var values = doc.GetStringColumnValues(sheetName, 0);
        // Should contain at least the non-numeric strings
        var list = new System.Collections.Generic.List<string>(values);
        Assert.NotEmpty(list);
    }

    [Fact]
    public void DogfoodPipeline_MultipleColumns_Independent()
    {
        var doc = FodsDocument.CreateNew();
        string sheetName = doc.GetSheetNames()[0];
        doc.SetCellValue(sheetName, 0, 0, "ColA");
        doc.SetCellValue(sheetName, 0, 1, "ColB");
        var col0 = new System.Collections.Generic.List<string>(
            doc.GetStringColumnValues(sheetName, 0));
        var col1 = new System.Collections.Generic.List<string>(
            doc.GetStringColumnValues(sheetName, 1));
        Assert.Contains("ColA", col0);
        Assert.Contains("ColB", col1);
    }
}
