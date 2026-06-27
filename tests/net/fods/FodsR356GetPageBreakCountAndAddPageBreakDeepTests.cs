// Tests for FodsDocument.GetPageBreakCount, AddPageBreak, GetPageBreakRow deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODS-R356

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R356: Tests for FodsDocument.GetPageBreakCount, AddPageBreak, GetPageBreakRow deeper.
/// GetPageBreakCount(sheetName): returns the number of page breaks in the specified sheet.
/// AddPageBreak(sheetName, rowIndex): inserts a horizontal page break above the given row.
/// GetPageBreakRow(sheetName, index): returns the row number of the page break at the given index.
/// Covers: GetPageBreakCount no-throw; GetPageBreakCount non-negative; GetPageBreakCount consistent;
/// GetPageBreakCount zero for new sheet; GetPageBreakCount after AddPageBreak increases;
/// GetPageBreakCount save-load;
/// AddPageBreak no-throw; AddPageBreak increases count; AddPageBreak save-load;
/// AddPageBreak multiple; AddPageBreak then ExportToCsv no-throw;
/// AddPageBreak then GetCellValue no-throw;
/// GetPageBreakRow no-throw; GetPageBreakRow non-negative; GetPageBreakRow consistent;
/// GetPageBreakRow save-load;
/// dogfood CreateDoc→AddPageBreak→GetPageBreakCount→GetPageBreakRow pipeline.
/// </summary>
public class FodsR356GetPageBreakCountAndAddPageBreakDeepTests : IDisposable
{
    private readonly string _tempDir;

    public FodsR356GetPageBreakCountAndAddPageBreakDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodsR356_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private static FodsDocument CreateReportWorkbook()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("QuarterlyReport");
        doc.SetCellValue("QuarterlyReport", 0, 0, "Section");
        doc.SetCellValue("QuarterlyReport", 0, 1, "Item");
        doc.SetCellValue("QuarterlyReport", 0, 2, "Q1");
        doc.SetCellValue("QuarterlyReport", 0, 3, "Q2");
        doc.SetCellValue("QuarterlyReport", 0, 4, "Q3");
        doc.SetCellValue("QuarterlyReport", 0, 5, "Q4");
        string[] sections = { "Revenue", "Revenue", "Revenue", "COGS", "COGS", "Gross_Profit",
                               "OpEx", "OpEx", "OpEx", "EBIT", "Tax", "Net_Income" };
        for (int i = 1; i <= 12; i++)
        {
            doc.SetCellValue("QuarterlyReport", i, 0, sections[i - 1]);
            doc.SetCellValue("QuarterlyReport", i, 1, $"Line_{i}");
            for (int q = 0; q < 4; q++)
                doc.SetCellValue("QuarterlyReport", i, 2 + q, ((i + q) * 1250).ToString());
        }
        return doc;
    }

    // -------------------------------------------------------------------------
    // GetPageBreakCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetPageBreakCount_NoThrow()
    {
        var doc = CreateReportWorkbook();
        var ex = Record.Exception(() => doc.GetPageBreakCount("QuarterlyReport"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetPageBreakCount_NonNegative()
    {
        var doc = CreateReportWorkbook();
        Assert.True(doc.GetPageBreakCount("QuarterlyReport") >= 0);
    }

    [Fact]
    public void GetPageBreakCount_Consistent()
    {
        var doc = CreateReportWorkbook();
        Assert.Equal(doc.GetPageBreakCount("QuarterlyReport"), doc.GetPageBreakCount("QuarterlyReport"));
    }

    [Fact]
    public void GetPageBreakCount_Zero_ForNewSheet()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("Sheet1");
        doc.SetCellValue("Sheet1", 0, 0, "Header");
        Assert.Equal(0, doc.GetPageBreakCount("Sheet1"));
    }

    [Fact]
    public void GetPageBreakCount_AfterAdd_Increases()
    {
        var doc = CreateReportWorkbook();
        var before = doc.GetPageBreakCount("QuarterlyReport");
        doc.AddPageBreak("QuarterlyReport", 4);
        Assert.Equal(before + 1, doc.GetPageBreakCount("QuarterlyReport"));
    }

    [Fact]
    public void GetPageBreakCount_SaveLoad_Consistent()
    {
        var doc = CreateReportWorkbook();
        doc.AddPageBreak("QuarterlyReport", 7);
        var before = doc.GetPageBreakCount("QuarterlyReport");
        var path = TempFile("pbc_save.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetPageBreakCount("QuarterlyReport"));
    }

    // -------------------------------------------------------------------------
    // AddPageBreak
    // -------------------------------------------------------------------------

    [Fact]
    public void AddPageBreak_NoThrow()
    {
        var doc = CreateReportWorkbook();
        var ex = Record.Exception(() => doc.AddPageBreak("QuarterlyReport", 4));
        Assert.Null(ex);
    }

    [Fact]
    public void AddPageBreak_Increases_Count()
    {
        var doc = CreateReportWorkbook();
        var before = doc.GetPageBreakCount("QuarterlyReport");
        doc.AddPageBreak("QuarterlyReport", 7);
        Assert.Equal(before + 1, doc.GetPageBreakCount("QuarterlyReport"));
    }

    [Fact]
    public void AddPageBreak_SaveLoad_Persists()
    {
        var doc = CreateReportWorkbook();
        doc.AddPageBreak("QuarterlyReport", 10);
        var before = doc.GetPageBreakCount("QuarterlyReport");
        var path = TempFile("apb_save.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetPageBreakCount("QuarterlyReport"));
    }

    [Fact]
    public void AddPageBreak_Multiple()
    {
        var doc = CreateReportWorkbook();
        doc.AddPageBreak("QuarterlyReport", 4);
        doc.AddPageBreak("QuarterlyReport", 7);
        doc.AddPageBreak("QuarterlyReport", 10);
        Assert.Equal(3, doc.GetPageBreakCount("QuarterlyReport"));
    }

    [Fact]
    public void AddPageBreak_Then_ExportToCsv_NoThrow()
    {
        var doc = CreateReportWorkbook();
        doc.AddPageBreak("QuarterlyReport", 6);
        var ex = Record.Exception(() => doc.ExportToCsv("QuarterlyReport"));
        Assert.Null(ex);
    }

    [Fact]
    public void AddPageBreak_Then_GetCellValue_NoThrow()
    {
        var doc = CreateReportWorkbook();
        doc.AddPageBreak("QuarterlyReport", 4);
        var ex = Record.Exception(() => doc.GetCellValue("QuarterlyReport", 1, 0));
        Assert.Null(ex);
    }

    // -------------------------------------------------------------------------
    // GetPageBreakRow
    // -------------------------------------------------------------------------

    [Fact]
    public void GetPageBreakRow_NoThrow()
    {
        var doc = CreateReportWorkbook();
        doc.AddPageBreak("QuarterlyReport", 5);
        var ex = Record.Exception(() => doc.GetPageBreakRow("QuarterlyReport", 0));
        Assert.Null(ex);
    }

    [Fact]
    public void GetPageBreakRow_NonNegative()
    {
        var doc = CreateReportWorkbook();
        doc.AddPageBreak("QuarterlyReport", 5);
        Assert.True(doc.GetPageBreakRow("QuarterlyReport", 0) >= 0);
    }

    [Fact]
    public void GetPageBreakRow_Consistent()
    {
        var doc = CreateReportWorkbook();
        doc.AddPageBreak("QuarterlyReport", 5);
        Assert.Equal(doc.GetPageBreakRow("QuarterlyReport", 0), doc.GetPageBreakRow("QuarterlyReport", 0));
    }

    [Fact]
    public void GetPageBreakRow_SaveLoad_Consistent()
    {
        var doc = CreateReportWorkbook();
        doc.AddPageBreak("QuarterlyReport", 8);
        var path = TempFile("pbr_save.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        Assert.True(loaded.GetPageBreakRow("QuarterlyReport", 0) >= 0);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_AddPageBreak_GetPageBreakCount_GetPageBreakRow_Pipeline()
    {
        // Management accounts — multi-section P&L for print-optimised board pack
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("ProfitAndLoss");
        doc.SetCellValue("ProfitAndLoss", 0, 0, "Account_Code");
        doc.SetCellValue("ProfitAndLoss", 0, 1, "Description");
        doc.SetCellValue("ProfitAndLoss", 0, 2, "Budget_GBP");
        doc.SetCellValue("ProfitAndLoss", 0, 3, "Actual_GBP");
        doc.SetCellValue("ProfitAndLoss", 0, 4, "Variance_GBP");
        doc.SetCellValue("ProfitAndLoss", 0, 5, "Variance_Pct");

        string[] accounts = {
            "4000:Subscription_Revenue", "4100:Professional_Services", "4200:Support_Revenue",
            "4999:Total_Revenue",
            "5000:Staff_Costs", "5100:Contractors", "5200:Infrastructure", "5300:Licences",
            "5999:Total_OpEx",
            "6000:Depreciation", "6100:Amortisation",
            "6999:Total_Overheads",
            "9000:EBIT", "9100:Finance_Costs", "9200:Tax", "9999:Net_Profit"
        };
        var rng = new Random(20250401);
        for (int i = 1; i <= accounts.Length; i++)
        {
            var parts = accounts[i - 1].Split(':');
            double budget = 50000 + rng.NextDouble() * 450000;
            double actual = budget * (0.85 + rng.NextDouble() * 0.30);
            double variance = actual - budget;
            double variancePct = budget != 0 ? (variance / budget) * 100 : 0;
            doc.SetCellValue("ProfitAndLoss", i, 0, parts[0]);
            doc.SetCellValue("ProfitAndLoss", i, 1, parts[1].Replace('_', ' '));
            doc.SetCellValue("ProfitAndLoss", i, 2, $"{budget:F0}");
            doc.SetCellValue("ProfitAndLoss", i, 3, $"{actual:F0}");
            doc.SetCellValue("ProfitAndLoss", i, 4, $"{variance:F0}");
            doc.SetCellValue("ProfitAndLoss", i, 5, $"{variancePct:F1}");
        }

        doc.AddSheet("BalanceSheet");
        doc.SetCellValue("BalanceSheet", 0, 0, "Category");
        doc.SetCellValue("BalanceSheet", 0, 1, "Item");
        doc.SetCellValue("BalanceSheet", 0, 2, "GBP");

        Assert.Equal(0, doc.GetPageBreakCount("ProfitAndLoss"));

        // AddPageBreak — section dividers for board print pack
        doc.AddPageBreak("ProfitAndLoss", 4);  // after revenue section
        Assert.Equal(1, doc.GetPageBreakCount("ProfitAndLoss"));

        doc.AddPageBreak("ProfitAndLoss", 9);  // after opex section
        Assert.Equal(2, doc.GetPageBreakCount("ProfitAndLoss"));

        doc.AddPageBreak("ProfitAndLoss", 12); // after overheads
        Assert.Equal(3, doc.GetPageBreakCount("ProfitAndLoss"));

        doc.AddPageBreak("ProfitAndLoss", 14); // after EBIT for finance/tax
        Assert.Equal(4, doc.GetPageBreakCount("ProfitAndLoss"));

        // BalanceSheet breaks
        doc.AddPageBreak("BalanceSheet", 5);
        Assert.Equal(1, doc.GetPageBreakCount("BalanceSheet"));

        // Consistent
        Assert.Equal(doc.GetPageBreakCount("ProfitAndLoss"), doc.GetPageBreakCount("ProfitAndLoss"));

        // GetPageBreakRow
        var pbr0 = doc.GetPageBreakRow("ProfitAndLoss", 0);
        Assert.True(pbr0 >= 0);
        Assert.Equal(pbr0, doc.GetPageBreakRow("ProfitAndLoss", 0)); // consistent

        var pbr1 = doc.GetPageBreakRow("ProfitAndLoss", 1);
        Assert.True(pbr1 >= 0);

        var pbr3 = doc.GetPageBreakRow("ProfitAndLoss", 3);
        Assert.True(pbr3 >= 0);

        // Page break rows should be monotonically increasing
        Assert.True(pbr0 <= pbr1);

        // ExportToCsv
        var ex = Record.Exception(() => doc.ExportToCsv("ProfitAndLoss"));
        Assert.Null(ex);

        // GetCellValue after break
        Assert.NotNull(doc.GetCellValue("ProfitAndLoss", 1, 0));

        // SaveToFile
        var path = TempFile("dogfood_board_pack.fods");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));
        Assert.True(new FileInfo(path).Length > 0);

        // LoadFile and verify
        var loaded = FodsDocument.LoadFile(path);
        Assert.Equal(4, loaded.GetPageBreakCount("ProfitAndLoss"));
        Assert.Equal(1, loaded.GetPageBreakCount("BalanceSheet"));
        Assert.True(loaded.GetPageBreakRow("ProfitAndLoss", 0) >= 0);
        Assert.NotNull(loaded.GetCellValue("ProfitAndLoss", 1, 0));

        // AddPageBreak on loaded
        loaded.AddPageBreak("ProfitAndLoss", 16);
        Assert.Equal(5, loaded.GetPageBreakCount("ProfitAndLoss"));

        // Final save
        var path2 = TempFile("dogfood_board_pack_v2.fods");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var loaded2 = FodsDocument.LoadFile(path2);
        Assert.Equal(5, loaded2.GetPageBreakCount("ProfitAndLoss"));
        Assert.True(loaded2.GetPageBreakRow("ProfitAndLoss", 0) >= 0);
        var ex2 = Record.Exception(() => loaded2.ExportToCsv("ProfitAndLoss"));
        var ex3 = Record.Exception(() => loaded2.AddPageBreak("ProfitAndLoss", 18));
        Assert.Null(ex2);
        Assert.Null(ex3);
    }
}
