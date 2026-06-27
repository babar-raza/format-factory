// Tests for FodsDocument.GetCellCommentCount, AddCellComment, GetCellComment deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODS-R349

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R349: Tests for FodsDocument.GetCellCommentCount, AddCellComment, GetCellComment deeper.
/// GetCellCommentCount(): returns the number of cell comments in the document.
/// AddCellComment(sheetName, row, column, text): adds a comment to the specified cell.
/// GetCellComment(sheetName, row, column): returns the comment text for the specified cell.
/// Covers: GetCellCommentCount no-throw; GetCellCommentCount non-negative; GetCellCommentCount consistent;
/// GetCellCommentCount zero for new doc; GetCellCommentCount after AddCellComment increases;
/// GetCellCommentCount save-load;
/// AddCellComment no-throw; AddCellComment increases count; AddCellComment save-load;
/// AddCellComment multiple; AddCellComment then ExportToHtml no-throw;
/// AddCellComment then GetCellValue no-throw;
/// GetCellComment no-throw; GetCellComment non-null; GetCellComment consistent;
/// GetCellComment save-load;
/// dogfood CreateDoc→AddCellComment→GetCellCommentCount→GetCellComment→SaveToFile pipeline.
/// </summary>
public class FodsR349GetCellCommentCountAndAddCellCommentDeepTests : IDisposable
{
    private readonly string _tempDir;

    public FodsR349GetCellCommentCountAndAddCellCommentDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodsR349_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private static FodsDocument CreateAuditWorkbookDoc()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("TrialBalance");
        doc.SetCellValue("TrialBalance", 0, 0, "Account");
        doc.SetCellValue("TrialBalance", 0, 1, "Description");
        doc.SetCellValue("TrialBalance", 0, 2, "Debit");
        doc.SetCellValue("TrialBalance", 0, 3, "Credit");
        string[] accounts = { "1100", "1200", "2100", "3100", "4100", "5100" };
        string[] descs = { "Cash_and_Equivalents", "Accounts_Receivable", "Accounts_Payable", "Share_Capital", "Revenue", "Cost_of_Sales" };
        for (int r = 1; r <= 6; r++)
        {
            doc.SetCellValue("TrialBalance", r, 0, accounts[r - 1]);
            doc.SetCellValue("TrialBalance", r, 1, descs[r - 1]);
            doc.SetCellValue("TrialBalance", r, 2, (r % 2 == 0 ? "" : (r * 50000).ToString()));
            doc.SetCellValue("TrialBalance", r, 3, (r % 2 == 0 ? (r * 50000).ToString() : ""));
        }
        return doc;
    }

    // -------------------------------------------------------------------------
    // GetCellCommentCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellCommentCount_NoThrow()
    {
        var doc = CreateAuditWorkbookDoc();
        var ex = Record.Exception(() => doc.GetCellCommentCount());
        Assert.Null(ex);
    }

    [Fact]
    public void GetCellCommentCount_NonNegative()
    {
        var doc = CreateAuditWorkbookDoc();
        Assert.True(doc.GetCellCommentCount() >= 0);
    }

    [Fact]
    public void GetCellCommentCount_Consistent()
    {
        var doc = CreateAuditWorkbookDoc();
        Assert.Equal(doc.GetCellCommentCount(), doc.GetCellCommentCount());
    }

    [Fact]
    public void GetCellCommentCount_Zero_ForNewDoc()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("Empty");
        Assert.Equal(0, doc.GetCellCommentCount());
    }

    [Fact]
    public void GetCellCommentCount_AfterAddCellComment_Increases()
    {
        var doc = CreateAuditWorkbookDoc();
        var before = doc.GetCellCommentCount();
        doc.AddCellComment("TrialBalance", 1, 2, "Auditor note: reconciled to bank statement 31/03/2024.");
        Assert.Equal(before + 1, doc.GetCellCommentCount());
    }

    [Fact]
    public void GetCellCommentCount_SaveLoad_Consistent()
    {
        var doc = CreateAuditWorkbookDoc();
        doc.AddCellComment("TrialBalance", 2, 2, "Per aged debtors schedule — refer to W/P B.3.");
        var before = doc.GetCellCommentCount();
        var path = TempFile("ccc_save.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetCellCommentCount());
    }

    // -------------------------------------------------------------------------
    // AddCellComment
    // -------------------------------------------------------------------------

    [Fact]
    public void AddCellComment_NoThrow()
    {
        var doc = CreateAuditWorkbookDoc();
        var ex = Record.Exception(() => doc.AddCellComment("TrialBalance", 3, 3, "Per purchase ledger listing W/P C.1."));
        Assert.Null(ex);
    }

    [Fact]
    public void AddCellComment_Increases_Count()
    {
        var doc = CreateAuditWorkbookDoc();
        var before = doc.GetCellCommentCount();
        doc.AddCellComment("TrialBalance", 4, 2, "Agrees to company register filed at Companies House.");
        Assert.Equal(before + 1, doc.GetCellCommentCount());
    }

    [Fact]
    public void AddCellComment_SaveLoad_Persists()
    {
        var doc = CreateAuditWorkbookDoc();
        doc.AddCellComment("TrialBalance", 5, 2, "Revenue recognised per IFRS 15 — see contract schedule.");
        var before = doc.GetCellCommentCount();
        var path = TempFile("acc_save.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetCellCommentCount());
    }

    [Fact]
    public void AddCellComment_Multiple()
    {
        var doc = CreateAuditWorkbookDoc();
        doc.AddCellComment("TrialBalance", 1, 2, "Comment A");
        doc.AddCellComment("TrialBalance", 2, 2, "Comment B");
        doc.AddCellComment("TrialBalance", 3, 3, "Comment C");
        Assert.Equal(3, doc.GetCellCommentCount());
    }

    [Fact]
    public void AddCellComment_Then_ExportToHtml_NoThrow()
    {
        var doc = CreateAuditWorkbookDoc();
        doc.AddCellComment("TrialBalance", 1, 2, "HTML export comment.");
        var ex = Record.Exception(() => doc.ExportToHtml());
        Assert.Null(ex);
    }

    [Fact]
    public void AddCellComment_Then_GetCellValue_NoThrow()
    {
        var doc = CreateAuditWorkbookDoc();
        doc.AddCellComment("TrialBalance", 2, 2, "GetCellValue test comment.");
        var ex = Record.Exception(() => doc.GetCellValue("TrialBalance", 2, 2));
        Assert.Null(ex);
    }

    // -------------------------------------------------------------------------
    // GetCellComment
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellComment_NoThrow()
    {
        var doc = CreateAuditWorkbookDoc();
        doc.AddCellComment("TrialBalance", 1, 2, "Comment retrieval test.");
        var ex = Record.Exception(() => doc.GetCellComment("TrialBalance", 1, 2));
        Assert.Null(ex);
    }

    [Fact]
    public void GetCellComment_NonNull()
    {
        var doc = CreateAuditWorkbookDoc();
        doc.AddCellComment("TrialBalance", 2, 3, "Non-null comment test.");
        Assert.NotNull(doc.GetCellComment("TrialBalance", 2, 3));
    }

    [Fact]
    public void GetCellComment_Consistent()
    {
        var doc = CreateAuditWorkbookDoc();
        doc.AddCellComment("TrialBalance", 3, 2, "Consistency test comment.");
        Assert.Equal(doc.GetCellComment("TrialBalance", 3, 2), doc.GetCellComment("TrialBalance", 3, 2));
    }

    [Fact]
    public void GetCellComment_SaveLoad_Consistent()
    {
        var doc = CreateAuditWorkbookDoc();
        doc.AddCellComment("TrialBalance", 4, 3, "Save-load comment test.");
        var path = TempFile("gcc_save.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        Assert.NotNull(loaded.GetCellComment("TrialBalance", 4, 3));
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_AddCellComment_GetCellCommentCount_GetCellComment_SaveToFile_Pipeline()
    {
        // External audit — group consolidation workbook with audit trail comments
        var doc = FodsDocument.CreateEmpty();

        // ---- Group P&L sheet ----
        doc.AddSheet("GroupPL");
        string[] plLines = { "Revenue", "Cost_of_Sales", "Gross_Profit", "Operating_Expenses", "EBITDA", "Depreciation", "EBIT", "Finance_Costs", "PBT", "Tax", "PAT" };
        doc.SetCellValue("GroupPL", 0, 0, "Line_Item");
        doc.SetCellValue("GroupPL", 0, 1, "FY2024_GBPk");
        doc.SetCellValue("GroupPL", 0, 2, "FY2023_GBPk");
        doc.SetCellValue("GroupPL", 0, 3, "YoY_Change_Pct");
        doc.SetCellValue("GroupPL", 0, 4, "Audit_Status");
        for (int r = 1; r <= 11; r++)
        {
            doc.SetCellValue("GroupPL", r, 0, plLines[r - 1]);
            doc.SetCellValue("GroupPL", r, 1, (r * 8500 + 12000).ToString());
            doc.SetCellValue("GroupPL", r, 2, (r * 8000 + 11000).ToString());
            doc.SetCellValue("GroupPL", r, 3, "6.3");
            doc.SetCellValue("GroupPL", r, 4, r <= 5 ? "Agreed" : "Under_Review");
        }

        // ---- Balance Sheet sheet ----
        doc.AddSheet("BalanceSheet");
        doc.SetCellValue("BalanceSheet", 0, 0, "Account");
        doc.SetCellValue("BalanceSheet", 0, 1, "FY2024_GBPk");
        doc.SetCellValue("BalanceSheet", 0, 2, "FY2023_GBPk");
        string[] bsLines = { "Goodwill", "PPE", "DTRA", "Inventories", "Trade_Receivables", "Cash", "Total_Assets", "Trade_Payables", "Borrowings", "Equity" };
        for (int r = 1; r <= 10; r++)
        {
            doc.SetCellValue("BalanceSheet", r, 0, bsLines[r - 1]);
            doc.SetCellValue("BalanceSheet", r, 1, (r * 12000).ToString());
            doc.SetCellValue("BalanceSheet", r, 2, (r * 11000).ToString());
        }

        Assert.Equal(0, doc.GetCellCommentCount());

        // AddCellComment — audit annotations on P&L
        doc.AddCellComment("GroupPL", 1, 1, "Revenue: Agreed to management accounts and IFRS 15 disclosure schedules (W/P A2.1). No material adjustments required.");
        Assert.Equal(1, doc.GetCellCommentCount());

        doc.AddCellComment("GroupPL", 2, 1, "Cost of Sales: Includes £2.1M inventory write-down — see W/P A4.3. Approved by CFO 28/04/2024.");
        Assert.Equal(2, doc.GetCellCommentCount());

        doc.AddCellComment("GroupPL", 5, 3, "YoY Change: EBITDA margin improved 1.2pp to 24.1% — driven by operating leverage on fixed cost base.");
        Assert.Equal(3, doc.GetCellCommentCount());

        // AddCellComment — audit annotations on Balance Sheet
        doc.AddCellComment("BalanceSheet", 1, 1, "Goodwill: Impairment test completed. VIU model reviewed — no impairment required. Key assumption: 5-year CAGR 7.5%. (W/P BS1.4)");
        Assert.Equal(4, doc.GetCellCommentCount());

        doc.AddCellComment("BalanceSheet", 5, 1, "Trade Receivables: Aged debtors reviewed. Bad debt provision £0.8M (0.6% of revenue) — adequate per IFRS 9 ECL model (W/P BS3.2).");
        Assert.Equal(5, doc.GetCellCommentCount());

        doc.AddCellComment("BalanceSheet", 6, 1, "Cash: Confirmed by bank letter from Barclays and HSBC (received 15/04/2024). Cash balances reconciled to TB. (W/P BS4.1)");
        Assert.Equal(6, doc.GetCellCommentCount());

        // Consistent
        Assert.Equal(doc.GetCellCommentCount(), doc.GetCellCommentCount());

        // GetCellComment
        var plRevComment = doc.GetCellComment("GroupPL", 1, 1);
        Assert.NotNull(plRevComment);
        Assert.Equal(plRevComment, doc.GetCellComment("GroupPL", 1, 1)); // consistent

        var bsGoodwillComment = doc.GetCellComment("BalanceSheet", 1, 1);
        Assert.NotNull(bsGoodwillComment);

        var cashComment = doc.GetCellComment("BalanceSheet", 6, 1);
        Assert.NotNull(cashComment);

        // ExportToHtml
        var html = doc.ExportToHtml();
        Assert.NotNull(html);
        Assert.NotEmpty(html);

        // GetCellValue
        Assert.NotNull(doc.GetCellValue("GroupPL", 1, 0));

        // GetSheetCount
        Assert.True(doc.GetSheetCount() >= 2);

        // SaveToFile
        var path = TempFile("dogfood_audit_workbook.fods");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));
        Assert.True(new FileInfo(path).Length > 0);

        // LoadFile and verify
        var loaded = FodsDocument.LoadFile(path);
        Assert.Equal(6, loaded.GetCellCommentCount());
        Assert.NotNull(loaded.GetCellComment("GroupPL", 1, 1));
        Assert.NotNull(loaded.GetCellComment("BalanceSheet", 6, 1));

        // AddCellComment on loaded
        loaded.AddCellComment("GroupPL", 9, 1, "Tax: Effective tax rate 24.1% — in line with UK corporate tax rate for FY2024. Deferred tax position reviewed (W/P T.1).");
        Assert.Equal(7, loaded.GetCellCommentCount());

        // ExportToHtml on loaded
        var loadedHtml = loaded.ExportToHtml();
        Assert.NotNull(loadedHtml);
        Assert.NotEmpty(loadedHtml);

        // Final save
        var path2 = TempFile("dogfood_audit_workbook_v2.fods");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var loaded2 = FodsDocument.LoadFile(path2);
        Assert.Equal(7, loaded2.GetCellCommentCount());
        Assert.NotNull(loaded2.GetCellComment("GroupPL", 1, 1));
        var ex1 = Record.Exception(() => loaded2.ExportToHtml());
        var ex2 = Record.Exception(() => loaded2.GetCellComment("BalanceSheet", 1, 1));
        var ex3 = Record.Exception(() => loaded2.AddCellComment("GroupPL", 10, 1, "PAT: Final figure agreed to consolidated financial statements."));
        Assert.Null(ex1);
        Assert.Null(ex2);
        Assert.Null(ex3);
    }
}
