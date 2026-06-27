// Tests for FodsDocument.GetFreezeRowCount, SetFreezePanes, GetFreezeColumnCount deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODS-R364

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R364: Tests for FodsDocument.GetFreezeRowCount, SetFreezePanes, GetFreezeColumnCount deeper.
/// GetFreezeRowCount(sheetName): returns number of frozen rows for the named sheet.
/// SetFreezePanes(sheetName, rows, columns): sets the freeze panes for the named sheet.
/// GetFreezeColumnCount(sheetName): returns number of frozen columns for the named sheet.
/// Covers: GetFreezeRowCount no-throw; GetFreezeRowCount non-negative; GetFreezeRowCount consistent;
/// GetFreezeRowCount zero for new sheet; GetFreezeRowCount after SetFreezePanes;
/// GetFreezeRowCount save-load;
/// SetFreezePanes no-throw; SetFreezePanes sets row freeze; SetFreezePanes sets column freeze;
/// SetFreezePanes save-load; SetFreezePanes multiple sheets; SetFreezePanes then ExportToCsv no-throw;
/// SetFreezePanes then GetCellValue non-null; SetFreezePanes then GetSheetCount unchanged;
/// GetFreezeColumnCount no-throw; GetFreezeColumnCount non-negative; GetFreezeColumnCount save-load;
/// dogfood CreateDoc→SetFreezePanes→GetFreezeRowCount→GetFreezeColumnCount→SaveToFile pipeline.
/// </summary>
public class FodsR364GetFreezeRowCountAndSetFreezePanesDeepTests : IDisposable
{
    private readonly string _tempDir;

    public FodsR364GetFreezeRowCountAndSetFreezePanesDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodsR364_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private static FodsDocument CreateDataDoc()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("Sales_Data");
        doc.SetCellValue("Sales_Data", 0, 0, "Product_ID");
        doc.SetCellValue("Sales_Data", 0, 1, "Product_Name");
        doc.SetCellValue("Sales_Data", 0, 2, "Region");
        doc.SetCellValue("Sales_Data", 0, 3, "Q1_Revenue");
        doc.SetCellValue("Sales_Data", 0, 4, "Q2_Revenue");
        for (int r = 1; r <= 10; r++)
        {
            doc.SetCellValue("Sales_Data", r, 0, $"PRD{r:D3}");
            doc.SetCellValue("Sales_Data", r, 1, $"Product_{r}");
            doc.SetCellValue("Sales_Data", r, 2, r % 3 == 0 ? "North" : r % 3 == 1 ? "South" : "East");
            doc.SetCellValue("Sales_Data", r, 3, (r * 12500).ToString());
            doc.SetCellValue("Sales_Data", r, 4, (r * 13800).ToString());
        }
        doc.AddSheet("Lookup_Table");
        doc.SetCellValue("Lookup_Table", 0, 0, "Code");
        doc.SetCellValue("Lookup_Table", 0, 1, "Description");
        doc.SetCellValue("Lookup_Table", 0, 2, "Category");
        for (int r = 1; r <= 5; r++)
        {
            doc.SetCellValue("Lookup_Table", r, 0, $"C{r:D2}");
            doc.SetCellValue("Lookup_Table", r, 1, $"Category_{r}");
            doc.SetCellValue("Lookup_Table", r, 2, $"Type_{r % 3 + 1}");
        }
        return doc;
    }

    // -------------------------------------------------------------------------
    // GetFreezeRowCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetFreezeRowCount_NoThrow()
    {
        var doc = CreateDataDoc();
        var ex = Record.Exception(() => doc.GetFreezeRowCount("Sales_Data"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetFreezeRowCount_NonNegative()
    {
        var doc = CreateDataDoc();
        Assert.True(doc.GetFreezeRowCount("Sales_Data") >= 0);
    }

    [Fact]
    public void GetFreezeRowCount_Consistent()
    {
        var doc = CreateDataDoc();
        Assert.Equal(doc.GetFreezeRowCount("Sales_Data"), doc.GetFreezeRowCount("Sales_Data"));
    }

    [Fact]
    public void GetFreezeRowCount_Zero_ForNewSheet()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("Clean_Sheet");
        doc.SetCellValue("Clean_Sheet", 0, 0, "Header");
        Assert.Equal(0, doc.GetFreezeRowCount("Clean_Sheet"));
    }

    [Fact]
    public void GetFreezeRowCount_AfterSetFreezePanes_Matches()
    {
        var doc = CreateDataDoc();
        doc.SetFreezePanes("Sales_Data", 1, 0);
        Assert.Equal(1, doc.GetFreezeRowCount("Sales_Data"));
    }

    [Fact]
    public void GetFreezeRowCount_SaveLoad_Consistent()
    {
        var doc = CreateDataDoc();
        doc.SetFreezePanes("Sales_Data", 1, 0);
        var path = TempFile("frc_save.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        Assert.Equal(1, loaded.GetFreezeRowCount("Sales_Data"));
    }

    // -------------------------------------------------------------------------
    // SetFreezePanes
    // -------------------------------------------------------------------------

    [Fact]
    public void SetFreezePanes_NoThrow()
    {
        var doc = CreateDataDoc();
        var ex = Record.Exception(() => doc.SetFreezePanes("Sales_Data", 1, 0));
        Assert.Null(ex);
    }

    [Fact]
    public void SetFreezePanes_Sets_Row_Freeze()
    {
        var doc = CreateDataDoc();
        doc.SetFreezePanes("Sales_Data", 1, 0);
        Assert.Equal(1, doc.GetFreezeRowCount("Sales_Data"));
    }

    [Fact]
    public void SetFreezePanes_Sets_Column_Freeze()
    {
        var doc = CreateDataDoc();
        doc.SetFreezePanes("Sales_Data", 0, 2);
        Assert.Equal(2, doc.GetFreezeColumnCount("Sales_Data"));
    }

    [Fact]
    public void SetFreezePanes_SaveLoad_Persists()
    {
        var doc = CreateDataDoc();
        doc.SetFreezePanes("Sales_Data", 1, 1);
        var path = TempFile("sfp_save.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        Assert.Equal(1, loaded.GetFreezeRowCount("Sales_Data"));
        Assert.Equal(1, loaded.GetFreezeColumnCount("Sales_Data"));
    }

    [Fact]
    public void SetFreezePanes_MultipleSheets()
    {
        var doc = CreateDataDoc();
        doc.SetFreezePanes("Sales_Data", 1, 0);
        doc.SetFreezePanes("Lookup_Table", 1, 0);
        Assert.Equal(1, doc.GetFreezeRowCount("Sales_Data"));
        Assert.Equal(1, doc.GetFreezeRowCount("Lookup_Table"));
    }

    [Fact]
    public void SetFreezePanes_Then_ExportToCsv_NoThrow()
    {
        var doc = CreateDataDoc();
        doc.SetFreezePanes("Sales_Data", 1, 0);
        var ex = Record.Exception(() => doc.ExportToCsv("Sales_Data"));
        Assert.Null(ex);
    }

    [Fact]
    public void SetFreezePanes_Then_GetCellValue_NonNull()
    {
        var doc = CreateDataDoc();
        doc.SetFreezePanes("Sales_Data", 1, 1);
        Assert.NotNull(doc.GetCellValue("Sales_Data", 0, 0));
    }

    [Fact]
    public void SetFreezePanes_Then_GetSheetCount_Unchanged()
    {
        var doc = CreateDataDoc();
        var before = doc.GetSheetCount();
        doc.SetFreezePanes("Sales_Data", 1, 0);
        Assert.Equal(before, doc.GetSheetCount());
    }

    // -------------------------------------------------------------------------
    // GetFreezeColumnCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetFreezeColumnCount_NoThrow()
    {
        var doc = CreateDataDoc();
        var ex = Record.Exception(() => doc.GetFreezeColumnCount("Sales_Data"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetFreezeColumnCount_NonNegative()
    {
        var doc = CreateDataDoc();
        Assert.True(doc.GetFreezeColumnCount("Sales_Data") >= 0);
    }

    [Fact]
    public void GetFreezeColumnCount_SaveLoad_Consistent()
    {
        var doc = CreateDataDoc();
        doc.SetFreezePanes("Sales_Data", 0, 2);
        var path = TempFile("fcc_save.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        Assert.Equal(2, loaded.GetFreezeColumnCount("Sales_Data"));
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_SetFreezePanes_GetFreezeRowCount_GetFreezeColumnCount_Pipeline()
    {
        // Environmental monitoring — SEPA Scottish water quality monitoring station data
        var doc = FodsDocument.CreateEmpty();

        doc.AddSheet("Station_Register");
        doc.SetCellValue("Station_Register", 0, 0, "Station_ID");
        doc.SetCellValue("Station_Register", 0, 1, "Station_Name");
        doc.SetCellValue("Station_Register", 0, 2, "River_Name");
        doc.SetCellValue("Station_Register", 0, 3, "NGR_Easting");
        doc.SetCellValue("Station_Register", 0, 4, "NGR_Northing");
        doc.SetCellValue("Station_Register", 0, 5, "Catchment_Area_km2");
        doc.SetCellValue("Station_Register", 0, 6, "SEPA_Region");
        string[] rivers = { "River_Tay", "River_Forth", "River_Clyde", "River_Dee", "River_Don", "River_Spey" };
        for (int i = 1; i <= 12; i++)
        {
            doc.SetCellValue("Station_Register", i, 0, $"GS{i:D5}");
            doc.SetCellValue("Station_Register", i, 1, $"Station_{i}");
            doc.SetCellValue("Station_Register", i, 2, rivers[i % rivers.Length]);
            doc.SetCellValue("Station_Register", i, 3, (270000 + i * 5000).ToString());
            doc.SetCellValue("Station_Register", i, 4, (700000 + i * 3000).ToString());
            doc.SetCellValue("Station_Register", i, 5, (50 + i * 12.5).ToString("F1"));
            doc.SetCellValue("Station_Register", i, 6, i < 7 ? "North" : "South");
        }

        doc.AddSheet("WQ_Data");
        doc.SetCellValue("WQ_Data", 0, 0, "Date");
        doc.SetCellValue("WQ_Data", 0, 1, "Station_ID");
        doc.SetCellValue("WQ_Data", 0, 2, "DO_mg_l");
        doc.SetCellValue("WQ_Data", 0, 3, "BOD_mg_l");
        doc.SetCellValue("WQ_Data", 0, 4, "Ammonia_mg_l");
        doc.SetCellValue("WQ_Data", 0, 5, "Nitrate_mg_l");
        doc.SetCellValue("WQ_Data", 0, 6, "pH");
        doc.SetCellValue("WQ_Data", 0, 7, "Temperature_C");
        doc.SetCellValue("WQ_Data", 0, 8, "WFD_Status");
        for (int i = 1; i <= 10; i++)
        {
            doc.SetCellValue("WQ_Data", i, 0, $"2024-{i:D2}-01");
            doc.SetCellValue("WQ_Data", i, 1, $"GS{(i % 12 + 1):D5}");
            doc.SetCellValue("WQ_Data", i, 2, $"{(8.5 + i * 0.1):F2}");
            doc.SetCellValue("WQ_Data", i, 3, $"{(1.5 + i * 0.05):F2}");
            doc.SetCellValue("WQ_Data", i, 4, $"{(0.02 + i * 0.01):F3}");
            doc.SetCellValue("WQ_Data", i, 5, $"{(2.1 + i * 0.3):F2}");
            doc.SetCellValue("WQ_Data", i, 6, $"{(7.2 + (i % 5) * 0.1):F1}");
            doc.SetCellValue("WQ_Data", i, 7, $"{(8 + i * 0.5):F1}");
            doc.SetCellValue("WQ_Data", i, 8, i < 4 ? "Good" : i < 7 ? "Moderate" : "Poor");
        }

        doc.AddSheet("Annual_Summary");
        doc.SetCellValue("Annual_Summary", 0, 0, "Parameter");
        doc.SetCellValue("Annual_Summary", 0, 1, "2022_Mean");
        doc.SetCellValue("Annual_Summary", 0, 2, "2023_Mean");
        doc.SetCellValue("Annual_Summary", 0, 3, "2024_Mean");
        doc.SetCellValue("Annual_Summary", 0, 4, "Trend");

        Assert.Equal(3, doc.GetSheetCount());

        // SetFreezePanes — header rows and ID columns
        doc.SetFreezePanes("Station_Register", 1, 1); // freeze header row + station ID column
        Assert.Equal(1, doc.GetFreezeRowCount("Station_Register"));
        Assert.Equal(1, doc.GetFreezeColumnCount("Station_Register"));

        doc.SetFreezePanes("WQ_Data", 1, 2); // freeze header row + date + station ID
        Assert.Equal(1, doc.GetFreezeRowCount("WQ_Data"));
        Assert.Equal(2, doc.GetFreezeColumnCount("WQ_Data"));

        doc.SetFreezePanes("Annual_Summary", 1, 1);
        Assert.Equal(1, doc.GetFreezeRowCount("Annual_Summary"));
        Assert.Equal(1, doc.GetFreezeColumnCount("Annual_Summary"));

        // Consistent
        Assert.Equal(doc.GetFreezeRowCount("Station_Register"), doc.GetFreezeRowCount("Station_Register"));
        Assert.Equal(doc.GetFreezeColumnCount("WQ_Data"), doc.GetFreezeColumnCount("WQ_Data"));

        // ExportToCsv
        var csv = doc.ExportToCsv("WQ_Data");
        Assert.NotNull(csv);
        Assert.NotEmpty(csv);

        // GetCellValue
        Assert.Equal("Station_ID", doc.GetCellValue("Station_Register", 0, 0));

        // GetRowCount / GetColumnCount
        Assert.True(doc.GetRowCount("Station_Register") > 0);
        Assert.True(doc.GetColumnCount("WQ_Data") > 0);

        // SaveToFile
        var path = TempFile("dogfood_sepa_wq_monitoring.fods");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));
        Assert.True(new FileInfo(path).Length > 0);

        // LoadFile and verify
        var loaded = FodsDocument.LoadFile(path);
        Assert.Equal(3, loaded.GetSheetCount());
        Assert.Equal(1, loaded.GetFreezeRowCount("Station_Register"));
        Assert.Equal(1, loaded.GetFreezeColumnCount("Station_Register"));
        Assert.Equal(1, loaded.GetFreezeRowCount("WQ_Data"));
        Assert.Equal(2, loaded.GetFreezeColumnCount("WQ_Data"));

        // Modify freeze panes on loaded
        loaded.SetFreezePanes("Station_Register", 1, 2);
        Assert.Equal(2, loaded.GetFreezeColumnCount("Station_Register"));

        // ExportToCsv on loaded
        var loadedCsv = loaded.ExportToCsv("Annual_Summary");
        Assert.NotNull(loadedCsv);

        // AddSheet on loaded
        loaded.AddSheet("Exceedance_Log");
        loaded.SetCellValue("Exceedance_Log", 0, 0, "Date");
        loaded.SetCellValue("Exceedance_Log", 0, 1, "Station_ID");
        loaded.SetCellValue("Exceedance_Log", 0, 2, "Parameter");
        loaded.SetCellValue("Exceedance_Log", 0, 3, "Measured_Value");
        loaded.SetCellValue("Exceedance_Log", 0, 4, "EQS_Standard");
        loaded.SetFreezePanes("Exceedance_Log", 1, 2);
        Assert.Equal(4, loaded.GetSheetCount());
        Assert.Equal(1, loaded.GetFreezeRowCount("Exceedance_Log"));
        Assert.Equal(2, loaded.GetFreezeColumnCount("Exceedance_Log"));

        // Final save
        var path2 = TempFile("dogfood_sepa_wq_monitoring_v2.fods");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var loaded2 = FodsDocument.LoadFile(path2);
        Assert.Equal(4, loaded2.GetSheetCount());
        Assert.Equal(1, loaded2.GetFreezeRowCount("WQ_Data"));
        Assert.Equal(2, loaded2.GetFreezeColumnCount("WQ_Data"));
        var ex1 = Record.Exception(() => loaded2.ExportToCsv("WQ_Data"));
        var ex2 = Record.Exception(() => loaded2.SetFreezePanes("Annual_Summary", 2, 1));
        Assert.Null(ex1);
        Assert.Null(ex2);
    }
}
