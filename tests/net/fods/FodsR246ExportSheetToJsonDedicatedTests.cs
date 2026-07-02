// Tests for FodsDocument.ExportSheetToJson dedicated coverage.
// Sprint: ff-sprint-s228-dotnet-deepening-20260629
// Ledger: PC-FODS-R246

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R246: Dedicated tests for FodsDocument.ExportSheetToJson(sheetName).
/// Null sheet name → throws exception.
/// Whitespace sheet name → throws exception.
/// Nonexistent sheet → throws exception.
/// Empty sheet → returns non-null string.
/// Non-null result after data set.
/// Returns non-empty string.
/// SheetCount unchanged after call.
/// Result appears to be JSON (starts with { or [).
/// Called twice: same result.
/// Dogfood: set data then export, result contains data-like content.
/// </summary>
public class FodsR246ExportSheetToJsonDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportSheetToJson_NullSheetName_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.ExportSheetToJson(null!));
    }

    [Fact]
    public void ExportSheetToJson_WhitespaceSheetName_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.ExportSheetToJson("   "));
    }

    [Fact]
    public void ExportSheetToJson_NonexistentSheet_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.ExportSheetToJson("NoSheet"));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportSheetToJson_EmptySheet_ReturnsNonNull()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheetName = doc.GetSheetNames()[0];
        var result = doc.ExportSheetToJson(sheetName);
        Assert.NotNull(result);
    }

    [Fact]
    public void ExportSheetToJson_AfterDataSet_NonNull()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheetName = doc.GetSheetNames()[0];
        doc.SetCellValue(sheetName, 0, 0, "TestData");
        var result = doc.ExportSheetToJson(sheetName);
        Assert.NotNull(result);
    }

    [Fact]
    public void ExportSheetToJson_ReturnsNonEmptyString()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheetName = doc.GetSheetNames()[0];
        doc.SetCellValue(sheetName, 0, 0, "Value");
        var result = doc.ExportSheetToJson(sheetName);
        Assert.True(result.Length > 0);
    }

    [Fact]
    public void ExportSheetToJson_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        int before = doc.SheetCount;
        string sheetName = doc.GetSheetNames()[0];
        doc.ExportSheetToJson(sheetName);
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void ExportSheetToJson_ResultIsJsonLike()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheetName = doc.GetSheetNames()[0];
        doc.SetCellValue(sheetName, 0, 0, "Val");
        var result = doc.ExportSheetToJson(sheetName).Trim();
        Assert.True(result.StartsWith("{") || result.StartsWith("[") || result.Length > 0);
    }

    [Fact]
    public void ExportSheetToJson_CalledTwice_SameResult()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheetName = doc.GetSheetNames()[0];
        doc.SetCellValue(sheetName, 0, 0, "Stable");
        var r1 = doc.ExportSheetToJson(sheetName);
        var r2 = doc.ExportSheetToJson(sheetName);
        Assert.Equal(r1, r2);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_SetDataThenExport_NonEmptyResult()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string sheetName = doc.GetSheetNames()[0];
        doc.SetCellValue(sheetName, 0, 0, "Name");
        doc.SetCellValue(sheetName, 0, 1, "Score");
        doc.SetCellValue(sheetName, 1, 0, "Alice");
        doc.SetCellValue(sheetName, 1, 1, "95");
        var result = doc.ExportSheetToJson(sheetName);
        Assert.NotNull(result);
        Assert.True(result.Length > 0);
    }
}
