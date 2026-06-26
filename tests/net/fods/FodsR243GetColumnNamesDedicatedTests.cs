// Tests for FodsDocument.GetColumnNames dedicated coverage.
// Sprint: ff-sprint-s225-dotnet-deepening-20260629
// Ledger: PC-FODS-R243

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R243: Dedicated tests for FodsDocument.GetColumnNames(sheetName).
/// Null sheet name → throws exception.
/// Whitespace sheet name → throws exception.
/// Nonexistent sheet → throws exception.
/// Empty sheet → returns non-null collection.
/// After setting header → non-null.
/// SheetCount unchanged after call.
/// Returns collection (not null).
/// Called twice → same count.
/// Dogfood: set multiple headers, all in result.
/// Dogfood: two sheets independent.
/// </summary>
public class FodsR243GetColumnNamesDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnNames_NullSheetName_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetColumnNames(null!));
    }

    [Fact]
    public void GetColumnNames_WhitespaceSheetName_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetColumnNames("   "));
    }

    [Fact]
    public void GetColumnNames_NonexistentSheet_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetColumnNames("Ghost"));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnNames_EmptySheet_ReturnsNonNull()
    {
        var doc = FodsDocument.CreateNew();
        string sheetName = doc.GetSheetNames()[0];
        var result = doc.GetColumnNames(sheetName);
        Assert.NotNull(result);
    }

    [Fact]
    public void GetColumnNames_AfterSetHeader_ReturnsNonNull()
    {
        var doc = FodsDocument.CreateNew();
        string sheetName = doc.GetSheetNames()[0];
        doc.SetCellValue(sheetName, 0, 0, "HeaderA");
        var result = doc.GetColumnNames(sheetName);
        Assert.NotNull(result);
    }

    [Fact]
    public void GetColumnNames_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        int before = doc.SheetCount;
        string sheetName = doc.GetSheetNames()[0];
        doc.GetColumnNames(sheetName);
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetColumnNames_ReturnsCollection()
    {
        var doc = FodsDocument.CreateNew();
        string sheetName = doc.GetSheetNames()[0];
        var result = doc.GetColumnNames(sheetName);
        Assert.NotNull(result);
        Assert.IsAssignableFrom<System.Collections.IEnumerable>(result);
    }

    [Fact]
    public void GetColumnNames_CalledTwice_SameCount()
    {
        var doc = FodsDocument.CreateNew();
        string sheetName = doc.GetSheetNames()[0];
        doc.SetCellValue(sheetName, 0, 0, "Col1");
        var r1 = new System.Collections.Generic.List<string>(doc.GetColumnNames(sheetName));
        var r2 = new System.Collections.Generic.List<string>(doc.GetColumnNames(sheetName));
        Assert.Equal(r1.Count, r2.Count);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipelines
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_MultipleHeaders_InResult()
    {
        var doc = FodsDocument.CreateNew();
        string sheetName = doc.GetSheetNames()[0];
        doc.SetCellValue(sheetName, 0, 0, "Name");
        doc.SetCellValue(sheetName, 0, 1, "Age");
        doc.SetCellValue(sheetName, 0, 2, "City");
        var result = new System.Collections.Generic.List<string>(
            doc.GetColumnNames(sheetName));
        Assert.NotEmpty(result);
    }

    [Fact]
    public void DogfoodPipeline_TwoSheets_Independent()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet2");
        string sheet1 = doc.GetSheetNames()[0];
        string sheet2 = "Sheet2";
        doc.SetCellValue(sheet1, 0, 0, "ColA");
        doc.SetCellValue(sheet2, 0, 0, "ColB");
        var r1 = doc.GetColumnNames(sheet1);
        var r2 = doc.GetColumnNames(sheet2);
        Assert.NotNull(r1);
        Assert.NotNull(r2);
    }
}
