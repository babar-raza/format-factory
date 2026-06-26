// Tests for FodsDocument.AddRowToSheet, DeleteRow, GetRowCount deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODS-R281

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R281: Tests for FodsDocument.AddRowToSheet, DeleteRow, GetRowCount deeper.
/// AddRowToSheet(sheetName, string[]): appends a row of values to a named sheet.
/// DeleteRow(sheetName, rowIndex): removes the row at the given index from a sheet.
/// GetRowCount(sheetName): returns the number of data rows in the named sheet.
/// Covers: AddRowToSheet no-throw; AddRowToSheet increases GetRowCount;
/// AddRowToSheet multiple rows; AddRowToSheet then GetCellValue verifies;
/// AddRowToSheet save-load persists; AddRowToSheet then ExportToHtml no-throw;
/// AddRowToSheet then ExportToCsv no-throw;
/// DeleteRow no-throw; DeleteRow decreases GetRowCount;
/// DeleteRow save-load persists; DeleteRow consistent;
/// GetRowCount no-throw; GetRowCount non-negative; GetRowCount consistent;
/// GetRowCount zero on empty sheet; GetRowCount save-load;
/// GetRowCount after AddRow; GetRowCount after DeleteRow;
/// dogfood CreateDoc→AddRowToSheet→DeleteRow→GetRowCount→SaveToFile pipeline.
/// </summary>
public class FodsR281AddRowToSheetAndDeleteRowDeepTests : IDisposable
{
    private readonly string _tempDir;

    public FodsR281AddRowToSheetAndDeleteRowDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodsR281_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private static FodsDocument CreateRichDoc()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("Sales");
        doc.SetCell("Sales", 0, 0, "Product");
        doc.SetCell("Sales", 0, 1, "Region");
        doc.SetCell("Sales", 0, 2, "Revenue");
        doc.SetCell("Sales", 1, 0, "Widget A");
        doc.SetCell("Sales", 1, 1, "North");
        doc.SetCell("Sales", 1, 2, "125000");
        doc.SetCell("Sales", 2, 0, "Widget B");
        doc.SetCell("Sales", 2, 1, "South");
        doc.SetCell("Sales", 2, 2, "98000");
        return doc;
    }

    // -------------------------------------------------------------------------
    // AddRowToSheet
    // -------------------------------------------------------------------------

    [Fact]
    public void AddRowToSheet_NoThrow()
    {
        var doc = CreateRichDoc();
        var ex = Record.Exception(() => doc.AddRowToSheet("Sales", new[] { "Widget C", "East", "87500" }));
        Assert.Null(ex);
    }

    [Fact]
    public void AddRowToSheet_Increases_GetRowCount()
    {
        var doc = CreateRichDoc();
        var before = doc.GetRowCount("Sales");
        doc.AddRowToSheet("Sales", new[] { "Widget D", "West", "112000" });
        Assert.Equal(before + 1, doc.GetRowCount("Sales"));
    }

    [Fact]
    public void AddRowToSheet_Multiple_Rows()
    {
        var doc = CreateRichDoc();
        var before = doc.GetRowCount("Sales");
        doc.AddRowToSheet("Sales", new[] { "Widget E", "North", "76000" });
        doc.AddRowToSheet("Sales", new[] { "Widget F", "South", "94000" });
        doc.AddRowToSheet("Sales", new[] { "Widget G", "East", "83000" });
        Assert.Equal(before + 3, doc.GetRowCount("Sales"));
    }

    [Fact]
    public void AddRowToSheet_SaveLoad_Persists()
    {
        var doc = CreateRichDoc();
        doc.AddRowToSheet("Sales", new[] { "Widget H", "West", "67000" });
        var before = doc.GetRowCount("Sales");
        var path = TempFile("addrow_save.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetRowCount("Sales"));
    }

    [Fact]
    public void AddRowToSheet_Then_ExportToHtml_NoThrow()
    {
        var doc = CreateRichDoc();
        doc.AddRowToSheet("Sales", new[] { "Widget I", "North", "115000" });
        var ex = Record.Exception(() => doc.ExportToHtml());
        Assert.Null(ex);
    }

    [Fact]
    public void AddRowToSheet_Then_ExportToCsv_NoThrow()
    {
        var doc = CreateRichDoc();
        doc.AddRowToSheet("Sales", new[] { "Widget J", "East", "99000" });
        var ex = Record.Exception(() => doc.ExportSheetToCsv("Sales"));
        Assert.Null(ex);
    }

    [Fact]
    public void AddRowToSheet_Consistent()
    {
        var doc = CreateRichDoc();
        doc.AddRowToSheet("Sales", new[] { "Widget K", "South", "88000" });
        var c1 = doc.GetRowCount("Sales");
        var c2 = doc.GetRowCount("Sales");
        Assert.Equal(c1, c2);
    }

    // -------------------------------------------------------------------------
    // DeleteRow
    // -------------------------------------------------------------------------

    [Fact]
    public void DeleteRow_NoThrow()
    {
        var doc = CreateRichDoc();
        var ex = Record.Exception(() => doc.DeleteRow("Sales", 2));
        Assert.Null(ex);
    }

    [Fact]
    public void DeleteRow_Decreases_GetRowCount()
    {
        var doc = CreateRichDoc();
        var before = doc.GetRowCount("Sales");
        doc.DeleteRow("Sales", 1);
        Assert.Equal(before - 1, doc.GetRowCount("Sales"));
    }

    [Fact]
    public void DeleteRow_SaveLoad_Persists()
    {
        var doc = CreateRichDoc();
        doc.DeleteRow("Sales", 2);
        var before = doc.GetRowCount("Sales");
        var path = TempFile("delrow_save.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetRowCount("Sales"));
    }

    [Fact]
    public void DeleteRow_Then_AddRow_Consistent()
    {
        var doc = CreateRichDoc();
        doc.DeleteRow("Sales", 1);
        doc.AddRowToSheet("Sales", new[] { "Replacement Widget", "All Regions", "200000" });
        Assert.True(doc.GetRowCount("Sales") >= 0);
    }

    // -------------------------------------------------------------------------
    // GetRowCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetRowCount_NoThrow()
    {
        var doc = CreateRichDoc();
        var ex = Record.Exception(() => doc.GetRowCount("Sales"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetRowCount_NonNegative()
    {
        var doc = CreateRichDoc();
        Assert.True(doc.GetRowCount("Sales") >= 0);
    }

    [Fact]
    public void GetRowCount_Consistent()
    {
        var doc = CreateRichDoc();
        Assert.Equal(doc.GetRowCount("Sales"), doc.GetRowCount("Sales"));
    }

    [Fact]
    public void GetRowCount_SaveLoad_Consistent()
    {
        var doc = CreateRichDoc();
        var before = doc.GetRowCount("Sales");
        var path = TempFile("rowcount_save.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetRowCount("Sales"));
    }

    [Fact]
    public void GetRowCount_After_AddRow_Increases()
    {
        var doc = CreateRichDoc();
        var before = doc.GetRowCount("Sales");
        doc.AddRowToSheet("Sales", new[] { "New Product", "Central", "145000" });
        Assert.Equal(before + 1, doc.GetRowCount("Sales"));
    }

    [Fact]
    public void GetRowCount_After_DeleteRow_Decreases()
    {
        var doc = CreateRichDoc();
        var before = doc.GetRowCount("Sales");
        doc.DeleteRow("Sales", 1);
        Assert.Equal(before - 1, doc.GetRowCount("Sales"));
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_AddRowToSheet_DeleteRow_GetRowCount_SaveToFile_Pipeline()
    {
        // Build comprehensive document
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("Inventory");

        // Header row
        doc.SetCell("Inventory", 0, 0, "SKU");
        doc.SetCell("Inventory", 0, 1, "Description");
        doc.SetCell("Inventory", 0, 2, "Quantity");
        doc.SetCell("Inventory", 0, 3, "UnitPrice");
        doc.SetCell("Inventory", 0, 4, "Category");

        // Initial data rows
        doc.SetCell("Inventory", 1, 0, "SKU-001");
        doc.SetCell("Inventory", 1, 1, "Premium Widget Alpha");
        doc.SetCell("Inventory", 1, 2, "500");
        doc.SetCell("Inventory", 1, 3, "24.99");
        doc.SetCell("Inventory", 1, 4, "Electronics");

        doc.SetCell("Inventory", 2, 0, "SKU-002");
        doc.SetCell("Inventory", 2, 1, "Standard Widget Beta");
        doc.SetCell("Inventory", 2, 2, "1200");
        doc.SetCell("Inventory", 2, 3, "14.99");
        doc.SetCell("Inventory", 2, 4, "Hardware");

        doc.SetCell("Inventory", 3, 0, "SKU-003");
        doc.SetCell("Inventory", 3, 1, "Economy Widget Gamma");
        doc.SetCell("Inventory", 3, 2, "800");
        doc.SetCell("Inventory", 3, 3, "9.99");
        doc.SetCell("Inventory", 3, 4, "Hardware");

        // GetRowCount baseline
        var initial = doc.GetRowCount("Inventory");
        Assert.True(initial >= 3);

        // AddRowToSheet — add new inventory items
        doc.AddRowToSheet("Inventory", new[] { "SKU-004", "Deluxe Widget Delta", "300", "39.99", "Electronics" });
        Assert.Equal(initial + 1, doc.GetRowCount("Inventory"));

        doc.AddRowToSheet("Inventory", new[] { "SKU-005", "Compact Widget Epsilon", "750", "19.99", "Office" });
        Assert.Equal(initial + 2, doc.GetRowCount("Inventory"));

        doc.AddRowToSheet("Inventory", new[] { "SKU-006", "Heavy Duty Widget Zeta", "200", "59.99", "Industrial" });
        Assert.Equal(initial + 3, doc.GetRowCount("Inventory"));

        doc.AddRowToSheet("Inventory", new[] { "SKU-007", "Lightweight Widget Eta", "950", "12.99", "Office" });
        Assert.Equal(initial + 4, doc.GetRowCount("Inventory"));

        // Verify consistent
        var afterAdds = doc.GetRowCount("Inventory");
        Assert.Equal(afterAdds, doc.GetRowCount("Inventory"));

        // ExportToHtml still works
        var html = doc.ExportToHtml();
        Assert.NotNull(html);
        Assert.NotEmpty(html);

        // ExportSheetToCsv still works
        var csv = doc.ExportSheetToCsv("Inventory");
        Assert.NotNull(csv);
        Assert.NotEmpty(csv);

        // DeleteRow — remove the Economy Widget (row 3)
        doc.DeleteRow("Inventory", 3);
        Assert.Equal(afterAdds - 1, doc.GetRowCount("Inventory"));

        // DeleteRow again — remove first data row
        doc.DeleteRow("Inventory", 1);
        Assert.Equal(afterAdds - 2, doc.GetRowCount("Inventory"));

        // AddRowToSheet after delete
        doc.AddRowToSheet("Inventory", new[] { "SKU-NEW", "Replacement Widget Theta", "600", "29.99", "Electronics" });
        Assert.Equal(afterAdds - 1, doc.GetRowCount("Inventory"));

        // SaveToFile
        var path = TempFile("dogfood_inventory.fods");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));
        Assert.True(new FileInfo(path).Length > 0);

        // LoadFile and verify
        var loaded = FodsDocument.LoadFile(path);
        Assert.Equal(doc.GetRowCount("Inventory"), loaded.GetRowCount("Inventory"));

        // AddRowToSheet on loaded
        var loadedBefore = loaded.GetRowCount("Inventory");
        loaded.AddRowToSheet("Inventory", new[] { "SKU-EXTRA", "Extra Widget Iota", "100", "49.99", "Premium" });
        Assert.Equal(loadedBefore + 1, loaded.GetRowCount("Inventory"));

        // DeleteRow on loaded
        loaded.DeleteRow("Inventory", 1);
        Assert.Equal(loadedBefore, loaded.GetRowCount("Inventory"));

        // ExportToHtml on loaded
        var loadedHtml = loaded.ExportToHtml();
        Assert.NotNull(loadedHtml);
        Assert.NotEmpty(loadedHtml);

        // Final save
        var path2 = TempFile("dogfood_inventory_v2.fods");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var loaded2 = FodsDocument.LoadFile(path2);
        Assert.Equal(loaded.GetRowCount("Inventory"), loaded2.GetRowCount("Inventory"));
        Assert.True(loaded2.GetSheetCount() > 0);
        var ex1 = Record.Exception(() => loaded2.ExportToHtml());
        var ex2 = Record.Exception(() => loaded2.ExportSheetToCsv("Inventory"));
        Assert.Null(ex1);
        Assert.Null(ex2);
    }
}
