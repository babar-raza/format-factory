// Tests for FodtDocument.GetHeaderText, SetHeaderText deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODT-R360

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R360: Tests for FodtDocument.GetHeaderText, SetHeaderText deeper.
/// GetHeaderText(): returns the current header text of the document.
/// SetHeaderText(text): sets the document header text.
/// Covers: GetHeaderText no-throw; GetHeaderText non-null; GetHeaderText consistent;
/// GetHeaderText save-load; SetHeaderText no-throw;
/// SetHeaderText then GetHeaderText updated; SetHeaderText then GetParagraphCount unchanged;
/// SetHeaderText then ExportToHtml no-throw; SetHeaderText then ExportToMarkdown no-throw;
/// SetHeaderText save-load; SetHeaderText override;
/// SetHeaderText then GetWordCount positive;
/// dogfood CreateDoc→SetHeaderText→GetHeaderText→SaveToFile pipeline.
/// </summary>
public class FodtR360GetHeaderTextAndSetHeaderTextDeepTests : IDisposable
{
    private readonly string _tempDir;

    public FodtR360GetHeaderTextAndSetHeaderTextDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodtR360_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private static FodtDocument CreatePlainDoc()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Consultation Response: Proposed Changes to UK Immigration Rules", 1);
        doc.AppendParagraph("This consultation response is submitted on behalf of the Immigration Law Practitioners Association (ILPA) in respect of the Home Office's proposed amendments to the Immigration Rules, Statement of Changes HC 590.");
        doc.AppendParagraph("ILPA represents immigration law practitioners across the United Kingdom and has over 1,000 individual and organisational members including barristers, solicitors, and legal advisers.");
        doc.AppendParagraph("The proposed changes to the Skilled Worker route introduce significant modifications to the salary thresholds, occupation codes, and shortage occupation provisions that will affect both employers and migrants.");
        return doc;
    }

    // -------------------------------------------------------------------------
    // GetHeaderText
    // -------------------------------------------------------------------------

    [Fact]
    public void GetHeaderText_NoThrow()
    {
        var doc = CreatePlainDoc();
        var ex = Record.Exception(() => doc.GetHeaderText());
        Assert.Null(ex);
    }

    [Fact]
    public void GetHeaderText_NonNull()
    {
        var doc = CreatePlainDoc();
        Assert.NotNull(doc.GetHeaderText());
    }

    [Fact]
    public void GetHeaderText_Consistent()
    {
        var doc = CreatePlainDoc();
        Assert.Equal(doc.GetHeaderText(), doc.GetHeaderText());
    }

    [Fact]
    public void GetHeaderText_SaveLoad_Consistent()
    {
        var doc = CreatePlainDoc();
        doc.SetHeaderText("ILPA Consultation Response — HC 590");
        var before = doc.GetHeaderText();
        var path = TempFile("ght_save.fodt");
        doc.SaveToFile(path);
        var loaded = FodtDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetHeaderText());
    }

    // -------------------------------------------------------------------------
    // SetHeaderText
    // -------------------------------------------------------------------------

    [Fact]
    public void SetHeaderText_NoThrow()
    {
        var doc = CreatePlainDoc();
        var ex = Record.Exception(() => doc.SetHeaderText("Draft — Confidential"));
        Assert.Null(ex);
    }

    [Fact]
    public void SetHeaderText_Then_GetHeaderText_Updated()
    {
        var doc = CreatePlainDoc();
        doc.SetHeaderText("ILPA — HC 590 Response — June 2024");
        Assert.Equal("ILPA — HC 590 Response — June 2024", doc.GetHeaderText());
    }

    [Fact]
    public void SetHeaderText_Then_GetParagraphCount_Unchanged()
    {
        var doc = CreatePlainDoc();
        var before = doc.GetParagraphCount();
        doc.SetHeaderText("Draft v1.0");
        Assert.Equal(before, doc.GetParagraphCount());
    }

    [Fact]
    public void SetHeaderText_Then_ExportToHtml_NoThrow()
    {
        var doc = CreatePlainDoc();
        doc.SetHeaderText("Consultation Response");
        var ex = Record.Exception(() => doc.ExportToHtml());
        Assert.Null(ex);
    }

    [Fact]
    public void SetHeaderText_Then_ExportToMarkdown_NoThrow()
    {
        var doc = CreatePlainDoc();
        doc.SetHeaderText("Draft — Not for Distribution");
        var ex = Record.Exception(() => doc.ExportToMarkdown());
        Assert.Null(ex);
    }

    [Fact]
    public void SetHeaderText_SaveLoad_Persists()
    {
        var doc = CreatePlainDoc();
        doc.SetHeaderText("CONFIDENTIAL — DRAFT");
        var path = TempFile("sht_save.fodt");
        doc.SaveToFile(path);
        var loaded = FodtDocument.LoadFile(path);
        Assert.Equal("CONFIDENTIAL — DRAFT", loaded.GetHeaderText());
    }

    [Fact]
    public void SetHeaderText_Override()
    {
        var doc = CreatePlainDoc();
        doc.SetHeaderText("Version 1");
        doc.SetHeaderText("Version 2");
        Assert.Equal("Version 2", doc.GetHeaderText());
    }

    [Fact]
    public void SetHeaderText_Then_GetWordCount_Positive()
    {
        var doc = CreatePlainDoc();
        doc.SetHeaderText("Draft");
        Assert.True(doc.GetWordCount() > 0);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetHeaderText_SetHeaderText_SaveToFile_Pipeline()
    {
        // Academic — ESRC Research Grant Application: document header workflow
        // Full research council application lifecycle: draft → review → submitted → awarded
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "ESRC Standard Grant Application: Platform Economy and Worker Wellbeing in the UK Gig Economy", 1);
        doc.AppendParagraph("This application seeks funding from the Economic and Social Research Council (ESRC) for a three-year programme of research examining the relationship between algorithmic management practices in digital platform companies and the psychological wellbeing, financial security, and legal status of gig economy workers in the United Kingdom.");

        doc.InsertHeading(3, "Case for Support — Section A: Research Questions", 2);
        doc.AppendParagraph("The research addresses four interconnected questions: (1) How do algorithmic rating and dispatch systems affect the subjective experience of autonomy among gig workers? (2) What is the relationship between platform-mediated income volatility and financial insecurity? (3) To what extent do current UK employment law frameworks (post-Uber BV v Aslam [2021] UKSC 5) adequately protect platform workers? (4) What policy interventions would most effectively improve gig worker wellbeing?");
        doc.AppendParagraph("The research will employ a mixed-methods longitudinal design, combining administrative data from HMRC's Real Time Information system (with appropriate data sharing agreements) with qualitative interviews (n=80) and an experience sampling methodology study (n=200) conducted over 18 months.");

        doc.InsertHeading(3, "Section B: Research Environment", 2);
        doc.AppendParagraph("The proposed research will be conducted at the Institute for Employment Studies (IES), Brighton, in partnership with the University of Oxford's Oxford Internet Institute. The IES has a strong track record of ESRC-funded research in labour market policy, with over £8.2m in ESRC grants awarded in the past 10 years.");
        doc.AppendParagraph("The Principal Investigator, Professor Sarah Callingham, holds the ESRC-funded Business Engagement Fellowship and brings extensive experience in platform economy research, including the DWP-commissioned independent review of flexible working (2022) and the Trades Union Congress advisory panel on AI and employment (2023).");

        doc.InsertHeading(3, "Section C: Pathways to Impact", 2);
        doc.AppendParagraph("Impact will be delivered through three channels: (1) policy engagement with BEIS, DWP, and HMRC via the ESRC Policy Fellowship scheme; (2) sector engagement with the Trades Union Congress, GMB, and the Independent Workers Union of Great Britain; (3) academic dissemination via high-impact journals (BJIR, Work Employment and Society, ILR Review) and the IES conference programme.");

        Assert.Equal(6, doc.GetParagraphCount());

        // GetHeaderText — initially empty or default
        var initialHeader = doc.GetHeaderText();
        Assert.NotNull(initialHeader);
        Assert.Equal(doc.GetHeaderText(), doc.GetHeaderText()); // consistent

        // SetHeaderText — draft stage
        doc.SetHeaderText("DRAFT — ESRC Standard Grant Application | Not for Circulation");
        Assert.Equal("DRAFT — ESRC Standard Grant Application | Not for Circulation", doc.GetHeaderText());
        Assert.Equal(6, doc.GetParagraphCount()); // unchanged

        // ExportToHtml with header
        var html = doc.ExportToHtml();
        Assert.NotNull(html);
        Assert.NotEmpty(html);

        // ExportToMarkdown with header
        var md = doc.ExportToMarkdown();
        Assert.NotNull(md);
        Assert.NotEmpty(md);

        // GetWordCount positive
        Assert.True(doc.GetWordCount() > 0);
        Assert.True(doc.GetCharCount() > 0);

        // SaveToFile (draft)
        var path1 = TempFile("dogfood_esrc_draft.fodt");
        doc.SaveToFile(path1);
        Assert.True(File.Exists(path1));
        Assert.True(new FileInfo(path1).Length > 0);

        // LoadFile and verify header persists
        var draft = FodtDocument.LoadFile(path1);
        Assert.Equal("DRAFT — ESRC Standard Grant Application | Not for Circulation", draft.GetHeaderText());
        Assert.Equal(6, draft.GetParagraphCount());

        // SetHeaderText — peer review stage
        draft.SetHeaderText("UNDER PEER REVIEW — ESRC Standard Grant | ES/W012345/1");
        Assert.Equal("UNDER PEER REVIEW — ESRC Standard Grant | ES/W012345/1", draft.GetHeaderText());

        // AppendParagraph — impact summary added at review stage
        draft.AppendParagraph("User Advisory Group: the research will be guided by a User Advisory Group comprising representatives from Deliveroo, Uber UK, IWGB, TUC, BEIS Labour Markets Analytical Team, and the Low Pay Commission, ensuring co-production of impact pathways throughout the research lifecycle.");
        Assert.Equal(7, draft.GetParagraphCount());
        Assert.Equal("UNDER PEER REVIEW — ESRC Standard Grant | ES/W012345/1", draft.GetHeaderText());

        // SaveToFile (review stage)
        var path2 = TempFile("dogfood_esrc_review.fodt");
        draft.SaveToFile(path2);
        Assert.True(File.Exists(path2));

        // LoadFile review version
        var review = FodtDocument.LoadFile(path2);
        Assert.Equal("UNDER PEER REVIEW — ESRC Standard Grant | ES/W012345/1", review.GetHeaderText());
        Assert.Equal(7, review.GetParagraphCount());

        // SetHeaderText — award stage
        review.SetHeaderText("AWARDED — ES/W012345/1 — £487,250 — January 2025 — December 2027");
        Assert.Equal("AWARDED — ES/W012345/1 — £487,250 — January 2025 — December 2027", review.GetHeaderText());

        // Final save
        var path3 = TempFile("dogfood_esrc_awarded.fodt");
        review.SaveToFile(path3);
        Assert.True(File.Exists(path3));
        var awarded = FodtDocument.LoadFile(path3);
        Assert.Equal("AWARDED — ES/W012345/1 — £487,250 — January 2025 — December 2027", awarded.GetHeaderText());
        Assert.Equal(7, awarded.GetParagraphCount());

        var ex1 = Record.Exception(() => awarded.ExportToHtml());
        var ex2 = Record.Exception(() => awarded.ExportToMarkdown());
        var ex3 = Record.Exception(() => awarded.SetHeaderText("FINAL"));
        Assert.Null(ex1);
        Assert.Null(ex2);
        Assert.Null(ex3);
        Assert.Equal("FINAL", awarded.GetHeaderText());
    }
}
