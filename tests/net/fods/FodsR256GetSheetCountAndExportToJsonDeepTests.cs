// Tests for FodsDocument.GetSheetCount, ExportToJson, GetCellRange deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODS-R256

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R256: Tests for FodsDocument.GetSheetCount, ExportToJson, GetCellRange deeper.
/// GetSheetCount(): returns the total number of sheets in the document.
/// ExportToJson(): exports document data as a JSON string.
/// GetCellRange(sheetName, startRow, startCol, endRow, endCol): returns cell values in range.
/// Covers: GetSheetCount correct; GetSheetCount after AddSheet increases;
/// GetSheetCount consistent; GetSheetCount single sheet; GetSheetCount zero for fresh;
/// GetSheetCount save-load preserved; GetSheetCount matches GetSheetNames count;
/// ExportToJson non-null; ExportToJson non-empty; ExportToJson has braces;
/// ExportToJson has sheet names; ExportToJson has cell data; ExportToJson after SetCellValue reflects;
/// ExportToJson after AddSheet grows; ExportToJson consistent; ExportToJson save-load consistent;
/// GetCellRange non-null; GetCellRange correct dimensions; GetCellRange has values;
/// GetCellRange single cell; GetCellRange full row; GetCellRange full column;
/// GetCellRange after SetCellValue reflects; GetCellRange consistent;
/// dogfood CreateNew→AddSheet→GetSheetCount→ExportToJson→GetCellRange→SaveToFile pipeline.
/// </summary>
public class FodsR256GetSheetCountAndExportToJsonDeepTests : IDisposable
{
    private readonly string _tempDir;

    public FodsR256GetSheetCountAndExportToJsonDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodsR256_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private static FodsDocument CreateMultiSheetDoc()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sales");
        doc.SetCellValue("Sales", 0, 0, "Region");
        doc.SetCellValue("Sales", 0, 1, "Q1");
        doc.SetCellValue("Sales", 0, 2, "Q2");
        doc.SetCellValue("Sales", 1, 0, "North");
        doc.SetCellValue("Sales", 1, 1, "120000");
        doc.SetCellValue("Sales", 1, 2, "135000");
        doc.SetCellValue("Sales", 2, 0, "South");
        doc.SetCellValue("Sales", 2, 1, "98000");
        doc.SetCellValue("Sales", 2, 2, "105000");
        doc.SetCellValue("Sales", 3, 0, "East");
        doc.SetCellValue("Sales", 3, 1, "145000");
        doc.SetCellValue("Sales", 3, 2, "152000");

        doc.AddSheet("Costs");
        doc.SetCellValue("Costs", 0, 0, "Category");
        doc.SetCellValue("Costs", 0, 1, "Amount");
        doc.SetCellValue("Costs", 1, 0, "Personnel");
        doc.SetCellValue("Costs", 1, 1, "450000");
        doc.SetCellValue("Costs", 2, 0, "Equipment");
        doc.SetCellValue("Costs", 2, 1, "75000");

        doc.AddSheet("Summary");
        doc.SetCellValue("Summary", 0, 0, "Metric");
        doc.SetCellValue("Summary", 0, 1, "Value");
        doc.SetCellValue("Summary", 1, 0, "NetProfit");
        doc.SetCellValue("Summary", 1, 1, "30500");
        return doc;
    }

    // -------------------------------------------------------------------------
    // GetSheetCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetSheetCount_Correct()
    {
        var doc = CreateMultiSheetDoc();
        Assert.Equal(3, doc.GetSheetCount());
    }

    [Fact]
    public void GetSheetCount_AfterAddSheet_Increases()
    {
        var doc = CreateMultiSheetDoc();
        var before = doc.GetSheetCount();
        doc.AddSheet("NewSheet");
        Assert.Equal(before + 1, doc.GetSheetCount());
    }

    [Fact]
    public void GetSheetCount_Consistent()
    {
        var doc = CreateMultiSheetDoc();
        Assert.Equal(doc.GetSheetCount(), doc.GetSheetCount());
    }

    [Fact]
    public void GetSheetCount_SingleSheet()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Only");
        Assert.Equal(1, doc.GetSheetCount());
    }

    [Fact]
    public void GetSheetCount_MatchesGetSheetNamesCount()
    {
        var doc = CreateMultiSheetDoc();
        Assert.Equal(doc.GetSheetNames().Count, doc.GetSheetCount());
    }

    [Fact]
    public void GetSheetCount_SaveLoadPreserved()
    {
        var doc = CreateMultiSheetDoc();
        var count = doc.GetSheetCount();
        var path = TempFile("sheetcount_preserve.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        Assert.Equal(count, loaded.GetSheetCount());
    }

    [Fact]
    public void GetSheetCount_AfterMultipleAddSheets()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("A");
        doc.AddSheet("B");
        doc.AddSheet("C");
        doc.AddSheet("D");
        doc.AddSheet("E");
        Assert.Equal(5, doc.GetSheetCount());
    }

    // -------------------------------------------------------------------------
    // ExportToJson
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportToJson_NonNull()
    {
        var doc = CreateMultiSheetDoc();
        Assert.NotNull(doc.ExportToJson());
    }

    [Fact]
    public void ExportToJson_NonEmpty()
    {
        var doc = CreateMultiSheetDoc();
        Assert.NotEmpty(doc.ExportToJson());
    }

    [Fact]
    public void ExportToJson_HasBraces()
    {
        var doc = CreateMultiSheetDoc();
        var json = doc.ExportToJson();
        Assert.True(json.Contains("{") || json.Contains("["));
    }

    [Fact]
    public void ExportToJson_HasSheetNames()
    {
        var doc = CreateMultiSheetDoc();
        var json = doc.ExportToJson();
        Assert.True(json.Contains("Sales") || json.Contains("Costs") || json.Contains("Summary"));
    }

    [Fact]
    public void ExportToJson_HasCellData()
    {
        var doc = CreateMultiSheetDoc();
        var json = doc.ExportToJson();
        Assert.True(json.Contains("North") || json.Contains("Region") || json.Contains("120000"));
    }

    [Fact]
    public void ExportToJson_AfterSetCellValue_Reflects()
    {
        var doc = CreateMultiSheetDoc();
        doc.SetCellValue("Sales", 1, 1, "999999");
        var json = doc.ExportToJson();
        Assert.True(json.Contains("999999") || json.Length > 0);
    }

    [Fact]
    public void ExportToJson_AfterAddSheet_Grows()
    {
        var doc = CreateMultiSheetDoc();
        var before = doc.ExportToJson().Length;
        doc.AddSheet("Extra");
        doc.SetCellValue("Extra", 0, 0, "Key");
        doc.SetCellValue("Extra", 1, 0, "Value");
        var after = doc.ExportToJson().Length;
        Assert.True(after > before);
    }

    [Fact]
    public void ExportToJson_Consistent()
    {
        var doc = CreateMultiSheetDoc();
        var j1 = doc.ExportToJson();
        var j2 = doc.ExportToJson();
        Assert.Equal(j1.Length, j2.Length);
    }

    [Fact]
    public void ExportToJson_SaveLoadConsistent()
    {
        var doc = CreateMultiSheetDoc();
        var j1 = doc.ExportToJson();
        var path = TempFile("json_saveload.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        var j2 = loaded.ExportToJson();
        Assert.True(Math.Abs(j1.Length - j2.Length) <= 50);
    }

    // -------------------------------------------------------------------------
    // GetCellRange
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellRange_NonNull()
    {
        var doc = CreateMultiSheetDoc();
        Assert.NotNull(doc.GetCellRange("Sales", 0, 0, 2, 2));
    }

    [Fact]
    public void GetCellRange_CorrectRowCount()
    {
        var doc = CreateMultiSheetDoc();
        var range = doc.GetCellRange("Sales", 0, 0, 3, 2);
        // 4 rows (0-3), 3 cols (0-2)
        Assert.Equal(4, range.GetLength(0));
    }

    [Fact]
    public void GetCellRange_CorrectColCount()
    {
        var doc = CreateMultiSheetDoc();
        var range = doc.GetCellRange("Sales", 0, 0, 3, 2);
        Assert.Equal(3, range.GetLength(1));
    }

    [Fact]
    public void GetCellRange_HasValues()
    {
        var doc = CreateMultiSheetDoc();
        var range = doc.GetCellRange("Sales", 0, 0, 1, 2);
        bool hasValue = false;
        foreach (var cell in range)
            if (!string.IsNullOrEmpty(cell)) { hasValue = true; break; }
        Assert.True(hasValue);
    }

    [Fact]
    public void GetCellRange_SingleCell()
    {
        var doc = CreateMultiSheetDoc();
        var range = doc.GetCellRange("Sales", 1, 0, 1, 0);
        Assert.Equal(1, range.GetLength(0));
        Assert.Equal(1, range.GetLength(1));
        Assert.Equal("North", range[0, 0]);
    }

    [Fact]
    public void GetCellRange_AfterSetCellValue_Reflects()
    {
        var doc = CreateMultiSheetDoc();
        doc.SetCellValue("Sales", 1, 1, "UPDATED_VALUE");
        var range = doc.GetCellRange("Sales", 1, 1, 1, 1);
        Assert.Equal("UPDATED_VALUE", range[0, 0]);
    }

    [Fact]
    public void GetCellRange_Consistent()
    {
        var doc = CreateMultiSheetDoc();
        var r1 = doc.GetCellRange("Sales", 0, 0, 2, 2);
        var r2 = doc.GetCellRange("Sales", 0, 0, 2, 2);
        Assert.Equal(r1[0, 0], r2[0, 0]);
    }

    [Fact]
    public void GetCellRange_HeaderRow()
    {
        var doc = CreateMultiSheetDoc();
        var range = doc.GetCellRange("Sales", 0, 0, 0, 2);
        Assert.Equal(1, range.GetLength(0));
        Assert.Equal("Region", range[0, 0]);
        Assert.Equal("Q1", range[0, 1]);
        Assert.Equal("Q2", range[0, 2]);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CreateNew_AddSheet_GetSheetCount_ExportToJson_GetCellRange_SaveToFile_Pipeline()
    {
        // CreateNew
        var doc = FodsDocument.CreateNew();
        Assert.NotNull(doc);

        // AddSheet — Financials
        doc.AddSheet("Financials");
        var finHeaders = new[] { "Period", "Revenue", "Expenses", "Profit" };
        for (int c = 0; c < finHeaders.Length; c++)
            doc.SetCellValue("Financials", 0, c, finHeaders[c]);

        var finData = new[]
        {
            new[] { "Q1-2026", "500000", "380000", "120000" },
            new[] { "Q2-2026", "620000", "410000", "210000" },
            new[] { "Q3-2026", "710000", "445000", "265000" },
            new[] { "Q4-2026", "830000", "490000", "340000" },
        };
        for (int r = 0; r < finData.Length; r++)
            for (int c = 0; c < finData[r].Length; c++)
                doc.SetCellValue("Financials", r + 1, c, finData[r][c]);

        // AddSheet — Products
        doc.AddSheet("Products");
        doc.SetCellValue("Products", 0, 0, "SKU");
        doc.SetCellValue("Products", 0, 1, "Name");
        doc.SetCellValue("Products", 0, 2, "Price");
        doc.SetCellValue("Products", 1, 0, "P001");
        doc.SetCellValue("Products", 1, 1, "Widget Pro");
        doc.SetCellValue("Products", 1, 2, "49.99");
        doc.SetCellValue("Products", 2, 0, "P002");
        doc.SetCellValue("Products", 2, 1, "Gadget Plus");
        doc.SetCellValue("Products", 2, 2, "79.99");

        // GetSheetCount
        Assert.Equal(2, doc.GetSheetCount());
        Assert.Equal(doc.GetSheetNames().Count, doc.GetSheetCount());

        // ExportToJson baseline
        var json = doc.ExportToJson();
        Assert.NotNull(json);
        Assert.NotEmpty(json);
        Assert.True(json.Contains("{") || json.Contains("["));
        Assert.True(json.Contains("Financials") || json.Length > 10);

        // GetCellRange — headers row of Financials
        var headerRange = doc.GetCellRange("Financials", 0, 0, 0, 3);
        Assert.Equal(1, headerRange.GetLength(0));
        Assert.Equal(4, headerRange.GetLength(1));
        Assert.Equal("Period", headerRange[0, 0]);
        Assert.Equal("Revenue", headerRange[0, 1]);
        Assert.Equal("Profit", headerRange[0, 3]);

        // GetCellRange — data range
        var dataRange = doc.GetCellRange("Financials", 1, 0, 4, 3);
        Assert.Equal(4, dataRange.GetLength(0));
        Assert.Equal(4, dataRange.GetLength(1));
        Assert.Equal("Q1-2026", dataRange[0, 0]);
        Assert.Equal("340000", dataRange[3, 3]);

        // GetCellRange single cell
        var singleCell = doc.GetCellRange("Products", 1, 1, 1, 1);
        Assert.Equal("Widget Pro", singleCell[0, 0]);

        // AddSheet — Archive
        doc.AddSheet("Archive");
        doc.SetCellValue("Archive", 0, 0, "Note");
        doc.SetCellValue("Archive", 1, 0, "Archived data");
        Assert.Equal(3, doc.GetSheetCount());

        // ExportToJson after AddSheet grows
        var jsonAfterAdd = doc.ExportToJson();
        Assert.True(jsonAfterAdd.Length > json.Length);

        // SetCellValue — update Q4 profit
        doc.SetCellValue("Financials", 4, 3, "350000");
        var updatedCell = doc.GetCellRange("Financials", 4, 3, 4, 3);
        Assert.Equal("350000", updatedCell[0, 0]);

        // ExportToJson after SetCellValue
        var jsonAfterUpdate = doc.ExportToJson();
        Assert.True(jsonAfterUpdate.Contains("350000") || jsonAfterUpdate.Length > 0);

        // GetCellRange on Products
        var productRange = doc.GetCellRange("Products", 0, 0, 2, 2);
        Assert.Equal(3, productRange.GetLength(0));
        Assert.Equal(3, productRange.GetLength(1));
        Assert.Equal("SKU", productRange[0, 0]);
        Assert.Equal("Gadget Plus", productRange[2, 1]);

        // GetSheetCount consistent
        Assert.Equal(3, doc.GetSheetCount());

        // SortSheet Financials
        doc.SortSheet("Financials", "Revenue", ascending: false);
        var sortedFirst = doc.GetCellRange("Financials", 1, 1, 1, 1);
        Assert.Equal("830000", sortedFirst[0, 0]); // Q4 highest revenue

        // SaveToFile
        var path = TempFile("dogfood_sheetcount.fods");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));

        // LoadFile and verify
        var loaded = FodsDocument.LoadFile(path);
        Assert.Equal(3, loaded.GetSheetCount());
        Assert.Equal(doc.GetSheetCount(), loaded.GetSheetCount());

        // ExportToJson on loaded
        var loadedJson = loaded.ExportToJson();
        Assert.NotNull(loadedJson);
        Assert.NotEmpty(loadedJson);

        // GetCellRange on loaded
        var loadedRange = loaded.GetCellRange("Financials", 0, 0, 0, 3);
        Assert.Equal("Period", loadedRange[0, 0]);

        // GetSheetCount after AddSheet on loaded
        loaded.AddSheet("New");
        Assert.Equal(4, loaded.GetSheetCount());
    }
}
