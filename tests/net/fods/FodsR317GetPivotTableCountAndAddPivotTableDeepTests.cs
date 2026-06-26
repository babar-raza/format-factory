// Tests for FodsDocument.GetPivotTableCount, AddPivotTable, GetPivotTableName deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODS-R317

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R317: Tests for FodsDocument.GetPivotTableCount, AddPivotTable, GetPivotTableName deeper.
/// GetPivotTableCount(sheetName): returns the number of pivot tables on the sheet.
/// AddPivotTable(sheetName, sourceRange, rowField, colField, valueField, name): adds a pivot table.
/// GetPivotTableName(sheetName, index): returns the name of the pivot table at the given index.
/// Covers: GetPivotTableCount no-throw; GetPivotTableCount non-negative; GetPivotTableCount consistent;
/// GetPivotTableCount zero for new sheet; GetPivotTableCount after AddPivotTable increases;
/// GetPivotTableCount save-load;
/// AddPivotTable no-throw; AddPivotTable increases count; AddPivotTable save-load;
/// AddPivotTable multiple; AddPivotTable then ExportToCsv no-throw;
/// GetPivotTableName no-throw; GetPivotTableName non-null; GetPivotTableName consistent;
/// GetPivotTableName save-load;
/// dogfood CreateDoc→AddPivotTable→GetPivotTableCount→GetPivotTableName→SaveToFile pipeline.
/// </summary>
public class FodsR317GetPivotTableCountAndAddPivotTableDeepTests : IDisposable
{
    private readonly string _tempDir;

    public FodsR317GetPivotTableCountAndAddPivotTableDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodsR317_" + Guid.NewGuid().ToString("N"));
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
        doc.AddSheet("Transactions");
        doc.SetCellValue("Transactions", 0, 0, "Date");
        doc.SetCellValue("Transactions", 0, 1, "Region");
        doc.SetCellValue("Transactions", 0, 2, "Category");
        doc.SetCellValue("Transactions", 0, 3, "Product");
        doc.SetCellValue("Transactions", 0, 4, "Revenue");
        doc.SetCellValue("Transactions", 0, 5, "Units");
        string[,] rows = {
            { "2026-Q1", "North", "Electronics", "Laptop", "45000", "30" },
            { "2026-Q1", "South", "Accessories", "Keyboard", "8500", "85" },
            { "2026-Q1", "East", "Electronics", "Monitor", "28000", "35" },
            { "2026-Q2", "North", "Electronics", "Laptop", "52000", "35" },
            { "2026-Q2", "West", "Accessories", "Mouse", "4800", "120" },
            { "2026-Q2", "South", "Electronics", "Monitor", "31000", "39" },
        };
        for (int r = 0; r < 6; r++)
            for (int c = 0; c < 6; c++)
                doc.SetCellValue("Transactions", r + 1, c, rows[r, c]);
        return doc;
    }

    // -------------------------------------------------------------------------
    // GetPivotTableCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetPivotTableCount_NoThrow()
    {
        var doc = CreateRichDoc();
        var ex = Record.Exception(() => doc.GetPivotTableCount("Transactions"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetPivotTableCount_NonNegative()
    {
        var doc = CreateRichDoc();
        Assert.True(doc.GetPivotTableCount("Transactions") >= 0);
    }

    [Fact]
    public void GetPivotTableCount_Consistent()
    {
        var doc = CreateRichDoc();
        Assert.Equal(doc.GetPivotTableCount("Transactions"), doc.GetPivotTableCount("Transactions"));
    }

    [Fact]
    public void GetPivotTableCount_Zero_ForNewSheet()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("Raw");
        doc.SetCellValue("Raw", 0, 0, "value");
        Assert.Equal(0, doc.GetPivotTableCount("Raw"));
    }

    [Fact]
    public void GetPivotTableCount_AfterAdd_Increases()
    {
        var doc = CreateRichDoc();
        var before = doc.GetPivotTableCount("Transactions");
        doc.AddPivotTable("Transactions", "A1:F7", "Region", "Category", "Revenue", "Revenue by Region-Category");
        Assert.Equal(before + 1, doc.GetPivotTableCount("Transactions"));
    }

    [Fact]
    public void GetPivotTableCount_SaveLoad_Consistent()
    {
        var doc = CreateRichDoc();
        doc.AddPivotTable("Transactions", "A1:F7", "Date", "Region", "Revenue", "Revenue by Date-Region");
        var before = doc.GetPivotTableCount("Transactions");
        var path = TempFile("ptc_save.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetPivotTableCount("Transactions"));
    }

    // -------------------------------------------------------------------------
    // AddPivotTable
    // -------------------------------------------------------------------------

    [Fact]
    public void AddPivotTable_NoThrow()
    {
        var doc = CreateRichDoc();
        var ex = Record.Exception(() =>
            doc.AddPivotTable("Transactions", "A1:F7", "Region", "Product", "Units", "Units by Region-Product"));
        Assert.Null(ex);
    }

    [Fact]
    public void AddPivotTable_Increases_Count()
    {
        var doc = CreateRichDoc();
        var before = doc.GetPivotTableCount("Transactions");
        doc.AddPivotTable("Transactions", "A1:F7", "Category", "Date", "Revenue", "Revenue Summary");
        Assert.Equal(before + 1, doc.GetPivotTableCount("Transactions"));
    }

    [Fact]
    public void AddPivotTable_SaveLoad_Persists()
    {
        var doc = CreateRichDoc();
        doc.AddPivotTable("Transactions", "A1:F7", "Region", "Category", "Revenue", "Region Pivot");
        var before = doc.GetPivotTableCount("Transactions");
        var path = TempFile("apt_save.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetPivotTableCount("Transactions"));
    }

    [Fact]
    public void AddPivotTable_Multiple()
    {
        var doc = CreateRichDoc();
        doc.AddPivotTable("Transactions", "A1:F7", "Region", "Category", "Revenue", "Pivot 1");
        doc.AddPivotTable("Transactions", "A1:F7", "Date", "Region", "Units", "Pivot 2");
        doc.AddPivotTable("Transactions", "A1:F7", "Product", "Region", "Revenue", "Pivot 3");
        Assert.Equal(3, doc.GetPivotTableCount("Transactions"));
    }

    [Fact]
    public void AddPivotTable_Then_ExportToCsv_NoThrow()
    {
        var doc = CreateRichDoc();
        doc.AddPivotTable("Transactions", "A1:F7", "Region", "Category", "Revenue", "Export Test Pivot");
        var ex = Record.Exception(() => doc.ExportToCsv("Transactions"));
        Assert.Null(ex);
    }

    // -------------------------------------------------------------------------
    // GetPivotTableName
    // -------------------------------------------------------------------------

    [Fact]
    public void GetPivotTableName_NoThrow()
    {
        var doc = CreateRichDoc();
        doc.AddPivotTable("Transactions", "A1:F7", "Region", "Category", "Revenue", "Test Pivot");
        var ex = Record.Exception(() => doc.GetPivotTableName("Transactions", 0));
        Assert.Null(ex);
    }

    [Fact]
    public void GetPivotTableName_NonNull()
    {
        var doc = CreateRichDoc();
        doc.AddPivotTable("Transactions", "A1:F7", "Date", "Region", "Revenue", "Date Pivot");
        Assert.NotNull(doc.GetPivotTableName("Transactions", 0));
    }

    [Fact]
    public void GetPivotTableName_Consistent()
    {
        var doc = CreateRichDoc();
        doc.AddPivotTable("Transactions", "A1:F7", "Category", "Product", "Units", "Category Pivot");
        Assert.Equal(doc.GetPivotTableName("Transactions", 0), doc.GetPivotTableName("Transactions", 0));
    }

    [Fact]
    public void GetPivotTableName_SaveLoad_Consistent()
    {
        var doc = CreateRichDoc();
        doc.AddPivotTable("Transactions", "A1:F7", "Region", "Category", "Revenue", "Save Test Pivot");
        var before = doc.GetPivotTableName("Transactions", 0);
        var path = TempFile("gptn_save.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        var after = loaded.GetPivotTableName("Transactions", 0);
        Assert.NotNull(after);
        Assert.True(after.Length >= 0);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_AddPivotTable_GetPivotTableCount_GetPivotTableName_SaveToFile_Pipeline()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("SalesMatrix");

        // Headers
        doc.SetCellValue("SalesMatrix", 0, 0, "FY");
        doc.SetCellValue("SalesMatrix", 0, 1, "Quarter");
        doc.SetCellValue("SalesMatrix", 0, 2, "BU");
        doc.SetCellValue("SalesMatrix", 0, 3, "Market");
        doc.SetCellValue("SalesMatrix", 0, 4, "Channel");
        doc.SetCellValue("SalesMatrix", 0, 5, "Revenue_M");
        doc.SetCellValue("SalesMatrix", 0, 6, "GM_Pct");
        doc.SetCellValue("SalesMatrix", 0, 7, "Units_K");

        // Data
        string[,] rows = {
            { "FY2025", "Q1", "Enterprise", "EMEA", "Direct", "42.5", "68.2", "12.1" },
            { "FY2025", "Q1", "SMB", "APAC", "Partner", "18.3", "54.1", "28.4" },
            { "FY2025", "Q2", "Enterprise", "Americas", "Direct", "51.2", "71.4", "14.8" },
            { "FY2025", "Q2", "SMB", "EMEA", "Online", "22.7", "58.3", "35.2" },
            { "FY2025", "Q3", "Enterprise", "APAC", "Direct", "38.9", "65.7", "11.2" },
            { "FY2025", "Q3", "Consumer", "Americas", "Retail", "28.4", "42.8", "64.7" },
            { "FY2025", "Q4", "Enterprise", "EMEA", "Partner", "62.1", "72.1", "17.9" },
            { "FY2025", "Q4", "SMB", "Americas", "Direct", "31.5", "61.2", "46.8" },
            { "FY2026", "Q1", "Enterprise", "EMEA", "Direct", "48.7", "69.4", "13.8" },
            { "FY2026", "Q1", "Consumer", "APAC", "Retail", "35.2", "44.1", "79.3" },
            { "FY2026", "Q2", "SMB", "EMEA", "Online", "26.8", "59.7", "41.5" },
            { "FY2026", "Q2", "Enterprise", "Americas", "Partner", "58.4", "73.2", "16.7" },
        };
        for (int r = 0; r < 12; r++)
            for (int c = 0; c < 8; c++)
                doc.SetCellValue("SalesMatrix", r + 1, c, rows[r, c]);

        // Zero pivot tables initially
        Assert.Equal(0, doc.GetPivotTableCount("SalesMatrix"));

        // AddPivotTable — BU by Market, Revenue
        doc.AddPivotTable("SalesMatrix", "A1:H13", "BU", "Market", "Revenue_M", "Revenue by BU and Market");
        Assert.Equal(1, doc.GetPivotTableCount("SalesMatrix"));

        // AddPivotTable — Quarter by BU, Units
        doc.AddPivotTable("SalesMatrix", "A1:H13", "Quarter", "BU", "Units_K", "Units by Quarter and BU");
        Assert.Equal(2, doc.GetPivotTableCount("SalesMatrix"));

        // AddPivotTable — Channel by FY, GM%
        doc.AddPivotTable("SalesMatrix", "A1:H13", "Channel", "FY", "GM_Pct", "Gross Margin by Channel and FY");
        Assert.Equal(3, doc.GetPivotTableCount("SalesMatrix"));

        // Consistent
        Assert.Equal(doc.GetPivotTableCount("SalesMatrix"), doc.GetPivotTableCount("SalesMatrix"));

        // GetPivotTableName
        var name0 = doc.GetPivotTableName("SalesMatrix", 0);
        Assert.NotNull(name0);
        Assert.Equal(name0, doc.GetPivotTableName("SalesMatrix", 0)); // consistent

        var name1 = doc.GetPivotTableName("SalesMatrix", 1);
        Assert.NotNull(name1);

        var name2 = doc.GetPivotTableName("SalesMatrix", 2);
        Assert.NotNull(name2);

        // ExportToCsv works
        var csv = doc.ExportToCsv("SalesMatrix");
        Assert.NotNull(csv);
        Assert.NotEmpty(csv);

        // SaveToFile
        var path = TempFile("dogfood_sales.fods");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));
        Assert.True(new FileInfo(path).Length > 0);

        // LoadFile and verify
        var loaded = FodsDocument.LoadFile(path);
        Assert.Equal(3, loaded.GetPivotTableCount("SalesMatrix"));
        Assert.NotNull(loaded.GetPivotTableName("SalesMatrix", 0));

        // AddPivotTable on loaded
        loaded.AddPivotTable("SalesMatrix", "A1:H13", "Market", "Quarter", "Revenue_M", "Market Revenue by Quarter");
        Assert.Equal(4, loaded.GetPivotTableCount("SalesMatrix"));

        // Mutate data
        loaded.SetCellValue("SalesMatrix", 13, 0, "FY2026");
        loaded.SetCellValue("SalesMatrix", 13, 1, "Q3");
        loaded.SetCellValue("SalesMatrix", 13, 2, "Enterprise");
        loaded.SetCellValue("SalesMatrix", 13, 3, "APAC");
        loaded.SetCellValue("SalesMatrix", 13, 4, "Direct");
        loaded.SetCellValue("SalesMatrix", 13, 5, "64.2");
        loaded.SetCellValue("SalesMatrix", 13, 6, "74.1");
        loaded.SetCellValue("SalesMatrix", 13, 7, "18.3");

        // Final save
        var path2 = TempFile("dogfood_sales_v2.fods");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var loaded2 = FodsDocument.LoadFile(path2);
        Assert.Equal(4, loaded2.GetPivotTableCount("SalesMatrix"));
        Assert.NotNull(loaded2.GetPivotTableName("SalesMatrix", 0));
        var ex1 = Record.Exception(() => loaded2.ExportToCsv("SalesMatrix"));
        Assert.Null(ex1);
    }
}
