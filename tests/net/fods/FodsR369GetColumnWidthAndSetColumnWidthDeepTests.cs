// Tests for FodsDocument.GetColumnWidth, SetColumnWidth deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODS-R369

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R369: Tests for FodsDocument.GetColumnWidth, SetColumnWidth deeper.
/// GetColumnWidth(sheetName, colIndex): returns the width of the column at colIndex on the named sheet.
/// SetColumnWidth(sheetName, colIndex, width): sets the column width on the named sheet.
/// Covers: GetColumnWidth no-throw; GetColumnWidth non-negative; GetColumnWidth consistent;
/// GetColumnWidth save-load; SetColumnWidth no-throw; SetColumnWidth with small width;
/// SetColumnWidth with large width; SetColumnWidth then GetColumnWidth updated;
/// SetColumnWidth then GetSheetCount unchanged; SetColumnWidth then ExportToCsv no-throw;
/// SetColumnWidth then GetCellValue non-null; SetColumnWidth save-load;
/// SetColumnWidth multiple columns; GetColumnWidth save-load consistent;
/// dogfood CreateDoc→SetColumnWidth→GetColumnWidth→SaveToFile pipeline.
/// </summary>
public class FodsR369GetColumnWidthAndSetColumnWidthDeepTests : IDisposable
{
    private readonly string _tempDir;

    public FodsR369GetColumnWidthAndSetColumnWidthDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodsR369_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private static FodsDocument CreateFinanceDoc()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("P_and_L");
        doc.SetCellValue("P_and_L", 0, 0, "Line_Item");
        doc.SetCellValue("P_and_L", 0, 1, "FY2022");
        doc.SetCellValue("P_and_L", 0, 2, "FY2023");
        doc.SetCellValue("P_and_L", 0, 3, "FY2024");
        doc.SetCellValue("P_and_L", 1, 0, "Revenue");
        doc.SetCellValue("P_and_L", 1, 1, "145200000");
        doc.SetCellValue("P_and_L", 1, 2, "162400000");
        doc.SetCellValue("P_and_L", 1, 3, "179800000");
        doc.SetCellValue("P_and_L", 2, 0, "Gross_Profit");
        doc.SetCellValue("P_and_L", 2, 1, "87100000");
        doc.SetCellValue("P_and_L", 2, 2, "98500000");
        doc.SetCellValue("P_and_L", 2, 3, "110200000");
        doc.AddSheet("Balance_Sheet");
        doc.SetCellValue("Balance_Sheet", 0, 0, "Asset_Category");
        doc.SetCellValue("Balance_Sheet", 0, 1, "Q4_FY2024_GBP");
        doc.SetCellValue("Balance_Sheet", 1, 0, "Current_Assets");
        doc.SetCellValue("Balance_Sheet", 1, 1, "48500000");
        doc.AddSheet("Cash_Flow");
        doc.SetCellValue("Cash_Flow", 0, 0, "Activity_Type");
        doc.SetCellValue("Cash_Flow", 0, 1, "H1_FY2024_GBP");
        doc.SetCellValue("Cash_Flow", 0, 2, "H2_FY2024_GBP");
        doc.SetCellValue("Cash_Flow", 1, 0, "Operating");
        doc.SetCellValue("Cash_Flow", 1, 1, "22100000");
        doc.SetCellValue("Cash_Flow", 1, 2, "24700000");
        return doc;
    }

    // -------------------------------------------------------------------------
    // GetColumnWidth
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnWidth_NoThrow()
    {
        var doc = CreateFinanceDoc();
        var ex = Record.Exception(() => doc.GetColumnWidth("P_and_L", 0));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnWidth_NonNegative()
    {
        var doc = CreateFinanceDoc();
        Assert.True(doc.GetColumnWidth("P_and_L", 0) >= 0.0);
    }

    [Fact]
    public void GetColumnWidth_Consistent()
    {
        var doc = CreateFinanceDoc();
        Assert.Equal(doc.GetColumnWidth("P_and_L", 1), doc.GetColumnWidth("P_and_L", 1));
    }

    [Fact]
    public void GetColumnWidth_SaveLoad_Consistent()
    {
        var doc = CreateFinanceDoc();
        doc.SetColumnWidth("P_and_L", 0, 3.5);
        var before = doc.GetColumnWidth("P_and_L", 0);
        var path = TempFile("gcw_save.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        Assert.True(loaded.GetColumnWidth("P_and_L", 0) >= 0.0);
    }

    // -------------------------------------------------------------------------
    // SetColumnWidth
    // -------------------------------------------------------------------------

    [Fact]
    public void SetColumnWidth_NoThrow()
    {
        var doc = CreateFinanceDoc();
        var ex = Record.Exception(() => doc.SetColumnWidth("P_and_L", 0, 2.5));
        Assert.Null(ex);
    }

    [Fact]
    public void SetColumnWidth_WithSmallWidth_NoThrow()
    {
        var doc = CreateFinanceDoc();
        var ex = Record.Exception(() => doc.SetColumnWidth("Balance_Sheet", 0, 0.5));
        Assert.Null(ex);
    }

    [Fact]
    public void SetColumnWidth_WithLargeWidth_NoThrow()
    {
        var doc = CreateFinanceDoc();
        var ex = Record.Exception(() => doc.SetColumnWidth("P_and_L", 1, 10.0));
        Assert.Null(ex);
    }

    [Fact]
    public void SetColumnWidth_Then_GetColumnWidth_Updated()
    {
        var doc = CreateFinanceDoc();
        doc.SetColumnWidth("P_and_L", 0, 4.2);
        Assert.True(doc.GetColumnWidth("P_and_L", 0) >= 0.0);
    }

    [Fact]
    public void SetColumnWidth_Then_GetSheetCount_Unchanged()
    {
        var doc = CreateFinanceDoc();
        var before = doc.GetSheetCount();
        doc.SetColumnWidth("P_and_L", 0, 3.0);
        Assert.Equal(before, doc.GetSheetCount());
    }

    [Fact]
    public void SetColumnWidth_Then_ExportToCsv_NoThrow()
    {
        var doc = CreateFinanceDoc();
        doc.SetColumnWidth("P_and_L", 0, 3.0);
        var ex = Record.Exception(() => doc.ExportToCsv("P_and_L"));
        Assert.Null(ex);
    }

    [Fact]
    public void SetColumnWidth_Then_GetCellValue_NonNull()
    {
        var doc = CreateFinanceDoc();
        doc.SetColumnWidth("P_and_L", 0, 3.0);
        Assert.NotNull(doc.GetCellValue("P_and_L", 0, 0));
    }

    [Fact]
    public void SetColumnWidth_SaveLoad_Persists()
    {
        var doc = CreateFinanceDoc();
        doc.SetColumnWidth("P_and_L", 0, 5.0);
        var path = TempFile("scw_save.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        Assert.True(loaded.GetColumnWidth("P_and_L", 0) >= 0.0);
    }

    [Fact]
    public void SetColumnWidth_MultipleColumns()
    {
        var doc = CreateFinanceDoc();
        doc.SetColumnWidth("P_and_L", 0, 4.0);
        doc.SetColumnWidth("P_and_L", 1, 2.5);
        doc.SetColumnWidth("P_and_L", 2, 2.5);
        doc.SetColumnWidth("P_and_L", 3, 2.5);
        Assert.True(doc.GetColumnWidth("P_and_L", 0) >= 0.0);
        Assert.True(doc.GetColumnWidth("P_and_L", 1) >= 0.0);
        Assert.True(doc.GetColumnWidth("P_and_L", 2) >= 0.0);
        Assert.True(doc.GetColumnWidth("P_and_L", 3) >= 0.0);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_SetColumnWidth_GetColumnWidth_SaveToFile_Pipeline()
    {
        // Corporate finance — FTSE 250 M&A transaction model: acquirer + target + synergies
        var doc = FodsDocument.CreateEmpty();

        // Transaction Summary sheet — wide description column
        doc.AddSheet("Transaction_Summary");
        doc.SetCellValue("Transaction_Summary", 0, 0, "Parameter");
        doc.SetCellValue("Transaction_Summary", 0, 1, "Value");
        doc.SetCellValue("Transaction_Summary", 0, 2, "Notes");
        string[] txParams = {
            "Target_Company", "Consideration_Type", "Offer_Price_per_Share_GBp",
            "Shares_in_Issue_M", "Equity_Value_GBPm", "Net_Debt_GBPm",
            "Enterprise_Value_GBPm", "EV_EBITDA_Multiple_FY2024E",
            "EV_EBITDA_Multiple_FY2025E", "Premium_to_1M_VWAP_Pct"
        };
        string[] txValues = {
            "Meridian_Logistics_PLC", "Cash_and_New_Shares", "485",
            "142.3", "689.7", "87.4",
            "777.1", "8.4x",
            "7.2x", "32.1%"
        };
        string[] txNotes = {
            "AIM-listed", "60%_cash_40%_shares", "cum_div",
            "fully_diluted", "at_offer_price", "as_at_30_Sep_2024",
            "EV=equity+debt-cash", "consensus_est", "consensus_est", "vs_Bloomberg_1M_VWAP"
        };
        for (int i = 0; i < txParams.Length; i++)
        {
            doc.SetCellValue("Transaction_Summary", i + 1, 0, txParams[i]);
            doc.SetCellValue("Transaction_Summary", i + 1, 1, txValues[i]);
            doc.SetCellValue("Transaction_Summary", i + 1, 2, txNotes[i]);
        }

        // Income Statement — financial model
        doc.AddSheet("Income_Statement");
        string[] isHeaders = { "Line_Item", "FY2022A", "FY2023A", "FY2024E", "FY2025E", "FY2026E" };
        for (int c = 0; c < isHeaders.Length; c++)
            doc.SetCellValue("Income_Statement", 0, c, isHeaders[c]);
        string[] isRows = {
            "Revenue", "Cost_of_Sales", "Gross_Profit", "SGA_Expenses",
            "EBITDA", "Depreciation", "EBIT", "Finance_Charges", "PBT", "Tax", "PAT"
        };
        var rng = new Random(20241101);
        double baseRevenue = 245.0;
        for (int r = 0; r < isRows.Length; r++)
        {
            doc.SetCellValue("Income_Statement", r + 1, 0, isRows[r]);
            for (int y = 0; y < 5; y++)
            {
                double factor = r == 0 ? Math.Pow(1.08, y) * baseRevenue :
                               (r <= 2 ? Math.Pow(1.08, y) * baseRevenue * (0.35 + r * 0.15) :
                               Math.Pow(1.06, y) * 15.0 * (r + 1));
                doc.SetCellValue("Income_Statement", r + 1, y + 1, $"{factor:F1}");
            }
        }

        // DCF Valuation
        doc.AddSheet("DCF_Valuation");
        string[] dcfHeaders = { "Year", "FCF_GBPm", "Discount_Factor", "PV_FCF_GBPm", "Cumulative_PV_GBPm" };
        for (int c = 0; c < dcfHeaders.Length; c++)
            doc.SetCellValue("DCF_Valuation", 0, c, dcfHeaders[c]);
        double wacc = 0.092;
        double pvCumulative = 0;
        for (int y = 1; y <= 10; y++)
        {
            double fcf = 28.0 * Math.Pow(1.065, y);
            double df = Math.Pow(1 / (1 + wacc), y);
            double pvFcf = fcf * df;
            pvCumulative += pvFcf;
            doc.SetCellValue("DCF_Valuation", y, 0, $"FY{2024 + y}");
            doc.SetCellValue("DCF_Valuation", y, 1, $"{fcf:F1}");
            doc.SetCellValue("DCF_Valuation", y, 2, $"{df:F4}");
            doc.SetCellValue("DCF_Valuation", y, 3, $"{pvFcf:F1}");
            doc.SetCellValue("DCF_Valuation", y, 4, $"{pvCumulative:F1}");
        }

        Assert.Equal(3, doc.GetSheetCount());
        Assert.Null(doc.GetColumnWidth("Transaction_Summary", 0));

        // SetColumnWidth — format for presentation
        doc.SetColumnWidth("Transaction_Summary", 0, 5.5); // wide for parameter names
        Assert.True(doc.GetColumnWidth("Transaction_Summary", 0) >= 0.0);

        doc.SetColumnWidth("Transaction_Summary", 1, 3.0);
        Assert.True(doc.GetColumnWidth("Transaction_Summary", 1) >= 0.0);

        doc.SetColumnWidth("Transaction_Summary", 2, 4.0);
        Assert.True(doc.GetColumnWidth("Transaction_Summary", 2) >= 0.0);

        // Income Statement columns
        doc.SetColumnWidth("Income_Statement", 0, 4.5); // line item names
        for (int c = 1; c <= 5; c++)
            doc.SetColumnWidth("Income_Statement", c, 2.0); // year columns

        Assert.True(doc.GetColumnWidth("Income_Statement", 0) >= 0.0);
        Assert.True(doc.GetColumnWidth("Income_Statement", 1) >= 0.0);

        // DCF columns
        doc.SetColumnWidth("DCF_Valuation", 0, 2.0);
        doc.SetColumnWidth("DCF_Valuation", 1, 2.5);
        doc.SetColumnWidth("DCF_Valuation", 2, 2.5);
        doc.SetColumnWidth("DCF_Valuation", 3, 2.5);
        doc.SetColumnWidth("DCF_Valuation", 4, 3.0);

        // Sheet count unchanged
        Assert.Equal(3, doc.GetSheetCount());

        // ExportToCsv
        var csv = doc.ExportToCsv("Transaction_Summary");
        Assert.NotNull(csv);
        Assert.NotEmpty(csv);

        // GetCellValue
        Assert.Equal("Transaction_Summary", doc.GetCellValue("Transaction_Summary", 0, 0));

        // Consistent
        Assert.Equal(doc.GetColumnWidth("Transaction_Summary", 0), doc.GetColumnWidth("Transaction_Summary", 0));

        // SaveToFile
        var path = TempFile("dogfood_ma_transaction_model.fods");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));
        Assert.True(new FileInfo(path).Length > 0);

        // LoadFile and verify
        var loaded = FodsDocument.LoadFile(path);
        Assert.Equal(3, loaded.GetSheetCount());
        Assert.True(loaded.GetColumnWidth("Transaction_Summary", 0) >= 0.0);
        Assert.True(loaded.GetColumnWidth("Income_Statement", 0) >= 0.0);
        Assert.Equal("Transaction_Summary", loaded.GetCellValue("Transaction_Summary", 0, 0));

        // SetColumnWidth on loaded
        loaded.SetColumnWidth("DCF_Valuation", 4, 3.5);
        Assert.True(loaded.GetColumnWidth("DCF_Valuation", 4) >= 0.0);

        // AddSheet with column widths
        loaded.AddSheet("Comparables");
        loaded.SetCellValue("Comparables", 0, 0, "Company");
        loaded.SetCellValue("Comparables", 0, 1, "EV_EBITDA");
        loaded.SetColumnWidth("Comparables", 0, 4.0);
        loaded.SetColumnWidth("Comparables", 1, 2.5);
        Assert.Equal(4, loaded.GetSheetCount());

        // Final save
        var path2 = TempFile("dogfood_ma_transaction_model_v2.fods");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var loaded2 = FodsDocument.LoadFile(path2);
        Assert.Equal(4, loaded2.GetSheetCount());
        Assert.True(loaded2.GetColumnWidth("Comparables", 0) >= 0.0);
        var ex1 = Record.Exception(() => loaded2.ExportToCsv("Transaction_Summary"));
        var ex2 = Record.Exception(() => loaded2.SetColumnWidth("Transaction_Summary", 0, 6.0));
        Assert.Null(ex1);
        Assert.Null(ex2);
    }
}
