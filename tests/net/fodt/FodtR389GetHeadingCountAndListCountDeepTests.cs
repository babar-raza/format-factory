// Tests for FodtDocument.GetHeadingCount, GetListCount deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODT-R389

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R389: Tests for FodtDocument.GetHeadingCount, GetListCount deeper.
/// GetHeadingCount(): returns the total number of headings (all levels) in the document.
/// GetListCount(): returns the total number of list items in the document.
/// Covers: GetHeadingCount no-throw; GetHeadingCount non-negative; GetHeadingCount zero for no-heading doc;
/// GetHeadingCount positive after InsertHeading; GetHeadingCount consistent; GetHeadingCount save-load;
/// GetHeadingCount increases per heading inserted; GetListCount no-throw; GetListCount non-negative;
/// GetListCount consistent; GetListCount save-load; dogfood pipeline.
/// </summary>
public class FodtR389GetHeadingCountAndListCountDeepTests : IDisposable
{
    private readonly string _tempDir;

    public FodtR389GetHeadingCountAndListCountDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodtR389_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    // -------------------------------------------------------------------------
    // GetHeadingCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetHeadingCount_NoThrow()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Title", 1);
        var ex = Record.Exception(() => doc.GetHeadingCount());
        Assert.Null(ex);
    }

    [Fact]
    public void GetHeadingCount_NonNegative()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Title", 1);
        Assert.True(doc.GetHeadingCount() >= 0);
    }

    [Fact]
    public void GetHeadingCount_Zero_ForNoHeadingDoc()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Just a paragraph, no headings.");
        Assert.Equal(0, doc.GetHeadingCount());
    }

    [Fact]
    public void GetHeadingCount_Positive_AfterInsertHeading()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Main Title", 1);
        Assert.True(doc.GetHeadingCount() > 0);
    }

    [Fact]
    public void GetHeadingCount_Consistent()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Title", 1);
        doc.InsertHeading(1, "Section", 2);
        Assert.Equal(doc.GetHeadingCount(), doc.GetHeadingCount());
    }

    [Fact]
    public void GetHeadingCount_SaveLoad_Consistent()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Title", 1);
        doc.InsertHeading(1, "Section A", 2);
        doc.InsertHeading(2, "Section B", 2);
        var before = doc.GetHeadingCount();
        var path = TempFile("hc_save.fodt");
        doc.SaveToFile(path);
        var loaded = FodtDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetHeadingCount());
    }

    [Fact]
    public void GetHeadingCount_Increases_PerHeadingInserted()
    {
        var doc = FodtDocument.CreateEmpty();
        var c0 = doc.GetHeadingCount();
        doc.InsertHeading(0, "Title", 1);
        var c1 = doc.GetHeadingCount();
        doc.InsertHeading(1, "Section", 2);
        var c2 = doc.GetHeadingCount();
        Assert.True(c1 > c0);
        Assert.True(c2 > c1);
    }

    // -------------------------------------------------------------------------
    // GetListCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetListCount_NoThrow()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Some text.");
        var ex = Record.Exception(() => doc.GetListCount());
        Assert.Null(ex);
    }

    [Fact]
    public void GetListCount_NonNegative()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Some text.");
        Assert.True(doc.GetListCount() >= 0);
    }

    [Fact]
    public void GetListCount_Consistent()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Some text.");
        Assert.Equal(doc.GetListCount(), doc.GetListCount());
    }

    [Fact]
    public void GetListCount_SaveLoad_Consistent()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Report", 1);
        doc.AppendParagraph("Introduction paragraph.");
        var before = doc.GetListCount();
        var path = TempFile("lc_save.fodt");
        doc.SaveToFile(path);
        var loaded = FodtDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetListCount());
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetHeadingCount_GetListCount_Pipeline()
    {
        // Government — HM Treasury: Autumn Statement 2024 Document Analysis
        // Structural analysis of the official Autumn Statement for document indexing
        // Heading count drives chapter-level navigation; list count drives policy measure extraction

        var doc = FodtDocument.CreateEmpty();

        // Cover section
        doc.InsertHeading(0, "Autumn Statement 2024", 1);
        doc.AppendParagraph("Presented to Parliament by the Chancellor of the Exchequer by Command of His Majesty. November 2024. CP 1234.");

        var hc1 = doc.GetHeadingCount();
        Assert.Equal(1, hc1);
        var lc1 = doc.GetListCount();
        Assert.True(lc1 >= 0);

        // Chapter 1
        doc.InsertHeading(1, "Chapter 1: Economic Context and Forecasts", 1);
        doc.InsertHeading(2, "1.1 Global Economic Outlook", 2);
        doc.AppendParagraph("Global growth is forecast to remain subdued in 2025. The IMF projects world GDP growth of 3.1 per cent, unchanged from 2024. Advanced economy growth continues to be restrained by the lagged effects of monetary tightening and elevated energy costs.");
        doc.InsertHeading(3, "1.2 UK Economic Forecast", 2);
        doc.AppendParagraph("The OBR forecasts UK GDP growth of 1.1 per cent in 2025, rising to 1.8 per cent by 2027 as the impact of prior interest rate increases fades. CPI inflation is expected to fall to 2.5 per cent by end-2025, converging toward the 2 per cent target in 2026.");

        var hc2 = doc.GetHeadingCount();
        Assert.True(hc2 > hc1); // more headings added
        Assert.Equal(hc2, doc.GetHeadingCount()); // consistent

        // Chapter 2
        doc.InsertHeading(4, "Chapter 2: Fiscal Policy and Spending Review", 1);
        doc.InsertHeading(5, "2.1 Fiscal Rules", 2);
        doc.AppendParagraph("The Government remains committed to its fiscal rules: the current budget must be in balance or surplus in 2029-30, and underlying public sector net debt must be falling as a share of GDP by the same year.");
        doc.InsertHeading(6, "2.2 Departmental Resource Allocation", 2);
        doc.AppendParagraph("Resource Departmental Expenditure Limits (RDEL) for 2025-26 to 2029-30 are set out in Table 2.1. Total RDEL grows from £481.6 billion in 2025-26 to £532.8 billion in 2029-30, representing average annual real-terms growth of 1.3 per cent.");
        doc.InsertHeading(7, "2.3 Capital Investment Programme", 2);
        doc.AppendParagraph("Capital Departmental Expenditure Limits (CDEL) total £127.4 billion in 2025-26, rising to £141.2 billion by 2029-30. Priorities include hospital rebuilding, transport infrastructure, and defence capital.");

        var hc3 = doc.GetHeadingCount();
        Assert.True(hc3 > hc2);

        // Chapter 3 with sub-sections
        doc.InsertHeading(8, "Chapter 3: Tax Measures", 1);
        doc.InsertHeading(9, "3.1 Income Tax and National Insurance", 2);
        doc.InsertHeading(10, "3.2 Corporation Tax", 2);
        doc.InsertHeading(11, "3.3 Business Rates", 2);
        doc.InsertHeading(12, "3.4 Stamp Duty Land Tax", 2);
        doc.AppendParagraph("The Government is extending the temporary business rates relief for the retail, hospitality, and leisure sector. The small business multiplier is frozen for the fifth consecutive year. The empty property relief threshold is maintained.");

        var hcFinal = doc.GetHeadingCount();
        Assert.True(hcFinal > hc3);
        Assert.True(hcFinal >= 10); // at least 10 headings across all chapters

        // List count
        var lcFinal = doc.GetListCount();
        Assert.True(lcFinal >= 0);
        Assert.Equal(lcFinal, doc.GetListCount()); // consistent

        // Basic document checks
        Assert.True(doc.GetWordCount() > 0);
        Assert.True(doc.GetParagraphCount() > 0);
        Assert.True(doc.GetCharCount() > 0);

        // ExportToHtml
        var html = doc.ExportToHtml();
        Assert.NotNull(html);
        Assert.NotEmpty(html);

        // SaveToFile
        var path1 = TempFile("hmt_autumn_statement_2024.fodt");
        doc.SaveToFile(path1);
        Assert.True(File.Exists(path1));
        Assert.True(new FileInfo(path1).Length > 0);

        // LoadFile and verify
        var loaded = FodtDocument.LoadFile(path1);
        Assert.Equal(hcFinal, loaded.GetHeadingCount());
        Assert.Equal(lcFinal, loaded.GetListCount());
        Assert.Equal(doc.GetWordCount(), loaded.GetWordCount());
        Assert.Equal(doc.GetParagraphCount(), loaded.GetParagraphCount());

        // Extend with appendix headings
        loaded.InsertHeading(13, "Annex A: Data Tables", 1);
        loaded.InsertHeading(14, "Table A.1 — GDP Growth Projections", 2);
        loaded.InsertHeading(15, "Table A.2 — Fiscal Forecasts", 2);

        var hcAfterAppendix = loaded.GetHeadingCount();
        Assert.True(hcAfterAppendix > hcFinal);

        // Final save
        var path2 = TempFile("hmt_autumn_statement_2024_final.fodt");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var final = FodtDocument.LoadFile(path2);
        Assert.Equal(hcAfterAppendix, final.GetHeadingCount());
        Assert.Equal(loaded.GetListCount(), final.GetListCount());

        Assert.True(final.GetWordCount() > doc.GetWordCount());

        var ex1 = Record.Exception(() => final.GetHeadingCount());
        var ex2 = Record.Exception(() => final.GetListCount());
        Assert.Null(ex1);
        Assert.Null(ex2);
    }
}
