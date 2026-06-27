// Tests for FodsDocument.GetCellCommentAuthor, GetCellCommentDate deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODS-R407

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R407: Tests for FodsDocument.GetCellCommentAuthor, GetCellCommentDate deeper.
/// GetCellCommentAuthor(sheet, row, col): returns the author of the cell comment, or null if no comment.
/// GetCellCommentDate(sheet, row, col): returns the date/timestamp of the cell comment, or null if no comment.
/// Covers: GetCellCommentAuthor no-throw; GetCellCommentAuthor null for no-comment;
/// GetCellCommentAuthor consistent; GetCellCommentAuthor non-null after SetCellComment;
/// GetCellCommentAuthor save-load; GetCellCommentDate no-throw; GetCellCommentDate null for no-comment;
/// GetCellCommentDate consistent; GetCellCommentDate save-load;
/// dogfood CreateDoc→SetCellComment→GetCellCommentAuthor→GetCellCommentDate→SaveToFile pipeline.
/// </summary>
public class FodsR407GetCellCommentAuthorAndGetCellCommentDateDeepTests : IDisposable
{
    private readonly string _tempDir;

    public FodsR407GetCellCommentAuthorAndGetCellCommentDateDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodsR407_" + Guid.NewGuid().ToString("N"));
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
        doc.SetCellValue("Sheet1", 0, 0, "Assumption");
        doc.SetCellValue("Sheet1", 0, 1, "Value");
        doc.SetCellValue("Sheet1", 1, 0, "Revenue Growth Rate");
        doc.SetCellValue("Sheet1", 1, 1, "8.5%");
        doc.SetCellValue("Sheet1", 2, 0, "EBITDA Margin");
        doc.SetCellValue("Sheet1", 2, 1, "22.3%");
        return doc;
    }

    // -------------------------------------------------------------------------
    // GetCellCommentAuthor
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellCommentAuthor_NoThrow()
    {
        var doc = CreateWorkbook();
        var ex = Record.Exception(() => doc.GetCellCommentAuthor("Sheet1", 1, 1));
        Assert.Null(ex);
    }

    [Fact]
    public void GetCellCommentAuthor_Null_ForNoComment()
    {
        var doc = CreateWorkbook();
        Assert.Null(doc.GetCellCommentAuthor("Sheet1", 1, 1));
    }

    [Fact]
    public void GetCellCommentAuthor_Consistent()
    {
        var doc = CreateWorkbook();
        Assert.Equal(doc.GetCellCommentAuthor("Sheet1", 1, 1), doc.GetCellCommentAuthor("Sheet1", 1, 1));
    }

    [Fact]
    public void GetCellCommentAuthor_NonNull_After_SetCellComment()
    {
        var doc = CreateWorkbook();
        doc.SetCellComment("Sheet1", 1, 1, "Reviewed by CFO — aligned with H1 actuals", "CFO_Review");
        Assert.NotNull(doc.GetCellCommentAuthor("Sheet1", 1, 1));
    }

    [Fact]
    public void GetCellCommentAuthor_SaveLoad_Consistent()
    {
        var doc = CreateWorkbook();
        doc.SetCellComment("Sheet1", 1, 1, "Consensus estimate from sell-side analysts", "Equity_Research");
        var before = doc.GetCellCommentAuthor("Sheet1", 1, 1);
        var path = TempFile("ca_save.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetCellCommentAuthor("Sheet1", 1, 1));
    }

    // -------------------------------------------------------------------------
    // GetCellCommentDate
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellCommentDate_NoThrow()
    {
        var doc = CreateWorkbook();
        var ex = Record.Exception(() => doc.GetCellCommentDate("Sheet1", 2, 1));
        Assert.Null(ex);
    }

    [Fact]
    public void GetCellCommentDate_Null_ForNoComment()
    {
        var doc = CreateWorkbook();
        Assert.Null(doc.GetCellCommentDate("Sheet1", 2, 1));
    }

    [Fact]
    public void GetCellCommentDate_Consistent()
    {
        var doc = CreateWorkbook();
        var d1 = doc.GetCellCommentDate("Sheet1", 2, 1);
        var d2 = doc.GetCellCommentDate("Sheet1", 2, 1);
        Assert.Equal(d1, d2);
    }

    [Fact]
    public void GetCellCommentDate_SaveLoad_Consistent()
    {
        var doc = CreateWorkbook();
        doc.SetCellComment("Sheet1", 2, 1, "Benchmarked against Sector median 21.8%", "Strategy_Team");
        var before = doc.GetCellCommentDate("Sheet1", 2, 1);
        var path = TempFile("cd_save.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetCellCommentDate("Sheet1", 2, 1));
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetCellCommentAuthor_GetCellCommentDate_SaveToFile_Pipeline()
    {
        // Finance — UK Private Equity: Leveraged Buyout (LBO) Model Review
        // Board paper workbook with analyst commentary embedded as cell comments
        // Multi-reviewer audit trail for investment committee sign-off

        var doc = FodsDocument.CreateEmpty();

        // Sheet 1: Key Assumptions — with reviewer comments
        doc.SetCellValue("Sheet1", 0, 0, "Assumption Category");
        doc.SetCellValue("Sheet1", 0, 1, "Base Case");
        doc.SetCellValue("Sheet1", 0, 2, "Bear Case");
        doc.SetCellValue("Sheet1", 0, 3, "Bull Case");
        doc.SetCellValue("Sheet1", 0, 4, "Reviewer");

        string[,] assumptions = {
            { "Revenue CAGR (FY25-30)", "8.5%", "4.2%", "13.1%", "Senior Analyst" },
            { "EBITDA Margin FY30", "24.8%", "19.2%", "29.5%", "VP Finance" },
            { "Entry Multiple (EV/EBITDA)", "9.2x", "9.2x", "9.2x", "MD" },
            { "Exit Multiple (EV/EBITDA)", "8.5x", "7.0x", "10.0x", "Investment Committee" },
            { "Leverage at Entry (ND/EBITDA)", "4.8x", "4.8x", "4.8x", "CFO" },
            { "Cost of Debt (Pre-tax)", "7.25%", "8.50%", "6.50%", "Debt Capital Markets" },
            { "Management Equity (% diluted)", "12.5%", "12.5%", "12.5%", "CEO" },
            { "Hold Period (Years)", "5", "5", "5", "Fund Manager" }
        };

        for (int i = 0; i < assumptions.GetLength(0); i++)
        {
            doc.SetCellValue("Sheet1", i + 1, 0, assumptions[i, 0]);
            doc.SetCellValue("Sheet1", i + 1, 1, assumptions[i, 1]);
            doc.SetCellValue("Sheet1", i + 1, 2, assumptions[i, 2]);
            doc.SetCellValue("Sheet1", i + 1, 3, assumptions[i, 3]);
            doc.SetCellValue("Sheet1", i + 1, 4, assumptions[i, 4]);
        }

        // Add reviewer comments to key cells
        doc.SetCellComment("Sheet1", 1, 1,
            "Based on management's FY24 trading update and consensus of 3 sell-side forecasts. Sensitivity range: ±2pp per 100bps market growth variance.",
            "J.Thompson_SeniorAnalyst");
        doc.SetCellComment("Sheet1", 2, 1,
            "Management guided 23-26% by FY29; we apply 1.5pp operational efficiency premium. Board has approved this assumption per IC Paper IC-2024-089.",
            "R.Patel_VPFinance");
        doc.SetCellComment("Sheet1", 3, 2,
            "Entry multiple reflects trailing 12-month EBITDA of £48.2m on agreed enterprise value of £443.4m. Verified against audited FY24 accounts.",
            "K.Williams_MD");
        doc.SetCellComment("Sheet1", 4, 1,
            "Exit at 8.5x assumes modest multiple compression vs entry 9.2x; in line with listed comps forward P/E of 14-16x, implying 8.0-9.0x EV/EBITDA.",
            "IC_SecretaryOffice");

        // Verify comments set
        Assert.NotNull(doc.GetCellCommentAuthor("Sheet1", 1, 1));
        Assert.NotNull(doc.GetCellCommentAuthor("Sheet1", 2, 1));
        Assert.NotNull(doc.GetCellCommentAuthor("Sheet1", 3, 2));
        Assert.NotNull(doc.GetCellCommentAuthor("Sheet1", 4, 1));

        // Verify no comment on header
        Assert.Null(doc.GetCellCommentAuthor("Sheet1", 0, 0));
        Assert.Null(doc.GetCellCommentDate("Sheet1", 0, 0));

        // Consistent reads
        var auth1 = doc.GetCellCommentAuthor("Sheet1", 1, 1);
        Assert.Equal(auth1, doc.GetCellCommentAuthor("Sheet1", 1, 1));
        var date2 = doc.GetCellCommentDate("Sheet1", 2, 1);
        Assert.Equal(date2, doc.GetCellCommentDate("Sheet1", 2, 1));

        // Sheet 2: Returns Analysis — with IC sign-off comments
        doc.AddSheet("Returns_Analysis");
        doc.SetCellValue("Returns_Analysis", 0, 0, "Metric");
        doc.SetCellValue("Returns_Analysis", 0, 1, "Base Case");
        doc.SetCellValue("Returns_Analysis", 0, 2, "Bear Case");
        doc.SetCellValue("Returns_Analysis", 0, 3, "Bull Case");
        doc.SetCellValue("Returns_Analysis", 1, 0, "Gross IRR");
        doc.SetCellValue("Returns_Analysis", 1, 1, "22.4%");
        doc.SetCellValue("Returns_Analysis", 1, 2, "11.8%");
        doc.SetCellValue("Returns_Analysis", 1, 3, "34.1%");
        doc.SetCellValue("Returns_Analysis", 2, 0, "Net IRR");
        doc.SetCellValue("Returns_Analysis", 2, 1, "18.9%");
        doc.SetCellValue("Returns_Analysis", 2, 2, "9.2%");
        doc.SetCellValue("Returns_Analysis", 2, 3, "29.6%");
        doc.SetCellValue("Returns_Analysis", 3, 0, "MOIC");
        doc.SetCellValue("Returns_Analysis", 3, 1, "2.8x");
        doc.SetCellValue("Returns_Analysis", 3, 2, "1.6x");
        doc.SetCellValue("Returns_Analysis", 3, 3, "4.2x");

        doc.SetCellComment("Returns_Analysis", 1, 1,
            "IC APPROVED: 22.4% gross IRR exceeds 20% hurdle rate. Approved by IC vote 5-0 on 15 Nov 2024. Reference: IC-MIN-20241115.",
            "IC_Chair");
        doc.SetCellComment("Returns_Analysis", 2, 1,
            "Net IRR after 2% management fee and 20% carried interest. Verified by Fund Accounting team. FA-VERIFY-20241116.",
            "FundAccounting_Head");

        Assert.NotNull(doc.GetCellCommentAuthor("Returns_Analysis", 1, 1));
        Assert.NotNull(doc.GetCellCommentDate("Returns_Analysis", 1, 1));

        // Basic assertions
        Assert.True(doc.GetSheetCount() >= 2);

        // SaveToFile
        var path1 = TempFile("dogfood_lbo_model_review.fods");
        doc.SaveToFile(path1);
        Assert.True(File.Exists(path1));
        Assert.True(new FileInfo(path1).Length > 0);

        // LoadFile and verify comments persisted
        var loaded = FodsDocument.LoadFile(path1);
        Assert.Equal(auth1, loaded.GetCellCommentAuthor("Sheet1", 1, 1));
        Assert.Equal(date2, loaded.GetCellCommentDate("Sheet1", 2, 1));
        Assert.Null(loaded.GetCellCommentAuthor("Sheet1", 0, 0));
        Assert.NotNull(loaded.GetCellCommentAuthor("Returns_Analysis", 1, 1));

        // Add risk committee review sheet
        loaded.AddSheet("Risk_Committee_Review");
        loaded.SetCellValue("Risk_Committee_Review", 0, 0, "Risk Factor");
        loaded.SetCellValue("Risk_Committee_Review", 0, 1, "Assessment");
        loaded.SetCellValue("Risk_Committee_Review", 1, 0, "Market Risk");
        loaded.SetCellValue("Risk_Committee_Review", 1, 1, "MEDIUM");
        loaded.SetCellComment("Risk_Committee_Review", 1, 1,
            "Revenue cyclicality mitigated by long-term contracts (avg 3.2yr). CRO review complete. CRO-20241118.",
            "CRO_SignOff");
        Assert.NotNull(loaded.GetCellCommentAuthor("Risk_Committee_Review", 1, 1));

        // Final save
        var path2 = TempFile("dogfood_lbo_model_review_final.fods");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var final = FodsDocument.LoadFile(path2);
        Assert.Equal(auth1, final.GetCellCommentAuthor("Sheet1", 1, 1));
        Assert.NotNull(final.GetCellCommentAuthor("Risk_Committee_Review", 1, 1));

        var ex1 = Record.Exception(() => final.GetCellCommentAuthor("Sheet1", 5, 5));
        var ex2 = Record.Exception(() => final.GetCellCommentDate("Sheet1", 5, 5));
        Assert.Null(ex1);
        Assert.Null(ex2);
        Assert.Null(final.GetCellCommentAuthor("Sheet1", 5, 5)); // empty cell
    }
}
