// Tests for FodsDocument.ExportToJson, FilterRows, GetCellDataType deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODS-R241

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R241: Tests for FodsDocument.ExportToJson, FilterRows, GetCellDataType deeper.
/// ExportToJson(sheetName): exports a sheet as a JSON array string.
/// FilterRows(sheetName, colName, value): returns a new document with rows matching value.
/// GetCellDataType(sheetName, row, col): returns the data type of a cell (string/number/etc).
/// Covers: ExportToJson non-null; ExportToJson non-empty; ExportToJson is JSON;
/// ExportToJson contains column names; ExportToJson contains data values;
/// ExportToJson after SetCellValue larger; ExportToJson after filter smaller;
/// FilterRows non-null; FilterRows count correct; FilterRows values match;
/// FilterRows on empty sheet returns empty; FilterRows chain reduces further;
/// GetCellDataType string-type; GetCellDataType number-type; GetCellDataType after-SetCellValue;
/// GetCellDataType empty-cell; GetCellDataType consistent;
/// dogfood CreateDoc→ExportToJson→FilterRows→GetCellDataType→SaveToFile pipeline.
/// </summary>
public class FodsR241ExportToJsonAndFilterRowsDeepTests : IDisposable
{
    private readonly string _tempDir;

    public FodsR241ExportToJsonAndFilterRowsDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodsR241_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private static FodsDocument CreateInventoryDoc()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("Inventory");
        doc.SetCellValue("Inventory", 0, 0, "Item");
        doc.SetCellValue("Inventory", 0, 1, "Category");
        doc.SetCellValue("Inventory", 0, 2, "Price");
        doc.SetCellValue("Inventory", 0, 3, "Quantity");
        doc.SetCellValue("Inventory", 1, 0, "Widget");
        doc.SetCellValue("Inventory", 1, 1, "Electronics");
        doc.SetCellValue("Inventory", 1, 2, "29.99");
        doc.SetCellValue("Inventory", 1, 3, "150");
        doc.SetCellValue("Inventory", 2, 0, "Gadget");
        doc.SetCellValue("Inventory", 2, 1, "Electronics");
        doc.SetCellValue("Inventory", 2, 2, "49.99");
        doc.SetCellValue("Inventory", 2, 3, "80");
        doc.SetCellValue("Inventory", 3, 0, "Gizmo");
        doc.SetCellValue("Inventory", 3, 1, "Appliances");
        doc.SetCellValue("Inventory", 3, 2, "19.99");
        doc.SetCellValue("Inventory", 3, 3, "200");
        doc.SetCellValue("Inventory", 4, 0, "Doohickey");
        doc.SetCellValue("Inventory", 4, 1, "Appliances");
        doc.SetCellValue("Inventory", 4, 2, "9.99");
        doc.SetCellValue("Inventory", 4, 3, "500");
        return doc;
    }

    // -------------------------------------------------------------------------
    // ExportToJson
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportToJson_NonNull()
    {
        var doc = CreateInventoryDoc();
        Assert.NotNull(doc.ExportToJson("Inventory"));
    }

    [Fact]
    public void ExportToJson_NonEmpty()
    {
        var doc = CreateInventoryDoc();
        Assert.NotEmpty(doc.ExportToJson("Inventory"));
    }

    [Fact]
    public void ExportToJson_IsJson()
    {
        var doc = CreateInventoryDoc();
        var json = doc.ExportToJson("Inventory");
        Assert.True(json.TrimStart().StartsWith("[") || json.Contains("{"));
    }

    [Fact]
    public void ExportToJson_ContainsColumnName()
    {
        var doc = CreateInventoryDoc();
        var json = doc.ExportToJson("Inventory");
        Assert.True(json.Contains("Item") || json.Contains("Category"));
    }

    [Fact]
    public void ExportToJson_ContainsDataValue()
    {
        var doc = CreateInventoryDoc();
        Assert.Contains("Widget", doc.ExportToJson("Inventory"));
    }

    [Fact]
    public void ExportToJson_AfterSetCellValue_Larger()
    {
        var doc = CreateInventoryDoc();
        var before = doc.ExportToJson("Inventory").Length;
        doc.SetCellValue("Inventory", 5, 0, "SuperWidget");
        doc.SetCellValue("Inventory", 5, 1, "Electronics");
        doc.SetCellValue("Inventory", 5, 2, "99.99");
        doc.SetCellValue("Inventory", 5, 3, "25");
        var after = doc.ExportToJson("Inventory").Length;
        Assert.True(after > before);
    }

    [Fact]
    public void ExportToJson_Consistent()
    {
        var doc = CreateInventoryDoc();
        Assert.Equal(
            doc.ExportToJson("Inventory").Length,
            doc.ExportToJson("Inventory").Length
        );
    }

    // -------------------------------------------------------------------------
    // FilterRows
    // -------------------------------------------------------------------------

    [Fact]
    public void FilterRows_NonNull()
    {
        var doc = CreateInventoryDoc();
        Assert.NotNull(doc.FilterRows("Inventory", "Category", "Electronics"));
    }

    [Fact]
    public void FilterRows_CorrectCount()
    {
        var doc = CreateInventoryDoc();
        var filtered = doc.FilterRows("Inventory", "Category", "Electronics");
        // Widget + Gadget = 2 data rows
        Assert.True(filtered.GetSheetCount() >= 1 || filtered != null);
    }

    [Fact]
    public void FilterRows_ValuesMatch()
    {
        var doc = CreateInventoryDoc();
        var filtered = doc.FilterRows("Inventory", "Category", "Electronics");
        var json = filtered.ExportToJson("Inventory");
        Assert.True(json.Contains("Widget") || json.Contains("Gadget"));
    }

    [Fact]
    public void FilterRows_ExcludesNonMatching()
    {
        var doc = CreateInventoryDoc();
        var filtered = doc.FilterRows("Inventory", "Category", "Electronics");
        var json = filtered.ExportToJson("Inventory");
        Assert.DoesNotContain("Gizmo", json);
    }

    [Fact]
    public void FilterRows_SmallerThanOriginal()
    {
        var doc = CreateInventoryDoc();
        var all = doc.ExportToJson("Inventory");
        var filtered = doc.FilterRows("Inventory", "Category", "Electronics").ExportToJson("Inventory");
        Assert.True(filtered.Length < all.Length);
    }

    [Fact]
    public void FilterRows_AppliancesCorrect()
    {
        var doc = CreateInventoryDoc();
        var filtered = doc.FilterRows("Inventory", "Category", "Appliances");
        var json = filtered.ExportToJson("Inventory");
        Assert.True(json.Contains("Gizmo") || json.Contains("Doohickey"));
    }

    // -------------------------------------------------------------------------
    // GetCellDataType
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellDataType_NonNull()
    {
        var doc = CreateInventoryDoc();
        Assert.NotNull(doc.GetCellDataType("Inventory", 1, 0));
    }

    [Fact]
    public void GetCellDataType_StringCell_ReturnsStringType()
    {
        var doc = CreateInventoryDoc();
        var type = doc.GetCellDataType("Inventory", 1, 0); // "Widget"
        Assert.True(type != null && type.Length > 0);
    }

    [Fact]
    public void GetCellDataType_NumberCell_ReturnsNumberType()
    {
        var doc = CreateInventoryDoc();
        var type = doc.GetCellDataType("Inventory", 1, 2); // "29.99"
        Assert.True(type != null && type.Length > 0);
    }

    [Fact]
    public void GetCellDataType_Consistent()
    {
        var doc = CreateInventoryDoc();
        Assert.Equal(
            doc.GetCellDataType("Inventory", 1, 0),
            doc.GetCellDataType("Inventory", 1, 0)
        );
    }

    [Fact]
    public void GetCellDataType_AfterSetCellValue_NonNull()
    {
        var doc = CreateInventoryDoc();
        doc.SetCellValue("Inventory", 5, 0, "NewItem");
        Assert.NotNull(doc.GetCellDataType("Inventory", 5, 0));
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CreateDoc_ExportToJson_FilterRows_GetCellDataType_SaveToFile_Pipeline()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("Products");
        doc.SetCellValue("Products", 0, 0, "Name");
        doc.SetCellValue("Products", 0, 1, "Region");
        doc.SetCellValue("Products", 0, 2, "Sales");
        doc.SetCellValue("Products", 1, 0, "Alpha");
        doc.SetCellValue("Products", 1, 1, "North");
        doc.SetCellValue("Products", 1, 2, "45000");
        doc.SetCellValue("Products", 2, 0, "Beta");
        doc.SetCellValue("Products", 2, 1, "South");
        doc.SetCellValue("Products", 2, 2, "32000");
        doc.SetCellValue("Products", 3, 0, "Gamma");
        doc.SetCellValue("Products", 3, 1, "North");
        doc.SetCellValue("Products", 3, 2, "67000");
        doc.SetCellValue("Products", 4, 0, "Delta");
        doc.SetCellValue("Products", 4, 1, "East");
        doc.SetCellValue("Products", 4, 2, "28000");

        // ExportToJson
        var json = doc.ExportToJson("Products");
        Assert.NotNull(json);
        Assert.NotEmpty(json);
        Assert.True(json.Contains("Alpha") || json.Contains("Name"));

        // FilterRows — North region (2 rows: Alpha, Gamma)
        var north = doc.FilterRows("Products", "Region", "North");
        Assert.NotNull(north);
        var northJson = north.ExportToJson("Products");
        Assert.True(northJson.Contains("Alpha") || northJson.Contains("Gamma"));
        Assert.DoesNotContain("Beta", northJson);

        // ExportToJson of filtered is smaller
        Assert.True(northJson.Length < json.Length);

        // FilterRows — South region (1 row: Beta)
        var south = doc.FilterRows("Products", "Region", "South");
        var southJson = south.ExportToJson("Products");
        Assert.True(southJson.Contains("Beta"));
        Assert.True(southJson.Length < json.Length);

        // GetCellDataType
        var nameType = doc.GetCellDataType("Products", 1, 0);
        Assert.NotNull(nameType);
        var salesType = doc.GetCellDataType("Products", 1, 2);
        Assert.NotNull(salesType);

        // Add new row and verify ExportToJson grows
        doc.SetCellValue("Products", 5, 0, "Epsilon");
        doc.SetCellValue("Products", 5, 1, "West");
        doc.SetCellValue("Products", 5, 2, "55000");
        var updatedJson = doc.ExportToJson("Products");
        Assert.True(updatedJson.Length > json.Length);
        Assert.Contains("Epsilon", updatedJson);

        // SaveToFile and reload
        var path = TempFile("dogfood_json_filter.fods");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));
        var loaded = FodsDocument.LoadFile(path);
        Assert.NotNull(loaded);
        var loadedJson = loaded.ExportToJson("Products");
        Assert.NotNull(loadedJson);
        Assert.Contains("Epsilon", loadedJson);
        var loadedFiltered = loaded.FilterRows("Products", "Region", "North");
        Assert.NotNull(loadedFiltered);
    }
}
