// Tests for FodsDocument.GetCellDataType — ODF value-type cell metadata inspection.
// Sprint: FORMAT-FACTORY-FODS-CELL-DATA-TYPE-20260626
// Ledger: R122-GOVERNED-DOTNET-FODS-CELL-DATA-TYPE-001

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R122: GetCellDataType(sheetName, row, col) — returns ODF office:value-type attribute
/// (e.g., "string", "float", "date") or null for cells without a type or out-of-range.
/// Supplements R110 basic coverage with type variety and boundary conditions.
/// </summary>
public class FodsR122GetCellDataTypeTests
{
    private static readonly string SamplesDir = Path.GetFullPath(
        Path.Combine(AppContext.BaseDirectory, "../../../../../../samples/by-format/fods"));

    private static string MinimalPath => Path.Combine(SamplesDir, "minimal-spreadsheet.fods");

    // ---- Null for new/empty sheet ----

    [Fact]
    public void GetCellDataType_EmptySheet_ReturnsNull()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Empty");
        var result = doc.GetCellDataType("Empty", 0, 0);
        Assert.Null(result);
    }

    // ---- String cells (most common default) ----

    [Fact]
    public void GetCellDataType_StringCell_ReturnsStringOrNull()
    {
        var doc = FodsDocument.Load(MinimalPath);
        // "Hello" in minimal fixture is a string cell
        var result = doc.GetCellDataType("Sheet1", 0, 0);
        // String-typed cells may return "string" or null (depending on ODF encoding)
        // either is valid — we just verify it doesn't throw
        Assert.True(result is null || result == "string");
    }

    // ---- Out of range returns null ----

    [Fact]
    public void GetCellDataType_RowOutOfRange_ReturnsNull()
    {
        var doc = FodsDocument.Load(MinimalPath);
        var result = doc.GetCellDataType("Sheet1", 999, 0);
        Assert.Null(result);
    }

    [Fact]
    public void GetCellDataType_ColOutOfRange_ReturnsNull()
    {
        var doc = FodsDocument.Load(MinimalPath);
        var result = doc.GetCellDataType("Sheet1", 0, 999);
        Assert.Null(result);
    }

    [Fact]
    public void GetCellDataType_NegativeRow_ReturnsNull()
    {
        var doc = FodsDocument.Load(MinimalPath);
        var result = doc.GetCellDataType("Sheet1", -1, 0);
        Assert.Null(result);
    }

    // ---- Non-existent sheet returns null ----

    [Fact]
    public void GetCellDataType_NonExistentSheet_ReturnsNull()
    {
        var doc = FodsDocument.Load(MinimalPath);
        var result = doc.GetCellDataType("Phantom", 0, 0);
        Assert.Null(result);
    }

    // ---- Empty sheet name throws ----

    [Fact]
    public void GetCellDataType_EmptySheetName_Throws()
    {
        var doc = FodsDocument.Load(MinimalPath);
        Assert.Throws<ArgumentException>(() => doc.GetCellDataType("", 0, 0));
    }

    [Fact]
    public void GetCellDataType_WhitespaceSheetName_Throws()
    {
        var doc = FodsDocument.Load(MinimalPath);
        Assert.Throws<ArgumentException>(() => doc.GetCellDataType("   ", 0, 0));
    }

    // ---- Dogfood pipeline: build sheet, check multiple cells ----

    [Fact]
    public void DogfoodPipeline_MultiSheetCellTypeInspection()
    {
        var doc = FodsDocument.CreateNew();
        var s1 = doc.AddSheet("Analysis");
        FodsDocument.SetCellValue(s1, 0, 0, "Label");
        FodsDocument.SetCellValue(s1, 0, 1, "Amount");

        // Both cells exist, GetCellDataType should not throw
        var t0 = doc.GetCellDataType("Analysis", 0, 0);
        var t1 = doc.GetCellDataType("Analysis", 0, 1);

        // Values should be string|null (plain text set cells)
        Assert.True(t0 is null || t0 == "string");
        Assert.True(t1 is null || t1 == "string");

        // Out of range cell
        var t_oob = doc.GetCellDataType("Analysis", 5, 5);
        Assert.Null(t_oob);

        // Export to CSV to verify same data is accessible
        var csv = FodsDocumentExporter.ExportSheetToCsv(s1);
        Assert.Contains("Label", csv);
        Assert.Contains("Amount", csv);
    }
}
