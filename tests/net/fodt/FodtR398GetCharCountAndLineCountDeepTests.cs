// Tests for FodtDocument.GetCharCount, GetLineCount deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODT-R398

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R398: Tests for FodtDocument.GetCharCount, GetLineCount deeper.
/// GetCharCount(): returns the total character count of all text in the document.
/// GetLineCount(): returns the total number of text lines (paragraphs or hard line breaks).
/// Covers: GetCharCount no-throw; GetCharCount positive for non-empty doc; GetCharCount non-negative;
/// GetCharCount consistent; GetCharCount increases after AppendParagraph; GetCharCount save-load;
/// GetLineCount no-throw; GetLineCount non-negative; GetLineCount positive for non-empty doc;
/// GetLineCount consistent; GetLineCount increases after AppendParagraph; GetLineCount save-load;
/// dogfood pipeline.
/// </summary>
public class FodtR398GetCharCountAndLineCountDeepTests : IDisposable
{
    private readonly string _tempDir;

    public FodtR398GetCharCountAndLineCountDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodtR398_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private static FodtDocument CreateRichDoc()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Annual Report Summary", 1);
        doc.AppendParagraph("This report summarises the key financial and operational performance indicators for the fiscal year ending 31 March 2024.");
        doc.AppendParagraph("Revenue grew by twelve percent year-on-year, driven by increased demand across all three product segments and strong performance in emerging markets.");
        doc.AppendParagraph("The board approved a final dividend of fourteen pence per share, reflecting confidence in the company's long-term growth strategy.");
        return doc;
    }

    // -------------------------------------------------------------------------
    // GetCharCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCharCount_NoThrow()
    {
        var doc = CreateRichDoc();
        var ex = Record.Exception(() => doc.GetCharCount());
        Assert.Null(ex);
    }

    [Fact]
    public void GetCharCount_Positive_ForNonEmptyDoc()
    {
        var doc = CreateRichDoc();
        Assert.True(doc.GetCharCount() > 0);
    }

    [Fact]
    public void GetCharCount_NonNegative()
    {
        var doc = FodtDocument.CreateEmpty();
        Assert.True(doc.GetCharCount() >= 0);
    }

    [Fact]
    public void GetCharCount_Consistent()
    {
        var doc = CreateRichDoc();
        Assert.Equal(doc.GetCharCount(), doc.GetCharCount());
    }

    [Fact]
    public void GetCharCount_Increases_After_AppendParagraph()
    {
        var doc = CreateRichDoc();
        var before = doc.GetCharCount();
        doc.AppendParagraph("An additional paragraph adds more characters to the total count.");
        Assert.True(doc.GetCharCount() > before);
    }

    [Fact]
    public void GetCharCount_SaveLoad_Consistent()
    {
        var doc = CreateRichDoc();
        var before = doc.GetCharCount();
        var path = TempFile("cc_save.fodt");
        doc.SaveToFile(path);
        var loaded = FodtDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetCharCount());
    }

    // -------------------------------------------------------------------------
    // GetLineCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetLineCount_NoThrow()
    {
        var doc = CreateRichDoc();
        var ex = Record.Exception(() => doc.GetLineCount());
        Assert.Null(ex);
    }

    [Fact]
    public void GetLineCount_NonNegative()
    {
        var doc = FodtDocument.CreateEmpty();
        Assert.True(doc.GetLineCount() >= 0);
    }

    [Fact]
    public void GetLineCount_Positive_ForNonEmptyDoc()
    {
        var doc = CreateRichDoc();
        Assert.True(doc.GetLineCount() > 0);
    }

    [Fact]
    public void GetLineCount_Consistent()
    {
        var doc = CreateRichDoc();
        Assert.Equal(doc.GetLineCount(), doc.GetLineCount());
    }

    [Fact]
    public void GetLineCount_Increases_After_AppendParagraph()
    {
        var doc = CreateRichDoc();
        var before = doc.GetLineCount();
        doc.AppendParagraph("A new paragraph adds at least one new line.");
        Assert.True(doc.GetLineCount() > before);
    }

    [Fact]
    public void GetLineCount_SaveLoad_Consistent()
    {
        var doc = CreateRichDoc();
        var before = doc.GetLineCount();
        var path = TempFile("lc_save.fodt");
        doc.SaveToFile(path);
        var loaded = FodtDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetLineCount());
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetCharCount_GetLineCount_Pipeline()
    {
        // Regulatory — FCA / FRC: Annual Report and Accounts Review Programme
        // Reviewer tools use character count and line count to assess document density
        // and compliance with FCA Disclosure Guidance and Transparency Rules (DTR)

        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "FCA Annual Report Review — Regulatory Assessment Template", 1);

        // Part 1: Basis of assessment
        doc.InsertSection("Part 1: Basis of Assessment");
        doc.InsertHeading(1, "1.1 Regulatory Framework", 2);
        doc.AppendParagraph("This assessment is conducted under the FCA Disclosure Guidance and Transparency Rules (DTR) and the FRC's UK Corporate Governance Code 2018. Listed companies are required to include in their annual reports a fair review of the company's business and a description of the principal risks and uncertainties facing the company.");
        doc.AppendParagraph("The Taskforce on Climate-related Financial Disclosures (TCFD) requirements, made mandatory for premium listed companies from 1 January 2021, are assessed as part of this review. Compliance with the FCA's Environmental Social and Governance (ESG) disclosure rules is separately evaluated.");

        var cc1 = doc.GetCharCount();
        var lc1 = doc.GetLineCount();
        Assert.True(cc1 > 0);
        Assert.True(lc1 > 0);

        // Part 2: Strategic report assessment
        doc.InsertSection("Part 2: Strategic Report");
        doc.InsertHeading(2, "2.1 Business Model Disclosure", 2);
        doc.AppendParagraph("The strategic report is required to include a description of the company's business model as required by the Companies Act 2006 section 414C. The assessment evaluates whether the business model description is sufficiently detailed to allow shareholders and stakeholders to understand the sources of value creation and the key drivers of long-term success.");
        doc.AppendParagraph("Section 172 statements, mandatory under the Companies (Miscellaneous Reporting) Regulations 2018, are assessed for completeness and evidential quality. Reviewers assess whether the board has given adequate consideration to the interests of employees, suppliers, customers, and the wider community.");
        doc.AppendParagraph("Going concern and viability statements are assessed against FRC guidance published in October 2020. The viability period declared must be consistent with the company's strategic planning horizon and supported by stress-testing assumptions that are clearly described and reasonable.");

        var cc2 = doc.GetCharCount();
        var lc2 = doc.GetLineCount();
        Assert.True(cc2 > cc1);
        Assert.True(lc2 > lc1);
        Assert.Equal(cc2, doc.GetCharCount()); // consistent
        Assert.Equal(lc2, doc.GetLineCount()); // consistent

        // Part 3: Governance and remuneration
        doc.InsertSection("Part 3: Corporate Governance");
        doc.InsertHeading(3, "3.1 Board Composition and Independence", 2);
        doc.AppendParagraph("The board composition is assessed against the UK Corporate Governance Code Provision 11, which requires that at least half the board, excluding the chair, should be non-executive directors the board considers to be independent. Deviations from this requirement must be explained under the comply-or-explain principle.");
        doc.InsertHeading(4, "3.2 Audit Committee Effectiveness", 2);
        doc.AppendParagraph("The audit committee report is reviewed for compliance with DTR 7.1 and Code Provision 26. The review assesses the committee's oversight of the external audit process, the robustness of significant accounting judgements, and the adequacy of internal controls reporting.");
        doc.AppendParagraph("Remuneration disclosures are assessed under the Directors' Remuneration Reporting Regulations 2013, as amended. The review evaluates whether pay outcomes are aligned with performance and whether the policy table complies with the statutory format requirements.");

        var cc3 = doc.GetCharCount();
        var lc3 = doc.GetLineCount();
        Assert.True(cc3 > cc2);
        Assert.True(lc3 > lc2);

        // Basic document integrity
        Assert.True(doc.GetWordCount() > 0);
        Assert.True(doc.GetParagraphCount() > 0);
        // Char count should be larger than word count (words < chars due to spaces)
        Assert.True(cc3 > doc.GetWordCount());

        // ExportToHtml
        var html = doc.ExportToHtml();
        Assert.NotNull(html);
        Assert.NotEmpty(html);

        // SaveToFile
        var path1 = TempFile("fca_frc_review_template.fodt");
        doc.SaveToFile(path1);
        Assert.True(File.Exists(path1));
        Assert.True(new FileInfo(path1).Length > 0);

        // LoadFile and verify
        var loaded = FodtDocument.LoadFile(path1);
        Assert.Equal(cc3, loaded.GetCharCount());
        Assert.Equal(lc3, loaded.GetLineCount());
        Assert.Equal(doc.GetWordCount(), loaded.GetWordCount());
        Assert.Equal(doc.GetParagraphCount(), loaded.GetParagraphCount());

        // Extend with appendix
        loaded.InsertSection("Appendix: Reviewer Checklist");
        loaded.AppendParagraph("DTR 7.1 audit committee composition: PASS. FRC Code Provision 11 board independence: PASS. TCFD compliance: PARTIAL — scenario analysis section requires enhancement. Going concern statement: PASS.");

        var ccFinal = loaded.GetCharCount();
        var lcFinal = loaded.GetLineCount();
        Assert.True(ccFinal > cc3);
        Assert.True(lcFinal > lc3);

        var path2 = TempFile("fca_frc_review_with_appendix.fodt");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var final = FodtDocument.LoadFile(path2);
        Assert.Equal(ccFinal, final.GetCharCount());
        Assert.Equal(lcFinal, final.GetLineCount());

        Assert.True(final.GetWordCount() > doc.GetWordCount());

        var ex1 = Record.Exception(() => final.GetCharCount());
        var ex2 = Record.Exception(() => final.GetLineCount());
        Assert.Null(ex1);
        Assert.Null(ex2);
    }
}
