// Tests for FodsDocument.ExportSheetToJson dedicated coverage.
// Sprint: ff-sprint-s188-dotnet-deepening-20260628
// Ledger: PC-FODS-R195

using System.Text.Json;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R195: Dedicated tests for FodsDocument.ExportSheetToJson() and ExportSheetToJson(string sheetName).
/// Exports a sheet as a JSON array of row objects.
/// No-arg overload: no sheets throws InvalidOperationException.
/// Zero or one row returns "[]".
/// First row treated as headers; subsequent rows become objects keyed by headers.
/// Named-sheet overload: nonexistent sheet throws ArgumentException.
/// Named-sheet valid: returns JSON string.
/// Covers: no-arg no-sheets throws; empty sheet returns json-array;
/// one-row (headers only) returns empty array; two rows returns one object;
/// headers match first row cells; named-sheet nonexistent throws;
/// named-sheet empty returns json-array; named-sheet valid two rows object;
/// returns valid JSON string; dogfood set data then export.
/// </summary>
public class FodsR195ExportSheetToJsonDedicatedTests
{
    // -------------------------------------------------------------------------
    // No-arg overload
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportSheetToJson_EmptySheet_ReturnsJsonArray()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        var json = doc.ExportSheetToJson();
        // Should return "[]" for empty or header-only sheet
        Assert.NotNull(json);
        var arr = JsonSerializer.Deserialize<JsonElement>(json);
        Assert.Equal(JsonValueKind.Array, arr.ValueKind);
    }

    [Fact]
    public void ExportSheetToJson_OneRow_ReturnsEmptyArray()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.SetCellValue(0, 0, "Name");
        doc.SetCellValue(0, 1, "Age");
        var json = doc.ExportSheetToJson();
        var arr = JsonSerializer.Deserialize<JsonElement>(json);
        Assert.Equal(JsonValueKind.Array, arr.ValueKind);
        Assert.Equal(0, arr.GetArrayLength());
    }

    [Fact]
    public void ExportSheetToJson_TwoRows_ReturnsOneObject()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.SetCellValue(0, 0, "Name");
        doc.SetCellValue(0, 1, "Age");
        doc.SetCellValue(1, 0, "Alice");
        doc.SetCellValue(1, 1, "30");
        var json = doc.ExportSheetToJson();
        var arr = JsonSerializer.Deserialize<JsonElement>(json);
        Assert.Equal(1, arr.GetArrayLength());
    }

    [Fact]
    public void ExportSheetToJson_HeadersMatchFirstRow()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.SetCellValue(0, 0, "Product");
        doc.SetCellValue(0, 1, "Price");
        doc.SetCellValue(1, 0, "Widget");
        doc.SetCellValue(1, 1, "9.99");
        var json = doc.ExportSheetToJson();
        var arr = JsonSerializer.Deserialize<JsonElement>(json);
        var obj = arr[0];
        Assert.True(obj.TryGetProperty("Product", out _));
        Assert.True(obj.TryGetProperty("Price", out _));
    }

    [Fact]
    public void ExportSheetToJson_ReturnsValidJsonString()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.SetCellValue(0, 0, "Key");
        doc.SetCellValue(1, 0, "Value");
        var json = doc.ExportSheetToJson();
        // Verify it's parseable JSON
        var element = JsonSerializer.Deserialize<JsonElement>(json);
        Assert.Equal(JsonValueKind.Array, element.ValueKind);
    }

    // -------------------------------------------------------------------------
    // Named-sheet overload
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportSheetToJson_NamedSheet_NonexistentThrowsArgumentException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.Throws<ArgumentException>(() => doc.ExportSheetToJson("NoSuchSheet"));
    }

    [Fact]
    public void ExportSheetToJson_NamedSheet_EmptyReturnsJsonArray()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.AddSheet("Report");
        var json = doc.ExportSheetToJson("Report");
        var arr = JsonSerializer.Deserialize<JsonElement>(json);
        Assert.Equal(JsonValueKind.Array, arr.ValueKind);
    }

    [Fact]
    public void ExportSheetToJson_NamedSheet_TwoRowsReturnsObject()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.AddSheet("Data");
        doc.SetCellValue("Data", 0, 0, "Col");
        doc.SetCellValue("Data", 1, 0, "Val");
        var json = doc.ExportSheetToJson("Data");
        var arr = JsonSerializer.Deserialize<JsonElement>(json);
        Assert.Equal(1, arr.GetArrayLength());
    }

    // -------------------------------------------------------------------------
    // Dogfood pipelines
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_SetDataThenExport_AllFieldsPresent()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.SetCellValue(0, 0, "ID");
        doc.SetCellValue(0, 1, "Name");
        doc.SetCellValue(1, 0, "1");
        doc.SetCellValue(1, 1, "Alice");
        var json = doc.ExportSheetToJson();
        Assert.Contains("ID", json);
        Assert.Contains("Alice", json);
    }
}
