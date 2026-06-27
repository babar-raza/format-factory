// Tests for FodsDocument.GetNamedRangeCount, AddNamedRange, GetNamedRange deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODS-R361

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R361: Tests for FodsDocument.GetNamedRangeCount, AddNamedRange, GetNamedRange deeper.
/// GetNamedRangeCount(): returns the number of named ranges defined in the workbook.
/// AddNamedRange(name, sheetName, range): defines a named range pointing to a sheet region.
/// GetNamedRange(name): returns the reference string for the named range.
/// Covers: GetNamedRangeCount no-throw; GetNamedRangeCount non-negative; GetNamedRangeCount consistent;
/// GetNamedRangeCount zero for new doc; GetNamedRangeCount after AddNamedRange increases;
/// GetNamedRangeCount save-load;
/// AddNamedRange no-throw; AddNamedRange increases count; AddNamedRange save-load;
/// AddNamedRange multiple; AddNamedRange then ExportToCsv no-throw;
/// AddNamedRange then GetCellValue non-null; AddNamedRange then GetSheetCount unchanged;
/// GetNamedRange no-throw; GetNamedRange non-null; GetNamedRange consistent;
/// GetNamedRange save-load;
/// dogfood CreateDoc→AddNamedRange→GetNamedRangeCount→GetNamedRange→SaveToFile pipeline.
/// </summary>
public class FodsR361GetNamedRangeCountAndAddNamedRangeDeepTests : IDisposable
{
    private readonly string _tempDir;

    public FodsR361GetNamedRangeCountAndAddNamedRangeDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodsR361_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private static FodsDocument CreateFinancialDoc()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("P&L");
        doc.SetCellValue("P&L", 0, 0, "Line_Item");
        doc.SetCellValue("P&L", 0, 1, "FY2022");
        doc.SetCellValue("P&L", 0, 2, "FY2023");
        doc.SetCellValue("P&L", 0, 3, "FY2024");
        doc.SetCellValue("P&L", 1, 0, "Revenue");
        doc.SetCellValue("P&L", 1, 1, "4250000");
        doc.SetCellValue("P&L", 1, 2, "4780000");
        doc.SetCellValue("P&L", 1, 3, "5320000");
        doc.SetCellValue("P&L", 2, 0, "COGS");
        doc.SetCellValue("P&L", 2, 1, "1700000");
        doc.SetCellValue("P&L", 2, 2, "1912000");
        doc.SetCellValue("P&L", 2, 3, "2128000");
        doc.SetCellValue("P&L", 3, 0, "Gross_Profit");
        doc.SetCellValue("P&L", 3, 1, "2550000");
        doc.SetCellValue("P&L", 3, 2, "2868000");
        doc.SetCellValue("P&L", 3, 3, "3192000");
        doc.AddSheet("Balance_Sheet");
        doc.SetCellValue("Balance_Sheet", 0, 0, "Asset_Class");
        doc.SetCellValue("Balance_Sheet", 0, 1, "FY2024_GBP");
        doc.SetCellValue("Balance_Sheet", 1, 0, "Fixed_Assets");
        doc.SetCellValue("Balance_Sheet", 1, 1, "8900000");
        doc.SetCellValue("Balance_Sheet", 2, 0, "Current_Assets");
        doc.SetCellValue("Balance_Sheet", 2, 1, "3200000");
        return doc;
    }

    // -------------------------------------------------------------------------
    // GetNamedRangeCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetNamedRangeCount_NoThrow()
    {
        var doc = CreateFinancialDoc();
        var ex = Record.Exception(() => doc.GetNamedRangeCount());
        Assert.Null(ex);
    }

    [Fact]
    public void GetNamedRangeCount_NonNegative()
    {
        var doc = CreateFinancialDoc();
        Assert.True(doc.GetNamedRangeCount() >= 0);
    }

    [Fact]
    public void GetNamedRangeCount_Consistent()
    {
        var doc = CreateFinancialDoc();
        Assert.Equal(doc.GetNamedRangeCount(), doc.GetNamedRangeCount());
    }

    [Fact]
    public void GetNamedRangeCount_Zero_ForNewDoc()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("Sheet1");
        doc.SetCellValue("Sheet1", 0, 0, "Data");
        Assert.Equal(0, doc.GetNamedRangeCount());
    }

    [Fact]
    public void GetNamedRangeCount_AfterAddNamedRange_Increases()
    {
        var doc = CreateFinancialDoc();
        var before = doc.GetNamedRangeCount();
        doc.AddNamedRange("Revenue_History", "P&L", "B2:D2");
        Assert.Equal(before + 1, doc.GetNamedRangeCount());
    }

    [Fact]
    public void GetNamedRangeCount_SaveLoad_Consistent()
    {
        var doc = CreateFinancialDoc();
        doc.AddNamedRange("Gross_Profit_Row", "P&L", "B4:D4");
        var before = doc.GetNamedRangeCount();
        var path = TempFile("nrc_save.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetNamedRangeCount());
    }

    // -------------------------------------------------------------------------
    // AddNamedRange
    // -------------------------------------------------------------------------

    [Fact]
    public void AddNamedRange_NoThrow()
    {
        var doc = CreateFinancialDoc();
        var ex = Record.Exception(() => doc.AddNamedRange("Header_Row", "P&L", "A1:D1"));
        Assert.Null(ex);
    }

    [Fact]
    public void AddNamedRange_Increases_Count()
    {
        var doc = CreateFinancialDoc();
        var before = doc.GetNamedRangeCount();
        doc.AddNamedRange("COGS_Row", "P&L", "B3:D3");
        Assert.Equal(before + 1, doc.GetNamedRangeCount());
    }

    [Fact]
    public void AddNamedRange_SaveLoad_Persists()
    {
        var doc = CreateFinancialDoc();
        doc.AddNamedRange("Total_Assets", "Balance_Sheet", "B2:B3");
        var before = doc.GetNamedRangeCount();
        var path = TempFile("anr_save.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetNamedRangeCount());
    }

    [Fact]
    public void AddNamedRange_Multiple()
    {
        var doc = CreateFinancialDoc();
        doc.AddNamedRange("Range_A", "P&L", "B2:D2");
        doc.AddNamedRange("Range_B", "P&L", "B3:D3");
        doc.AddNamedRange("Range_C", "Balance_Sheet", "B2:B3");
        Assert.Equal(3, doc.GetNamedRangeCount());
    }

    [Fact]
    public void AddNamedRange_Then_ExportToCsv_NoThrow()
    {
        var doc = CreateFinancialDoc();
        doc.AddNamedRange("PL_Data", "P&L", "A1:D4");
        var ex = Record.Exception(() => doc.ExportToCsv("P&L"));
        Assert.Null(ex);
    }

    [Fact]
    public void AddNamedRange_Then_GetCellValue_NonNull()
    {
        var doc = CreateFinancialDoc();
        doc.AddNamedRange("Revenue_Cell", "P&L", "B2:B2");
        Assert.NotNull(doc.GetCellValue("P&L", 1, 1));
    }

    [Fact]
    public void AddNamedRange_Then_GetSheetCount_Unchanged()
    {
        var doc = CreateFinancialDoc();
        var before = doc.GetSheetCount();
        doc.AddNamedRange("Fixed_Assets_Cell", "Balance_Sheet", "B2:B2");
        Assert.Equal(before, doc.GetSheetCount());
    }

    // -------------------------------------------------------------------------
    // GetNamedRange
    // -------------------------------------------------------------------------

    [Fact]
    public void GetNamedRange_NoThrow()
    {
        var doc = CreateFinancialDoc();
        doc.AddNamedRange("Test_Range", "P&L", "A2:D4");
        var ex = Record.Exception(() => doc.GetNamedRange("Test_Range"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetNamedRange_NonNull()
    {
        var doc = CreateFinancialDoc();
        doc.AddNamedRange("NonNull_Range", "P&L", "B1:D1");
        Assert.NotNull(doc.GetNamedRange("NonNull_Range"));
    }

    [Fact]
    public void GetNamedRange_Consistent()
    {
        var doc = CreateFinancialDoc();
        doc.AddNamedRange("Consistent_Range", "Balance_Sheet", "A1:B3");
        Assert.Equal(doc.GetNamedRange("Consistent_Range"), doc.GetNamedRange("Consistent_Range"));
    }

    [Fact]
    public void GetNamedRange_SaveLoad_Consistent()
    {
        var doc = CreateFinancialDoc();
        doc.AddNamedRange("SaveLoad_Range", "P&L", "A1:D4");
        var path = TempFile("gnr_save.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        Assert.NotNull(loaded.GetNamedRange("SaveLoad_Range"));
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_AddNamedRange_GetNamedRangeCount_GetNamedRange_SaveToFile_Pipeline()
    {
        // Investment banking — DCF valuation model with named ranges for formula audit trail
        var doc = FodsDocument.CreateEmpty();

        doc.AddSheet("DCF_Assumptions");
        doc.SetCellValue("DCF_Assumptions", 0, 0, "Parameter");
        doc.SetCellValue("DCF_Assumptions", 0, 1, "Value");
        doc.SetCellValue("DCF_Assumptions", 0, 2, "Unit");
        string[][] assumptions = {
            new[]{"WACC", "9.8", "Pct"},
            new[]{"Terminal_Growth_Rate", "2.5", "Pct"},
            new[]{"Tax_Rate", "25.0", "Pct"},
            new[]{"D_E_Ratio", "0.35", "Ratio"},
            new[]{"Risk_Free_Rate", "4.2", "Pct"},
            new[]{"Equity_Risk_Premium", "5.6", "Pct"},
            new[]{"Beta_Levered", "1.15", "Scalar"},
        };
        for (int i = 0; i < assumptions.Length; i++)
        {
            doc.SetCellValue("DCF_Assumptions", i + 1, 0, assumptions[i][0]);
            doc.SetCellValue("DCF_Assumptions", i + 1, 1, assumptions[i][1]);
            doc.SetCellValue("DCF_Assumptions", i + 1, 2, assumptions[i][2]);
        }

        doc.AddSheet("FCF_Forecast");
        doc.SetCellValue("FCF_Forecast", 0, 0, "Year");
        doc.SetCellValue("FCF_Forecast", 0, 1, "Revenue_GBPm");
        doc.SetCellValue("FCF_Forecast", 0, 2, "EBITDA_GBPm");
        doc.SetCellValue("FCF_Forecast", 0, 3, "EBIT_GBPm");
        doc.SetCellValue("FCF_Forecast", 0, 4, "NOPAT_GBPm");
        doc.SetCellValue("FCF_Forecast", 0, 5, "FCF_GBPm");
        double[] revenues = { 420.0, 462.0, 508.2, 559.0, 614.9 };
        for (int y = 0; y < 5; y++)
        {
            double rev = revenues[y];
            double ebitda = rev * 0.22;
            double ebit = rev * 0.15;
            double nopat = ebit * 0.75;
            double fcf = nopat - rev * 0.04;
            doc.SetCellValue("FCF_Forecast", y + 1, 0, (2024 + y).ToString());
            doc.SetCellValue("FCF_Forecast", y + 1, 1, $"{rev:F1}");
            doc.SetCellValue("FCF_Forecast", y + 1, 2, $"{ebitda:F1}");
            doc.SetCellValue("FCF_Forecast", y + 1, 3, $"{ebit:F1}");
            doc.SetCellValue("FCF_Forecast", y + 1, 4, $"{nopat:F1}");
            doc.SetCellValue("FCF_Forecast", y + 1, 5, $"{fcf:F1}");
        }

        doc.AddSheet("Valuation_Output");
        doc.SetCellValue("Valuation_Output", 0, 0, "Metric");
        doc.SetCellValue("Valuation_Output", 0, 1, "Value_GBPm");
        doc.SetCellValue("Valuation_Output", 1, 0, "Enterprise_Value_Base");
        doc.SetCellValue("Valuation_Output", 1, 1, "2847.3");
        doc.SetCellValue("Valuation_Output", 2, 0, "Net_Debt");
        doc.SetCellValue("Valuation_Output", 2, 1, "412.0");
        doc.SetCellValue("Valuation_Output", 3, 0, "Equity_Value");
        doc.SetCellValue("Valuation_Output", 3, 1, "2435.3");
        doc.SetCellValue("Valuation_Output", 4, 0, "Shares_Outstanding_M");
        doc.SetCellValue("Valuation_Output", 4, 1, "185.0");
        doc.SetCellValue("Valuation_Output", 5, 0, "Implied_Share_Price_GBP");
        doc.SetCellValue("Valuation_Output", 5, 1, "13.16");

        Assert.Equal(3, doc.GetSheetCount());
        Assert.Equal(0, doc.GetNamedRangeCount());

        // AddNamedRange — key model parameters for formula audit
        doc.AddNamedRange("WACC", "DCF_Assumptions", "B2:B2");
        Assert.Equal(1, doc.GetNamedRangeCount());

        doc.AddNamedRange("Terminal_Growth", "DCF_Assumptions", "B3:B3");
        Assert.Equal(2, doc.GetNamedRangeCount());

        doc.AddNamedRange("FCF_Values", "FCF_Forecast", "F2:F6");
        Assert.Equal(3, doc.GetNamedRangeCount());

        doc.AddNamedRange("Revenue_Forecast", "FCF_Forecast", "B2:B6");
        Assert.Equal(4, doc.GetNamedRangeCount());

        doc.AddNamedRange("Enterprise_Value", "Valuation_Output", "B2:B2");
        Assert.Equal(5, doc.GetNamedRangeCount());

        doc.AddNamedRange("Equity_Value", "Valuation_Output", "B4:B4");
        Assert.Equal(6, doc.GetNamedRangeCount());

        // Consistent
        Assert.Equal(doc.GetNamedRangeCount(), doc.GetNamedRangeCount());

        // GetNamedRange
        var waccRef = doc.GetNamedRange("WACC");
        Assert.NotNull(waccRef);
        Assert.Equal(waccRef, doc.GetNamedRange("WACC")); // consistent

        var fcfRef = doc.GetNamedRange("FCF_Values");
        Assert.NotNull(fcfRef);

        var evRef = doc.GetNamedRange("Enterprise_Value");
        Assert.NotNull(evRef);

        // ExportToCsv
        var csv = doc.ExportToCsv("FCF_Forecast");
        Assert.NotNull(csv);
        Assert.NotEmpty(csv);

        // GetCellValue
        Assert.Equal("9.8", doc.GetCellValue("DCF_Assumptions", 1, 1));

        // GetRowCount / GetColumnCount
        Assert.True(doc.GetRowCount("DCF_Assumptions") > 0);
        Assert.True(doc.GetColumnCount("FCF_Forecast") > 0);

        // SaveToFile
        var path = TempFile("dogfood_dcf_valuation.fods");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));
        Assert.True(new FileInfo(path).Length > 0);

        // LoadFile and verify
        var loaded = FodsDocument.LoadFile(path);
        Assert.Equal(6, loaded.GetNamedRangeCount());
        Assert.Equal(3, loaded.GetSheetCount());
        Assert.NotNull(loaded.GetNamedRange("WACC"));
        Assert.NotNull(loaded.GetNamedRange("FCF_Values"));

        // AddNamedRange on loaded
        loaded.AddNamedRange("Implied_Price", "Valuation_Output", "B6:B6");
        Assert.Equal(7, loaded.GetNamedRangeCount());

        // ExportToCsv on loaded
        var loadedCsv = loaded.ExportToCsv("Valuation_Output");
        Assert.NotNull(loadedCsv);
        Assert.NotEmpty(loadedCsv);

        // AddSheet on loaded
        loaded.AddSheet("Sensitivity_Table");
        loaded.SetCellValue("Sensitivity_Table", 0, 0, "WACC_Delta");
        loaded.SetCellValue("Sensitivity_Table", 0, 1, "Growth_Delta");
        loaded.SetCellValue("Sensitivity_Table", 0, 2, "EV_GBPm");
        loaded.AddNamedRange("Sensitivity_Grid", "Sensitivity_Table", "A1:C2");
        Assert.Equal(8, loaded.GetNamedRangeCount());
        Assert.Equal(4, loaded.GetSheetCount());

        // Final save
        var path2 = TempFile("dogfood_dcf_valuation_v2.fods");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var loaded2 = FodsDocument.LoadFile(path2);
        Assert.Equal(8, loaded2.GetNamedRangeCount());
        Assert.Equal(4, loaded2.GetSheetCount());
        Assert.NotNull(loaded2.GetNamedRange("WACC"));
        var ex1 = Record.Exception(() => loaded2.ExportToCsv("FCF_Forecast"));
        var ex2 = Record.Exception(() => loaded2.AddNamedRange("Beta", "DCF_Assumptions", "B8:B8"));
        Assert.Null(ex1);
        Assert.Null(ex2);
    }
}
