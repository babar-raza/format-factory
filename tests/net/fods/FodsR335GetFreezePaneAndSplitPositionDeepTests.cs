// Tests for FodsDocument.GetFreezePaneRow, GetFreezePaneColumn, SetFreezePane deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODS-R335

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R335: Tests for FodsDocument.GetFreezePaneRow, GetFreezePaneColumn, SetFreezePane deeper.
/// GetFreezePaneRow(sheet): returns the row index at which the freeze pane is set (0 = no freeze).
/// GetFreezePaneColumn(sheet): returns the column index at which the freeze pane is set.
/// SetFreezePane(sheet, row, col): sets a freeze pane at the given row/column split position.
/// Covers: GetFreezePaneRow no-throw; GetFreezePaneRow non-negative; GetFreezePaneRow consistent;
/// GetFreezePaneRow zero for no freeze; GetFreezePaneRow save-load;
/// GetFreezePaneColumn no-throw; GetFreezePaneColumn non-negative; GetFreezePaneColumn consistent;
/// GetFreezePaneColumn zero for no freeze; GetFreezePaneColumn save-load;
/// SetFreezePane no-throw; SetFreezePane updates row; SetFreezePane updates column;
/// SetFreezePane save-load; SetFreezePane then GetCharCount positive;
/// SetFreezePane then ExportToHtml no-throw;
/// dogfood CreateDoc→SetFreezePane→GetFreezePaneRow→GetFreezePaneColumn→SaveToFile pipeline.
/// </summary>
public class FodsR335GetFreezePaneAndSplitPositionDeepTests : IDisposable
{
    private readonly string _tempDir;

    public FodsR335GetFreezePaneAndSplitPositionDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodsR335_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private static FodsDocument CreateDataSheet()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("DataTable");
        string[] headers = { "ID", "Name", "Department", "Salary", "StartDate", "Manager", "Location" };
        for (int c = 0; c < headers.Length; c++)
            doc.SetCellValue("DataTable", 0, c, headers[c]);
        for (int r = 1; r <= 12; r++)
        {
            doc.SetCellValue("DataTable", r, 0, $"EMP{r:D3}");
            doc.SetCellValue("DataTable", r, 1, $"Employee_{r}");
            doc.SetCellValue("DataTable", r, 2, new[] { "Engineering", "Finance", "HR", "Sales" }[r % 4]);
            doc.SetCellValue("DataTable", r, 3, (50000 + r * 3500).ToString());
            doc.SetCellValue("DataTable", r, 4, $"2020-{(r % 12) + 1:D2}-{(r % 28) + 1:D2}");
            doc.SetCellValue("DataTable", r, 5, $"Manager_{(r % 3) + 1}");
            doc.SetCellValue("DataTable", r, 6, new[] { "London", "New York", "Singapore" }[r % 3]);
        }
        return doc;
    }

    // -------------------------------------------------------------------------
    // GetFreezePaneRow
    // -------------------------------------------------------------------------

    [Fact]
    public void GetFreezePaneRow_NoThrow()
    {
        var doc = CreateDataSheet();
        var ex = Record.Exception(() => doc.GetFreezePaneRow("DataTable"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetFreezePaneRow_NonNegative()
    {
        var doc = CreateDataSheet();
        Assert.True(doc.GetFreezePaneRow("DataTable") >= 0);
    }

    [Fact]
    public void GetFreezePaneRow_Consistent()
    {
        var doc = CreateDataSheet();
        Assert.Equal(doc.GetFreezePaneRow("DataTable"), doc.GetFreezePaneRow("DataTable"));
    }

    [Fact]
    public void GetFreezePaneRow_Zero_ForNoFreeze()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("NoFreeze");
        Assert.Equal(0, doc.GetFreezePaneRow("NoFreeze"));
    }

    [Fact]
    public void GetFreezePaneRow_SaveLoad_Consistent()
    {
        var doc = CreateDataSheet();
        doc.SetFreezePane("DataTable", 1, 0);
        var before = doc.GetFreezePaneRow("DataTable");
        var path = TempFile("fpr_save.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetFreezePaneRow("DataTable"));
    }

    // -------------------------------------------------------------------------
    // GetFreezePaneColumn
    // -------------------------------------------------------------------------

    [Fact]
    public void GetFreezePaneColumn_NoThrow()
    {
        var doc = CreateDataSheet();
        var ex = Record.Exception(() => doc.GetFreezePaneColumn("DataTable"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetFreezePaneColumn_NonNegative()
    {
        var doc = CreateDataSheet();
        Assert.True(doc.GetFreezePaneColumn("DataTable") >= 0);
    }

    [Fact]
    public void GetFreezePaneColumn_Consistent()
    {
        var doc = CreateDataSheet();
        Assert.Equal(doc.GetFreezePaneColumn("DataTable"), doc.GetFreezePaneColumn("DataTable"));
    }

    [Fact]
    public void GetFreezePaneColumn_Zero_ForNoFreeze()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("NoFreeze");
        Assert.Equal(0, doc.GetFreezePaneColumn("NoFreeze"));
    }

    [Fact]
    public void GetFreezePaneColumn_SaveLoad_Consistent()
    {
        var doc = CreateDataSheet();
        doc.SetFreezePane("DataTable", 0, 2);
        var before = doc.GetFreezePaneColumn("DataTable");
        var path = TempFile("fpc_save.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetFreezePaneColumn("DataTable"));
    }

    // -------------------------------------------------------------------------
    // SetFreezePane
    // -------------------------------------------------------------------------

    [Fact]
    public void SetFreezePane_NoThrow()
    {
        var doc = CreateDataSheet();
        var ex = Record.Exception(() => doc.SetFreezePane("DataTable", 1, 1));
        Assert.Null(ex);
    }

    [Fact]
    public void SetFreezePane_Updates_Row()
    {
        var doc = CreateDataSheet();
        doc.SetFreezePane("DataTable", 2, 0);
        Assert.Equal(2, doc.GetFreezePaneRow("DataTable"));
    }

    [Fact]
    public void SetFreezePane_Updates_Column()
    {
        var doc = CreateDataSheet();
        doc.SetFreezePane("DataTable", 0, 3);
        Assert.Equal(3, doc.GetFreezePaneColumn("DataTable"));
    }

    [Fact]
    public void SetFreezePane_SaveLoad_Persists()
    {
        var doc = CreateDataSheet();
        doc.SetFreezePane("DataTable", 1, 2);
        var path = TempFile("sfp_save.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        Assert.Equal(1, loaded.GetFreezePaneRow("DataTable"));
        Assert.Equal(2, loaded.GetFreezePaneColumn("DataTable"));
    }

    [Fact]
    public void SetFreezePane_Then_GetCharCount_Positive()
    {
        var doc = CreateDataSheet();
        doc.SetFreezePane("DataTable", 1, 1);
        Assert.True(doc.GetCharCount() > 0);
    }

    [Fact]
    public void SetFreezePane_Then_ExportToHtml_NoThrow()
    {
        var doc = CreateDataSheet();
        doc.SetFreezePane("DataTable", 1, 0);
        var ex = Record.Exception(() => doc.ExportToHtml());
        Assert.Null(ex);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_SetFreezePane_GetFreezePaneRow_GetFreezePaneColumn_SaveToFile_Pipeline()
    {
        // Financial modelling — multi-sheet P&L with freeze panes for header navigation
        var doc = FodsDocument.CreateEmpty();

        // Income Statement sheet
        doc.AddSheet("IncomeStatement");
        string[] isHeaders = { "Line Item", "Q1 2026", "Q2 2026", "Q3 2026", "Q4 2026", "FY 2026", "FY 2025", "YoY %" };
        for (int c = 0; c < isHeaders.Length; c++)
            doc.SetCellValue("IncomeStatement", 0, c, isHeaders[c]);
        string[] isRows = { "Revenue", "Cost of Goods Sold", "Gross Profit", "R&D Expense", "SG&A Expense", "EBIT", "Interest Expense", "EBT", "Tax Provision", "Net Income" };
        int[] q1Values = { 125000, 72000, 53000, 18000, 22000, 13000, 1500, 11500, 2875, 8625 };
        for (int r = 0; r < isRows.Length; r++)
        {
            doc.SetCellValue("IncomeStatement", r + 1, 0, isRows[r]);
            for (int q = 0; q < 4; q++)
                doc.SetCellValue("IncomeStatement", r + 1, q + 1, (q1Values[r] * (1.0 + q * 0.05)).ToString("F0"));
        }

        // Balance Sheet sheet
        doc.AddSheet("BalanceSheet");
        string[] bsHeaders = { "Account", "Dec 2025", "Mar 2026", "Jun 2026", "Sep 2026", "Dec 2026" };
        for (int c = 0; c < bsHeaders.Length; c++)
            doc.SetCellValue("BalanceSheet", 0, c, bsHeaders[c]);
        for (int r = 1; r <= 12; r++)
            for (int c = 0; c < 6; c++)
                doc.SetCellValue("BalanceSheet", r, c, c == 0 ? $"Account_{r}" : (r * c * 10000).ToString());

        // GetFreezePaneRow — zero initially (no freeze)
        Assert.Equal(0, doc.GetFreezePaneRow("IncomeStatement"));
        Assert.Equal(0, doc.GetFreezePaneColumn("IncomeStatement"));

        // SetFreezePane on IncomeStatement — freeze header row
        doc.SetFreezePane("IncomeStatement", 1, 1);
        Assert.Equal(1, doc.GetFreezePaneRow("IncomeStatement"));
        Assert.Equal(1, doc.GetFreezePaneColumn("IncomeStatement"));
        Assert.Equal(doc.GetFreezePaneRow("IncomeStatement"), doc.GetFreezePaneRow("IncomeStatement")); // consistent

        // SetFreezePane on BalanceSheet — freeze header row and first column
        doc.SetFreezePane("BalanceSheet", 1, 1);
        Assert.Equal(1, doc.GetFreezePaneRow("BalanceSheet"));
        Assert.Equal(1, doc.GetFreezePaneColumn("BalanceSheet"));

        // Reconfigure freeze pane
        doc.SetFreezePane("IncomeStatement", 2, 2);
        Assert.Equal(2, doc.GetFreezePaneRow("IncomeStatement"));
        Assert.Equal(2, doc.GetFreezePaneColumn("IncomeStatement"));

        // ExportToHtml
        var html = doc.ExportToHtml();
        Assert.NotNull(html);
        Assert.NotEmpty(html);

        // GetCharCount positive
        Assert.True(doc.GetCharCount() > 0);

        // SaveToFile
        var path = TempFile("dogfood_pnl_freeze.fods");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));
        Assert.True(new FileInfo(path).Length > 0);

        // LoadFile and verify freeze pane persistence
        var loaded = FodsDocument.LoadFile(path);
        Assert.Equal(2, loaded.GetFreezePaneRow("IncomeStatement"));
        Assert.Equal(2, loaded.GetFreezePaneColumn("IncomeStatement"));
        Assert.Equal(1, loaded.GetFreezePaneRow("BalanceSheet"));
        Assert.Equal(1, loaded.GetFreezePaneColumn("BalanceSheet"));

        // Update freeze pane on loaded
        loaded.SetFreezePane("IncomeStatement", 1, 1);
        Assert.Equal(1, loaded.GetFreezePaneRow("IncomeStatement"));

        // ExportToHtml on loaded
        var loadedHtml = loaded.ExportToHtml();
        Assert.NotNull(loadedHtml);
        Assert.NotEmpty(loadedHtml);

        // SetCellValue on loaded
        loaded.SetCellValue("IncomeStatement", 11, 0, "Adjusted Net Income");
        loaded.SetCellValue("IncomeStatement", 11, 1, "9200");

        // Final save
        var path2 = TempFile("dogfood_pnl_freeze_v2.fods");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var loaded2 = FodsDocument.LoadFile(path2);
        Assert.Equal(1, loaded2.GetFreezePaneRow("IncomeStatement"));
        Assert.Equal(1, loaded2.GetFreezePaneColumn("IncomeStatement"));
        var ex1 = Record.Exception(() => loaded2.ExportToHtml());
        var ex2 = Record.Exception(() => loaded2.GetFreezePaneRow("BalanceSheet"));
        var ex3 = Record.Exception(() => loaded2.SetFreezePane("BalanceSheet", 2, 0));
        Assert.Null(ex1);
        Assert.Null(ex2);
        Assert.Null(ex3);
    }
}
