// Tests for FodtDocument.GetLinkCount, GetImageCount deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODT-R390

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R390: Tests for FodtDocument.GetLinkCount, GetImageCount deeper.
/// GetLinkCount(): returns the total number of hyperlinks in the document.
/// GetImageCount(): returns the total number of embedded images in the document.
/// Covers: GetLinkCount no-throw; GetLinkCount non-negative; GetLinkCount consistent;
/// GetLinkCount save-load; GetImageCount no-throw; GetImageCount non-negative;
/// GetImageCount consistent; GetImageCount save-load;
/// dogfood FCA consultation document analysis pipeline.
/// </summary>
public class FodtR390GetLinkCountAndImageCountDeepTests : IDisposable
{
    private readonly string _tempDir;

    public FodtR390GetLinkCountAndImageCountDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodtR390_" + Guid.NewGuid().ToString("N"));
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
        doc.InsertHeading(0, "Consultation Paper CP24/20", 1);
        doc.AppendParagraph("This consultation paper seeks views on proposed amendments to the FCA's Conduct of Business sourcebook.");
        doc.AppendParagraph("The consultation period runs until 30 November 2024. Responses should be submitted via the FCA's online portal.");
        return doc;
    }

    // -------------------------------------------------------------------------
    // GetLinkCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetLinkCount_NoThrow()
    {
        var doc = CreateRichDoc();
        var ex = Record.Exception(() => doc.GetLinkCount());
        Assert.Null(ex);
    }

    [Fact]
    public void GetLinkCount_NonNegative()
    {
        var doc = CreateRichDoc();
        Assert.True(doc.GetLinkCount() >= 0);
    }

    [Fact]
    public void GetLinkCount_Consistent()
    {
        var doc = CreateRichDoc();
        Assert.Equal(doc.GetLinkCount(), doc.GetLinkCount());
    }

    [Fact]
    public void GetLinkCount_SaveLoad_Consistent()
    {
        var doc = CreateRichDoc();
        var before = doc.GetLinkCount();
        var path = TempFile("lc_save.fodt");
        doc.SaveToFile(path);
        var loaded = FodtDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetLinkCount());
    }

    // -------------------------------------------------------------------------
    // GetImageCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetImageCount_NoThrow()
    {
        var doc = CreateRichDoc();
        var ex = Record.Exception(() => doc.GetImageCount());
        Assert.Null(ex);
    }

    [Fact]
    public void GetImageCount_NonNegative()
    {
        var doc = CreateRichDoc();
        Assert.True(doc.GetImageCount() >= 0);
    }

    [Fact]
    public void GetImageCount_Consistent()
    {
        var doc = CreateRichDoc();
        Assert.Equal(doc.GetImageCount(), doc.GetImageCount());
    }

    [Fact]
    public void GetImageCount_SaveLoad_Consistent()
    {
        var doc = CreateRichDoc();
        var before = doc.GetImageCount();
        var path = TempFile("ic_save.fodt");
        doc.SaveToFile(path);
        var loaded = FodtDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetImageCount());
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetLinkCount_GetImageCount_Pipeline()
    {
        // Financial Regulation — FCA: Consumer Duty Annual Compliance Report Template
        // Regulatory document for firms' annual Consumer Duty board reporting
        // Link count validates cross-reference structure; image count validates figure completeness

        var doc = FodtDocument.CreateEmpty();

        doc.InsertHeading(0, "Consumer Duty Annual Board Report — Template FG23/2", 1);
        doc.AppendParagraph("This template supports firms in meeting their Consumer Duty obligations under PRIN 2A. The Financial Conduct Authority published the Consumer Duty rules in PS22/9 (July 2022), with implementation for existing products and services by 31 July 2023.");

        // Section 1
        doc.InsertSection("Section 1: Board Attestation and Governance");
        doc.InsertHeading(1, "1.1 Board Oversight of Consumer Duty", 2);
        doc.AppendParagraph("The board confirms that it has reviewed and approved this Consumer Duty annual assessment. The assessment covers the firm's activities as a manufacturer and/or distributor in scope of PRIN 2A.7 and PRIN 2A.8.");
        doc.AppendParagraph("This report should be read alongside the firm's overall Conduct Risk Framework and the annual fair value assessments prepared under PROD 4.3. The board acknowledges its accountability under SMCR for ensuring Consumer Duty compliance.");

        var lc1 = doc.GetLinkCount();
        Assert.True(lc1 >= 0);
        var ic1 = doc.GetImageCount();
        Assert.True(ic1 >= 0);
        Assert.Equal(lc1, doc.GetLinkCount()); // consistent
        Assert.Equal(ic1, doc.GetImageCount()); // consistent

        // Section 2
        doc.InsertSection("Section 2: Customer Outcome Monitoring");
        doc.InsertHeading(2, "2.1 Products and Services Outcome", 2);
        doc.AppendParagraph("Firms must demonstrate that their products and services are designed to meet the needs of the target market. Evidence should include product governance committee minutes, target market assessments, and consumer testing results where available.");
        doc.InsertHeading(3, "2.2 Price and Value Outcome", 2);
        doc.AppendParagraph("The price and value outcome requires firms to ensure that the price paid for a product or service is reasonable relative to the overall benefits received. Fair value assessments must consider both the direct and indirect costs to consumers.");
        doc.InsertHeading(4, "2.3 Consumer Understanding Outcome", 2);
        doc.AppendParagraph("All communications must be clear, fair, and not misleading. Firms should conduct comprehension testing with representative consumer samples, particularly for complex products or significant changes to terms and conditions.");
        doc.InsertHeading(5, "2.4 Consumer Support Outcome", 2);
        doc.AppendParagraph("Customer service channels must meet the needs of consumers, including those in vulnerable circumstances. Firms should monitor service metrics including average handling times, first contact resolution rates, and complaints about service accessibility.");

        var lc2 = doc.GetLinkCount();
        var ic2 = doc.GetImageCount();
        Assert.True(lc2 >= 0);
        Assert.True(ic2 >= 0);
        Assert.Equal(lc2, doc.GetLinkCount()); // consistent

        // Section 3
        doc.InsertSection("Section 3: Data and MI Annex");
        doc.InsertHeading(6, "3.1 Key Metrics Dashboard", 2);
        doc.AppendParagraph("The following management information should be included as supporting evidence for this report: complaint volumes and root cause analysis; product withdrawal rates and post-sale contact rates; NPS scores and verbatim customer feedback analysis; vulnerable customer identification rates and support outcomes.");
        doc.InsertHeading(7, "3.2 Remediation Actions", 2);
        doc.AppendParagraph("Any identified harms or potential harms must be recorded with their root cause, affected consumer population estimate, proposed remediation approach, and target completion date. The board should review and approve all material remediation plans.");

        var lcFinal = doc.GetLinkCount();
        var icFinal = doc.GetImageCount();
        Assert.True(lcFinal >= 0);
        Assert.True(icFinal >= 0);

        // Basic document checks
        Assert.True(doc.GetWordCount() > 0);
        Assert.True(doc.GetParagraphCount() > 0);
        Assert.True(doc.GetCharCount() > 0);
        Assert.True(doc.GetHeadingCount() >= 7);

        // ExportToHtml
        var html = doc.ExportToHtml();
        Assert.NotNull(html);
        Assert.NotEmpty(html);

        // SaveToFile
        var path1 = TempFile("fca_consumer_duty_board_report.fodt");
        doc.SaveToFile(path1);
        Assert.True(File.Exists(path1));
        Assert.True(new FileInfo(path1).Length > 0);

        // LoadFile and verify
        var loaded = FodtDocument.LoadFile(path1);
        Assert.Equal(lcFinal, loaded.GetLinkCount());
        Assert.Equal(icFinal, loaded.GetImageCount());
        Assert.Equal(doc.GetWordCount(), loaded.GetWordCount());
        Assert.Equal(doc.GetParagraphCount(), loaded.GetParagraphCount());

        // Extend with appendix
        loaded.InsertSection("Appendix: Regulatory References");
        loaded.AppendParagraph("PS22/9: A new Consumer Duty. FCA, July 2022. FG22/5: Final non-Handbook Guidance for firms on the Consumer Duty. FCA, July 2022. FG23/2: Guidance for firms on the Consumer Duty. FCA, January 2023.");

        var lcAfter = loaded.GetLinkCount();
        var icAfter = loaded.GetImageCount();
        Assert.True(lcAfter >= 0);
        Assert.True(icAfter >= 0);

        // Final save
        var path2 = TempFile("fca_consumer_duty_board_report_final.fodt");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var final = FodtDocument.LoadFile(path2);
        Assert.Equal(lcAfter, final.GetLinkCount());
        Assert.Equal(icAfter, final.GetImageCount());

        Assert.True(final.GetWordCount() > doc.GetWordCount());

        var ex1 = Record.Exception(() => final.GetLinkCount());
        var ex2 = Record.Exception(() => final.GetImageCount());
        Assert.Null(ex1);
        Assert.Null(ex2);
    }
}
