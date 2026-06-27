// Tests for FodsDocument.GetAutoFilterState, SetAutoFilter deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODS-R410

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R410: Tests for FodsDocument.GetAutoFilterState, SetAutoFilter deeper.
/// GetAutoFilterState(sheet): returns true if auto-filter is enabled on the sheet, false otherwise.
/// SetAutoFilter(sheet, bool): enables or disables auto-filter on the named sheet.
/// Covers: GetAutoFilterState no-throw; GetAutoFilterState false for new sheet;
/// GetAutoFilterState consistent; SetAutoFilter no-throw;
/// GetAutoFilterState true after SetAutoFilter(true); toggleable;
/// SetAutoFilter save-load consistent; dogfood pipeline.
/// </summary>
public class FodsR410GetAutoFilterStateAndSetAutoFilterDeepTests : IDisposable
{
    private readonly string _tempDir;

    public FodsR410GetAutoFilterStateAndSetAutoFilterDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodsR410_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private static FodsDocument CreateWorkbook()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.SetCellValue("Sheet1", 0, 0, "ID");
        doc.SetCellValue("Sheet1", 0, 1, "Name");
        doc.SetCellValue("Sheet1", 0, 2, "Value");
        for (int i = 1; i <= 10; i++)
        {
            doc.SetCellValue("Sheet1", i, 0, i.ToString());
            doc.SetCellValue("Sheet1", i, 1, $"Item_{i}");
            doc.SetCellValue("Sheet1", i, 2, (i * 100).ToString());
        }
        return doc;
    }

    // -------------------------------------------------------------------------
    // GetAutoFilterState
    // -------------------------------------------------------------------------

    [Fact]
    public void GetAutoFilterState_NoThrow()
    {
        var doc = CreateWorkbook();
        var ex = Record.Exception(() => doc.GetAutoFilterState("Sheet1"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetAutoFilterState_False_ForNewSheet()
    {
        var doc = CreateWorkbook();
        Assert.False(doc.GetAutoFilterState("Sheet1"));
    }

    [Fact]
    public void GetAutoFilterState_Consistent()
    {
        var doc = CreateWorkbook();
        Assert.Equal(doc.GetAutoFilterState("Sheet1"), doc.GetAutoFilterState("Sheet1"));
    }

    // -------------------------------------------------------------------------
    // SetAutoFilter
    // -------------------------------------------------------------------------

    [Fact]
    public void SetAutoFilter_NoThrow()
    {
        var doc = CreateWorkbook();
        var ex = Record.Exception(() => doc.SetAutoFilter("Sheet1", true));
        Assert.Null(ex);
    }

    [Fact]
    public void GetAutoFilterState_True_After_SetAutoFilter_True()
    {
        var doc = CreateWorkbook();
        doc.SetAutoFilter("Sheet1", true);
        Assert.True(doc.GetAutoFilterState("Sheet1"));
    }

    [Fact]
    public void SetAutoFilter_Toggleable()
    {
        var doc = CreateWorkbook();
        doc.SetAutoFilter("Sheet1", true);
        Assert.True(doc.GetAutoFilterState("Sheet1"));
        doc.SetAutoFilter("Sheet1", false);
        Assert.False(doc.GetAutoFilterState("Sheet1"));
        doc.SetAutoFilter("Sheet1", true);
        Assert.True(doc.GetAutoFilterState("Sheet1"));
    }

    [Fact]
    public void SetAutoFilter_SaveLoad_Consistent()
    {
        var doc = CreateWorkbook();
        doc.SetAutoFilter("Sheet1", true);
        var before = doc.GetAutoFilterState("Sheet1");
        var path = TempFile("af_save.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetAutoFilterState("Sheet1"));
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetAutoFilterState_SetAutoFilter_SaveToFile_Pipeline()
    {
        // Finance — UK Office for Budget Responsibility (OBR): Economic and Fiscal Outlook Data
        // Multi-sheet workbook with filterable economic forecasts and scenario analysis
        // Auto-filter enables analysts to slice data by forecast vintage and scenario

        var doc = FodsDocument.CreateEmpty();

        // Sheet 1: GDP Forecast — filterable by scenario and vintage
        doc.SetCellValue("Sheet1", 0, 0, "Vintage");
        doc.SetCellValue("Sheet1", 0, 1, "Scenario");
        doc.SetCellValue("Sheet1", 0, 2, "Year");
        doc.SetCellValue("Sheet1", 0, 3, "GDP_Growth_Pct");
        doc.SetCellValue("Sheet1", 0, 4, "CPI_Pct");
        doc.SetCellValue("Sheet1", 0, 5, "Unemployment_Pct");
        doc.SetCellValue("Sheet1", 0, 6, "PSND_GDP_Pct");

        string[] vintages = { "EFO_Mar24", "EFO_Oct24", "EFO_Mar25" };
        string[] scenarios = { "Central", "Upside", "Downside" };
        double[][] gdpBase = {
            new[] { 0.8, 1.9, 1.8, 1.7, 1.6 }, // EFO Mar24 central
            new[] { 1.1, 2.1, 2.0, 1.9, 1.8 }, // EFO Mar24 upside
            new[] { 0.5, 1.7, 1.6, 1.5, 1.4 }  // EFO Mar24 downside
        };

        int row = 1;
        foreach (var vintage in vintages)
        {
            for (int s = 0; s < scenarios.Length; s++)
            {
                for (int yr = 2024; yr <= 2028; yr++)
                {
                    int yIdx = yr - 2024;
                    double gdp = gdpBase[s][yIdx] + (vintages[System.Array.IndexOf(vintages, vintage)] - 0) * 0.1;
                    double cpi = 3.1 - yIdx * 0.4 + (s == 1 ? -0.3 : s == 2 ? 0.3 : 0);
                    double unemp = 4.2 + yIdx * 0.1 + (s == 2 ? 0.5 : 0);
                    double psnd = 88.5 + yIdx * 1.5 + (s == 2 ? 3.0 : 0);
                    doc.SetCellValue("Sheet1", row, 0, vintage);
                    doc.SetCellValue("Sheet1", row, 1, scenarios[s]);
                    doc.SetCellValue("Sheet1", row, 2, yr.ToString());
                    doc.SetCellValue("Sheet1", row, 3, gdp.ToString("F1"));
                    doc.SetCellValue("Sheet1", row, 4, cpi.ToString("F1"));
                    doc.SetCellValue("Sheet1", row, 5, unemp.ToString("F1"));
                    doc.SetCellValue("Sheet1", row, 6, psnd.ToString("F1"));
                    row++;
                }
            }
        }

        // Sheet 2: Fiscal Metrics — filterable by department
        doc.AddSheet("Fiscal_DEL");
        doc.SetCellValue("Fiscal_DEL", 0, 0, "Department");
        doc.SetCellValue("Fiscal_DEL", 0, 1, "DEL_Baseline_Gbp_Bn");
        doc.SetCellValue("Fiscal_DEL", 0, 2, "DEL_Forecast_Gbp_Bn");
        doc.SetCellValue("Fiscal_DEL", 0, 3, "Variance_Gbp_Bn");
        doc.SetCellValue("Fiscal_DEL", 0, 4, "RAG");

        string[][] depts = {
            new[] { "DHSC", "193.4", "198.1", "+4.7", "AMBER" },
            new[] { "DfE", "102.1", "103.8", "+1.7", "GREEN" },
            new[] { "MoD", "55.2", "57.9", "+2.7", "AMBER" },
            new[] { "DWP", "138.6", "142.3", "+3.7", "AMBER" },
            new[] { "HO", "21.4", "21.9", "+0.5", "GREEN" },
            new[] { "MoJ", "14.8", "15.6", "+0.8", "AMBER" },
            new[] { "DCMS", "8.9", "8.7", "-0.2", "GREEN" },
            new[] { "BEIS", "34.2", "38.1", "+3.9", "RED" },
            new[] { "DfT", "29.8", "30.2", "+0.4", "GREEN" },
            new[] { "FCO", "12.1", "12.4", "+0.3", "GREEN" }
        };

        for (int i = 0; i < depts.Length; i++)
        {
            for (int col = 0; col < depts[i].Length; col++)
                doc.SetCellValue("Fiscal_DEL", i + 1, col, depts[i][col]);
        }

        // Initial state: no auto-filter on any sheet
        Assert.False(doc.GetAutoFilterState("Sheet1"));
        Assert.False(doc.GetAutoFilterState("Fiscal_DEL"));

        // Enable auto-filter on GDP forecast sheet
        doc.SetAutoFilter("Sheet1", true);
        Assert.True(doc.GetAutoFilterState("Sheet1"));
        Assert.False(doc.GetAutoFilterState("Fiscal_DEL")); // not set yet

        // Enable auto-filter on fiscal sheet
        doc.SetAutoFilter("Fiscal_DEL", true);
        Assert.True(doc.GetAutoFilterState("Fiscal_DEL"));

        // Consistent reads
        Assert.Equal(true, doc.GetAutoFilterState("Sheet1"));
        Assert.Equal(true, doc.GetAutoFilterState("Fiscal_DEL"));

        // Disable and re-enable GDP filter
        doc.SetAutoFilter("Sheet1", false);
        Assert.False(doc.GetAutoFilterState("Sheet1"));
        doc.SetAutoFilter("Sheet1", true);
        Assert.True(doc.GetAutoFilterState("Sheet1"));

        // Basic assertions
        Assert.True(doc.GetSheetCount() >= 2);
        Assert.True(doc.GetRowCount("Sheet1") > 0);
        Assert.True(doc.GetRowCount("Fiscal_DEL") > 0);

        // SaveToFile
        var path1 = TempFile("dogfood_obr_efo_data.fods");
        doc.SaveToFile(path1);
        Assert.True(File.Exists(path1));
        Assert.True(new FileInfo(path1).Length > 0);

        // LoadFile and verify auto-filter state persisted
        var loaded = FodsDocument.LoadFile(path1);
        Assert.True(loaded.GetAutoFilterState("Sheet1"));
        Assert.True(loaded.GetAutoFilterState("Fiscal_DEL"));
        Assert.Equal(doc.GetAutoFilterState("Sheet1"), loaded.GetAutoFilterState("Sheet1"));

        // Add supplementary scenarios sheet
        loaded.AddSheet("Scenarios_Narrative");
        loaded.SetCellValue("Scenarios_Narrative", 0, 0, "Scenario");
        loaded.SetCellValue("Scenarios_Narrative", 0, 1, "Description");
        loaded.SetCellValue("Scenarios_Narrative", 1, 0, "Central");
        loaded.SetCellValue("Scenarios_Narrative", 1, 1, "OBR baseline incorporating government policy announcements to March 2025.");
        loaded.SetCellValue("Scenarios_Narrative", 2, 0, "Upside");
        loaded.SetCellValue("Scenarios_Narrative", 2, 1, "Faster productivity growth; lower energy prices; stronger global demand.");
        loaded.SetCellValue("Scenarios_Narrative", 3, 0, "Downside");
        loaded.SetCellValue("Scenarios_Narrative", 3, 1, "Persistent inflation; weaker global demand; higher interest rates.");

        // This new sheet should have no auto-filter initially
        Assert.False(loaded.GetAutoFilterState("Scenarios_Narrative"));

        // Enable filter on new sheet
        loaded.SetAutoFilter("Scenarios_Narrative", true);
        Assert.True(loaded.GetAutoFilterState("Scenarios_Narrative"));

        // Final save
        var path2 = TempFile("dogfood_obr_efo_data_final.fods");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var final = FodsDocument.LoadFile(path2);
        Assert.True(final.GetAutoFilterState("Sheet1"));
        Assert.True(final.GetAutoFilterState("Fiscal_DEL"));
        Assert.True(final.GetAutoFilterState("Scenarios_Narrative"));

        var ex1 = Record.Exception(() => final.GetAutoFilterState("Sheet1"));
        var ex2 = Record.Exception(() => final.SetAutoFilter("Sheet1", false));
        Assert.Null(ex1);
        Assert.Null(ex2);
        Assert.False(final.GetAutoFilterState("Sheet1")); // just toggled off
    }
}
