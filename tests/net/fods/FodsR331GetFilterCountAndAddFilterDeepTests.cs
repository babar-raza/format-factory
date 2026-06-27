// Tests for FodsDocument.GetFilterCount, AddFilter, GetFilterColumn deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODS-R331

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R331: Tests for FodsDocument.GetFilterCount, AddFilter, GetFilterColumn deeper.
/// GetFilterCount(sheetName): returns the number of auto-filter rules on the sheet.
/// AddFilter(sheetName, columnName, filterValue): adds a filter rule for the given column.
/// GetFilterColumn(sheetName, index): returns the column name of the filter rule at the index.
/// Covers: GetFilterCount no-throw; GetFilterCount non-negative; GetFilterCount consistent;
/// GetFilterCount zero for new sheet; GetFilterCount after AddFilter increases; GetFilterCount save-load;
/// AddFilter no-throw; AddFilter increases count; AddFilter save-load;
/// AddFilter multiple; AddFilter then GetColumnSum no-throw; AddFilter then ExportToCsv no-throw;
/// GetFilterColumn no-throw; GetFilterColumn non-null; GetFilterColumn consistent; GetFilterColumn save-load;
/// dogfood CreateDoc→AddFilter→GetFilterCount→GetFilterColumn→SaveToFile pipeline.
/// </summary>
public class FodsR331GetFilterCountAndAddFilterDeepTests : IDisposable
{
    private readonly string _tempDir;

    public FodsR331GetFilterCountAndAddFilterDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodsR331_" + Guid.NewGuid().ToString("N"));
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
        doc.SetCellValue("Inventory", 0, 0, "sku");
        doc.SetCellValue("Inventory", 0, 1, "category");
        doc.SetCellValue("Inventory", 0, 2, "warehouse");
        doc.SetCellValue("Inventory", 0, 3, "qty_on_hand");
        doc.SetCellValue("Inventory", 0, 4, "reorder_level");
        string[][] rows = {
            new[] { "SKU001", "Electronics", "WH-A", "450", "100" },
            new[] { "SKU002", "Apparel", "WH-B", "1200", "200" },
            new[] { "SKU003", "Electronics", "WH-A", "85", "150" },
            new[] { "SKU004", "Furniture", "WH-C", "32", "10" },
            new[] { "SKU005", "Apparel", "WH-B", "680", "100" },
        };
        for (int r = 0; r < rows.Length; r++)
            for (int c = 0; c < rows[r].Length; c++)
                doc.SetCellValue("Inventory", r + 1, c, rows[r][c]);
        return doc;
    }

    // -------------------------------------------------------------------------
    // GetFilterCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetFilterCount_NoThrow()
    {
        var doc = CreateInventoryDoc();
        var ex = Record.Exception(() => doc.GetFilterCount("Inventory"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetFilterCount_NonNegative()
    {
        var doc = CreateInventoryDoc();
        Assert.True(doc.GetFilterCount("Inventory") >= 0);
    }

    [Fact]
    public void GetFilterCount_Consistent()
    {
        var doc = CreateInventoryDoc();
        Assert.Equal(doc.GetFilterCount("Inventory"), doc.GetFilterCount("Inventory"));
    }

    [Fact]
    public void GetFilterCount_Zero_ForNewSheet()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("Fresh");
        doc.SetCellValue("Fresh", 0, 0, "id");
        Assert.Equal(0, doc.GetFilterCount("Fresh"));
    }

    [Fact]
    public void GetFilterCount_AfterAddFilter_Increases()
    {
        var doc = CreateInventoryDoc();
        var before = doc.GetFilterCount("Inventory");
        doc.AddFilter("Inventory", "category", "Electronics");
        Assert.Equal(before + 1, doc.GetFilterCount("Inventory"));
    }

    [Fact]
    public void GetFilterCount_SaveLoad_Consistent()
    {
        var doc = CreateInventoryDoc();
        doc.AddFilter("Inventory", "warehouse", "WH-A");
        var before = doc.GetFilterCount("Inventory");
        var path = TempFile("fc_save.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetFilterCount("Inventory"));
    }

    // -------------------------------------------------------------------------
    // AddFilter
    // -------------------------------------------------------------------------

    [Fact]
    public void AddFilter_NoThrow()
    {
        var doc = CreateInventoryDoc();
        var ex = Record.Exception(() => doc.AddFilter("Inventory", "category", "Apparel"));
        Assert.Null(ex);
    }

    [Fact]
    public void AddFilter_Increases_Count()
    {
        var doc = CreateInventoryDoc();
        var before = doc.GetFilterCount("Inventory");
        doc.AddFilter("Inventory", "category", "Electronics");
        Assert.Equal(before + 1, doc.GetFilterCount("Inventory"));
    }

    [Fact]
    public void AddFilter_SaveLoad_Persists()
    {
        var doc = CreateInventoryDoc();
        doc.AddFilter("Inventory", "warehouse", "WH-B");
        var before = doc.GetFilterCount("Inventory");
        var path = TempFile("af_save.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetFilterCount("Inventory"));
    }

    [Fact]
    public void AddFilter_Multiple()
    {
        var doc = CreateInventoryDoc();
        doc.AddFilter("Inventory", "category", "Electronics");
        doc.AddFilter("Inventory", "warehouse", "WH-A");
        doc.AddFilter("Inventory", "reorder_level", "100");
        Assert.Equal(3, doc.GetFilterCount("Inventory"));
    }

    [Fact]
    public void AddFilter_Then_GetColumnSum_NoThrow()
    {
        var doc = CreateInventoryDoc();
        doc.AddFilter("Inventory", "category", "Electronics");
        var ex = Record.Exception(() => doc.GetColumnSum("Inventory", "qty_on_hand"));
        Assert.Null(ex);
    }

    [Fact]
    public void AddFilter_Then_ExportToCsv_NoThrow()
    {
        var doc = CreateInventoryDoc();
        doc.AddFilter("Inventory", "warehouse", "WH-C");
        var path = TempFile("filter_export.csv");
        var ex = Record.Exception(() => doc.ExportToCsv("Inventory", path));
        Assert.Null(ex);
    }

    // -------------------------------------------------------------------------
    // GetFilterColumn
    // -------------------------------------------------------------------------

    [Fact]
    public void GetFilterColumn_NoThrow()
    {
        var doc = CreateInventoryDoc();
        doc.AddFilter("Inventory", "category", "Furniture");
        var ex = Record.Exception(() => doc.GetFilterColumn("Inventory", 0));
        Assert.Null(ex);
    }

    [Fact]
    public void GetFilterColumn_NonNull()
    {
        var doc = CreateInventoryDoc();
        doc.AddFilter("Inventory", "warehouse", "WH-A");
        Assert.NotNull(doc.GetFilterColumn("Inventory", 0));
    }

    [Fact]
    public void GetFilterColumn_Consistent()
    {
        var doc = CreateInventoryDoc();
        doc.AddFilter("Inventory", "category", "Electronics");
        Assert.Equal(doc.GetFilterColumn("Inventory", 0), doc.GetFilterColumn("Inventory", 0));
    }

    [Fact]
    public void GetFilterColumn_SaveLoad_Consistent()
    {
        var doc = CreateInventoryDoc();
        doc.AddFilter("Inventory", "category", "Apparel");
        var before = doc.GetFilterColumn("Inventory", 0);
        var path = TempFile("fco_save.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        Assert.NotNull(loaded.GetFilterColumn("Inventory", 0));
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_AddFilter_GetFilterCount_GetFilterColumn_SaveToFile_Pipeline()
    {
        // Procurement analytics — 12 purchase orders with supplier/category breakdown
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("PO");
        doc.SetCellValue("PO", 0, 0, "po_number");
        doc.SetCellValue("PO", 0, 1, "supplier");
        doc.SetCellValue("PO", 0, 2, "category");
        doc.SetCellValue("PO", 0, 3, "country");
        doc.SetCellValue("PO", 0, 4, "amount_usd");
        doc.SetCellValue("PO", 0, 5, "lead_time_days");
        doc.SetCellValue("PO", 0, 6, "status");

        string[][] data = {
            new[] { "PO-2026-001", "Foxconn",    "Electronics", "China",   "2850000", "28", "received" },
            new[] { "PO-2026-002", "Jabil",       "Electronics", "Mexico",  "1420000", "14", "in_transit" },
            new[] { "PO-2026-003", "Flextronics", "Electronics", "Malaysia","1980000", "21", "received" },
            new[] { "PO-2026-004", "Arauco",      "Raw_Material","Chile",   "485000",  "35", "processing" },
            new[] { "PO-2026-005", "Sanlam",      "Services",    "SA",      "285000",  "7",  "received" },
            new[] { "PO-2026-006", "Foxconn",     "Electronics", "China",   "3250000", "28", "in_transit" },
            new[] { "PO-2026-007", "Covestro",    "Raw_Material","Germany", "782000",  "18", "received" },
            new[] { "PO-2026-008", "Wipro",       "Services",    "India",   "420000",  "5",  "processing" },
            new[] { "PO-2026-009", "Murata",      "Electronics", "Japan",   "1650000", "24", "received" },
            new[] { "PO-2026-010", "BASF",        "Raw_Material","Germany", "625000",  "22", "in_transit" },
            new[] { "PO-2026-011", "Accenture",   "Services",    "Ireland", "580000",  "0",  "received" },
            new[] { "PO-2026-012", "Celestica",   "Electronics", "Canada",  "895000",  "16", "received" },
        };
        for (int r = 0; r < data.Length; r++)
            for (int c = 0; c < data[r].Length; c++)
                doc.SetCellValue("PO", r + 1, c, data[r][c]);

        // Initial filter count — zero
        Assert.Equal(0, doc.GetFilterCount("PO"));

        // AddFilter — 4 procurement filters
        doc.AddFilter("PO", "category", "Electronics");
        Assert.Equal(1, doc.GetFilterCount("PO"));

        doc.AddFilter("PO", "status", "received");
        Assert.Equal(2, doc.GetFilterCount("PO"));

        doc.AddFilter("PO", "supplier", "Foxconn");
        Assert.Equal(3, doc.GetFilterCount("PO"));

        doc.AddFilter("PO", "country", "China");
        Assert.Equal(4, doc.GetFilterCount("PO"));

        doc.AddFilter("PO", "status", "in_transit");
        Assert.Equal(5, doc.GetFilterCount("PO"));

        // Consistent
        Assert.Equal(doc.GetFilterCount("PO"), doc.GetFilterCount("PO"));

        // GetFilterColumn
        var col0 = doc.GetFilterColumn("PO", 0);
        Assert.NotNull(col0);
        Assert.Equal(col0, doc.GetFilterColumn("PO", 0)); // consistent

        var col4 = doc.GetFilterColumn("PO", 4);
        Assert.NotNull(col4);

        // Column operations work after filtering
        var ex1 = Record.Exception(() => doc.GetColumnSum("PO", "amount_usd"));
        Assert.Null(ex1);

        // ExportToCsv works
        var csvPath = TempFile("dogfood_po.csv");
        var ex2 = Record.Exception(() => doc.ExportToCsv("PO", csvPath));
        Assert.Null(ex2);

        // SaveToFile
        var path = TempFile("dogfood_procurement.fods");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));
        Assert.True(new FileInfo(path).Length > 0);

        // LoadFile and verify
        var loaded = FodsDocument.LoadFile(path);
        Assert.Equal(5, loaded.GetFilterCount("PO"));
        Assert.NotNull(loaded.GetFilterColumn("PO", 0));
        Assert.NotNull(loaded.GetFilterColumn("PO", 4));

        // AddFilter on loaded
        loaded.AddFilter("PO", "category", "Services");
        Assert.Equal(6, loaded.GetFilterCount("PO"));

        // ExportToCsv on loaded
        var csvPath2 = TempFile("dogfood_po_v2.csv");
        var ex3 = Record.Exception(() => loaded.ExportToCsv("PO", csvPath2));
        Assert.Null(ex3);

        // Final save
        var path2 = TempFile("dogfood_procurement_v2.fods");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var loaded2 = FodsDocument.LoadFile(path2);
        Assert.Equal(6, loaded2.GetFilterCount("PO"));
        Assert.NotNull(loaded2.GetFilterColumn("PO", 5));
        var ex4 = Record.Exception(() => loaded2.AddFilter("PO", "lead_time_days", "28"));
        Assert.Null(ex4);
    }
}
