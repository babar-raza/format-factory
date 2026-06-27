// Tests for FodtDocument.GetSentenceCount, GetAverageSentenceLength deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODT-R387

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R387: Tests for FodtDocument.GetSentenceCount, GetAverageSentenceLength deeper.
/// GetSentenceCount(): returns the total number of sentences in the document.
/// GetAverageSentenceLength(): returns the mean number of words per sentence.
/// Covers: GetSentenceCount no-throw; GetSentenceCount non-negative; GetSentenceCount positive for non-empty;
/// GetSentenceCount consistent; GetSentenceCount increases after AppendParagraph;
/// GetSentenceCount save-load; GetAverageSentenceLength no-throw; GetAverageSentenceLength non-negative;
/// GetAverageSentenceLength consistent; GetAverageSentenceLength save-load;
/// GetAverageSentenceLength increases with longer sentences; dogfood pipeline.
/// </summary>
public class FodtR387GetSentenceCountAndAverageSentenceLengthDeepTests : IDisposable
{
    private readonly string _tempDir;

    public FodtR387GetSentenceCountAndAverageSentenceLengthDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodtR387_" + Guid.NewGuid().ToString("N"));
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
        doc.InsertHeading(0, "Corporate Governance Report", 1);
        doc.AppendParagraph("The board of directors met quarterly to review performance. Attendance was high across all committees. Minutes were recorded and circulated promptly.");
        doc.AppendParagraph("Risk management procedures were strengthened during the year. The audit committee commissioned an independent review. Findings were presented to the full board in November.");
        return doc;
    }

    private static FodtDocument CreateShortSentenceDoc()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Rain fell. Wind blew. Cold air arrived.");
        return doc;
    }

    private static FodtDocument CreateLongSentenceDoc()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("The Financial Conduct Authority published its annual report on the state of retail investment markets, highlighting significant disparities in consumer outcomes across different distribution channels and product categories, with particular concern expressed regarding the persistence of high-cost credit products in vulnerable communities.");
        doc.AppendParagraph("The Prudential Regulation Authority's stress testing framework requires participating banks to demonstrate resilience against a severe but plausible macroeconomic scenario, including a sharp contraction in GDP, a significant rise in unemployment, and a sustained period of negative interest rates across the major advanced economies.");
        return doc;
    }

    // -------------------------------------------------------------------------
    // GetSentenceCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetSentenceCount_NoThrow()
    {
        var doc = CreateRichDoc();
        var ex = Record.Exception(() => doc.GetSentenceCount());
        Assert.Null(ex);
    }

    [Fact]
    public void GetSentenceCount_NonNegative()
    {
        var doc = CreateRichDoc();
        Assert.True(doc.GetSentenceCount() >= 0);
    }

    [Fact]
    public void GetSentenceCount_Positive_ForNonEmptyDoc()
    {
        var doc = CreateRichDoc();
        Assert.True(doc.GetSentenceCount() > 0);
    }

    [Fact]
    public void GetSentenceCount_Consistent()
    {
        var doc = CreateRichDoc();
        Assert.Equal(doc.GetSentenceCount(), doc.GetSentenceCount());
    }

    [Fact]
    public void GetSentenceCount_Increases_After_AppendParagraph()
    {
        var doc = CreateRichDoc();
        var before = doc.GetSentenceCount();
        doc.AppendParagraph("A new sentence was added. Another sentence followed immediately.");
        Assert.True(doc.GetSentenceCount() > before);
    }

    [Fact]
    public void GetSentenceCount_SaveLoad_Consistent()
    {
        var doc = CreateRichDoc();
        var before = doc.GetSentenceCount();
        var path = TempFile("sc_save.fodt");
        doc.SaveToFile(path);
        var loaded = FodtDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetSentenceCount());
    }

    // -------------------------------------------------------------------------
    // GetAverageSentenceLength
    // -------------------------------------------------------------------------

    [Fact]
    public void GetAverageSentenceLength_NoThrow()
    {
        var doc = CreateRichDoc();
        var ex = Record.Exception(() => doc.GetAverageSentenceLength());
        Assert.Null(ex);
    }

    [Fact]
    public void GetAverageSentenceLength_NonNegative()
    {
        var doc = CreateRichDoc();
        Assert.True(doc.GetAverageSentenceLength() >= 0.0);
    }

    [Fact]
    public void GetAverageSentenceLength_Consistent()
    {
        var doc = CreateRichDoc();
        Assert.Equal(doc.GetAverageSentenceLength(), doc.GetAverageSentenceLength());
    }

    [Fact]
    public void GetAverageSentenceLength_SaveLoad_Consistent()
    {
        var doc = CreateRichDoc();
        var before = doc.GetAverageSentenceLength();
        var path = TempFile("asl_save.fodt");
        doc.SaveToFile(path);
        var loaded = FodtDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetAverageSentenceLength(), precision: 6);
    }

    [Fact]
    public void GetAverageSentenceLength_LargerForLongSentenceDoc()
    {
        var shortDoc = CreateShortSentenceDoc();
        var longDoc = CreateLongSentenceDoc();
        Assert.True(longDoc.GetAverageSentenceLength() > shortDoc.GetAverageSentenceLength());
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetSentenceCount_GetAverageSentenceLength_Pipeline()
    {
        // Legal — Competition and Markets Authority (CMA): Phase 2 Inquiry Report
        // Stylometric analysis of merger inquiry reports for readability and complexity benchmarking
        // Sentence count and average sentence length quantify legal writing density

        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "CMA Phase 2 Inquiry — Microsoft/Activision Blizzard: Final Report Summary", 1);

        // Chapter 1: Introduction (short, plain sentences)
        doc.InsertSection("Chapter 1: Introduction");
        doc.InsertHeading(1, "1.1 Overview", 2);
        doc.AppendParagraph("The Competition and Markets Authority (CMA) conducted a Phase 2 inquiry into the anticipated acquisition of Activision Blizzard Inc by Microsoft Corporation. The inquiry was launched on 1 September 2022. The inquiry group comprised five members appointed by the CMA Panel.");
        doc.AppendParagraph("The transaction raised concerns in the cloud gaming market. The CMA assessed the competitive effects of the merger. A final report was issued in April 2023.");

        var sc1 = doc.GetSentenceCount();
        Assert.True(sc1 > 0);
        var asl1 = doc.GetAverageSentenceLength();
        Assert.True(asl1 >= 0.0);

        // Chapter 2: Theory of Harm (complex legal sentences)
        doc.InsertSection("Chapter 2: Theory of Harm");
        doc.InsertHeading(2, "2.1 Cloud Gaming Market", 2);
        doc.AppendParagraph("The CMA identified a realistic prospect that the merged entity would have the ability and incentive to foreclose rival multi-game subscription services and cloud gaming platforms by withholding or degrading access to Activision Blizzard's content, including its flagship Call of Duty franchise, which currently accounts for a disproportionate share of consumer engagement and spend in the relevant markets.");
        doc.AppendParagraph("In reaching this conclusion, the inquiry group considered a wide range of evidence, including internal documents produced by Microsoft and Activision Blizzard, responses to the CMA's information requests from third parties including platform operators, publishers, and consumer groups, as well as econometric and market share analysis conducted by the CMA's economics team and external advisers retained for the purpose of the inquiry.");

        var sc2 = doc.GetSentenceCount();
        Assert.True(sc2 > sc1); // more sentences after new chapters
        var asl2 = doc.GetAverageSentenceLength();
        Assert.True(asl2 >= 0.0);
        Assert.Equal(sc2, doc.GetSentenceCount()); // consistent

        // Chapter 3: Remedies
        doc.InsertSection("Chapter 3: Remedies");
        doc.InsertHeading(3, "3.1 Behavioural Undertakings", 2);
        doc.AppendParagraph("Microsoft offered behavioural remedies in the form of ten-year licensing agreements with competing cloud gaming providers. The CMA considered whether these remedies were sufficient to address the identified concerns. It concluded that they were not capable of being monitored and enforced effectively.");
        doc.AppendParagraph("The CMA therefore provisionally found that the merger should be prohibited. Microsoft subsequently offered a restructured transaction that excluded cloud streaming rights for Activision games outside the EEA. The CMA accepted this remedy as sufficient to address the competition concern in cloud gaming.");

        var sc3 = doc.GetSentenceCount();
        Assert.True(sc3 > sc2);
        Assert.True(sc3 <= doc.GetWordCount()); // sentences never exceed words

        // Average sentence length check
        var aslFinal = doc.GetAverageSentenceLength();
        Assert.True(aslFinal >= 0.0);
        Assert.Equal(aslFinal, doc.GetAverageSentenceLength()); // consistent

        // Basic document checks
        Assert.True(doc.GetWordCount() > 0);
        Assert.True(doc.GetParagraphCount() > 0);
        Assert.True(doc.GetCharCount() > 0);

        // ExportToHtml
        var html = doc.ExportToHtml();
        Assert.NotNull(html);
        Assert.NotEmpty(html);

        // SaveToFile
        var path1 = TempFile("cma_activision_report.fodt");
        doc.SaveToFile(path1);
        Assert.True(File.Exists(path1));
        Assert.True(new FileInfo(path1).Length > 0);

        // LoadFile and verify
        var loaded = FodtDocument.LoadFile(path1);
        Assert.Equal(sc3, loaded.GetSentenceCount());
        Assert.Equal(aslFinal, loaded.GetAverageSentenceLength(), precision: 6);
        Assert.Equal(doc.GetWordCount(), loaded.GetWordCount());
        Assert.Equal(doc.GetParagraphCount(), loaded.GetParagraphCount());

        // Extend with appendix (short, bullet-style sentences)
        loaded.InsertSection("Appendix A: Participating Undertakings");
        loaded.AppendParagraph("Microsoft Corporation. Activision Blizzard Inc. King Digital Entertainment. Blizzard Entertainment SAS.");

        var scAfterAppendix = loaded.GetSentenceCount();
        Assert.True(scAfterAppendix > sc3); // more sentences

        // Final save
        var path2 = TempFile("cma_activision_report_final.fodt");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var final = FodtDocument.LoadFile(path2);
        Assert.Equal(scAfterAppendix, final.GetSentenceCount());
        Assert.Equal(loaded.GetAverageSentenceLength(), final.GetAverageSentenceLength(), precision: 6);

        Assert.True(final.GetWordCount() > doc.GetWordCount());

        var ex1 = Record.Exception(() => final.GetSentenceCount());
        var ex2 = Record.Exception(() => final.GetAverageSentenceLength());
        Assert.Null(ex1);
        Assert.Null(ex2);
    }
}
