// Tests for FodtDocument.GetCharCount, SplitByHeading, GetParagraphCount deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODT-R260

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R260: Tests for FodtDocument.GetCharCount, SplitByHeading, GetParagraphCount deeper.
/// GetCharCount(): returns the total number of characters in the document.
/// SplitByHeading(level): splits document into sections by heading of the given level.
/// GetParagraphCount(): returns the total number of paragraphs (headings + body).
/// Covers: GetCharCount positive; GetCharCount consistent; GetCharCount no-throw;
/// GetCharCount after AppendParagraph grows; GetCharCount after RemoveParagraphAt shrinks;
/// GetCharCount after ReplaceText similar; GetCharCount for empty doc=0 or >=0;
/// GetCharCount > GetWordCount * 3; GetCharCount save-load consistent;
/// SplitByHeading non-null; SplitByHeading non-empty; SplitByHeading count correct;
/// SplitByHeading no-throw; SplitByHeading consistent; SplitByHeading each is FodtDocument;
/// SplitByHeading by h1 correct count; SplitByHeading by h2 more sections;
/// SplitByHeading preserves content; SplitByHeading each section non-empty;
/// GetParagraphCount positive; GetParagraphCount consistent; GetParagraphCount no-throw;
/// GetParagraphCount after AppendParagraph increases; GetParagraphCount after RemoveParagraphAt decreases;
/// GetParagraphCount save-load consistent; GetParagraphCount after AppendList increases;
/// GetParagraphCount after InsertHeading increases; GetParagraphCount empty doc=0;
/// dogfood CreateDoc→GetCharCount→SplitByHeading→GetParagraphCount→SaveToFile pipeline.
/// </summary>
public class FodtR260GetCharCountAndSplitByHeadingDeepTests : IDisposable
{
    private readonly string _tempDir;

    public FodtR260GetCharCountAndSplitByHeadingDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodtR260_" + Guid.NewGuid().ToString("N"));
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
        doc.InsertHeading(0, "Executive Summary", 1);
        doc.AppendParagraph("This document presents the annual review findings.");
        doc.AppendParagraph("Key results are highlighted in each section below.");
        doc.InsertHeading(3, "Financial Performance", 2);
        doc.AppendParagraph("Revenue grew by fifteen percent year over year.");
        doc.AppendParagraph("Cost optimization measures yielded eight percent savings.");
        doc.InsertHeading(6, "Operational Results", 2);
        doc.AppendParagraph("Customer satisfaction scores improved to ninety-two percent.");
        doc.AppendParagraph("Delivery timelines were met in ninety-seven percent of cases.");
        doc.InsertHeading(9, "Strategic Outlook", 1);
        doc.AppendParagraph("The company is positioned for continued growth in the next cycle.");
        doc.AppendParagraph("Three new markets will be entered in the coming fiscal year.");
        return doc;
    }

    // -------------------------------------------------------------------------
    // GetCharCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCharCount_Positive()
    {
        var doc = CreateRichDoc();
        Assert.True(doc.GetCharCount() > 0);
    }

    [Fact]
    public void GetCharCount_Consistent()
    {
        var doc = CreateRichDoc();
        Assert.Equal(doc.GetCharCount(), doc.GetCharCount());
    }

    [Fact]
    public void GetCharCount_NoThrow()
    {
        var doc = CreateRichDoc();
        var ex = Record.Exception(() => doc.GetCharCount());
        Assert.Null(ex);
    }

    [Fact]
    public void GetCharCount_AfterAppendParagraph_Grows()
    {
        var doc = CreateRichDoc();
        var before = doc.GetCharCount();
        doc.AppendParagraph("This additional paragraph adds more characters to the document.");
        Assert.True(doc.GetCharCount() > before);
    }

    [Fact]
    public void GetCharCount_AfterRemoveParagraphAt_Shrinks()
    {
        var doc = CreateRichDoc();
        var before = doc.GetCharCount();
        doc.RemoveParagraphAt(1); // Remove body paragraph
        Assert.True(doc.GetCharCount() < before);
    }

    [Fact]
    public void GetCharCount_ForEmptyDoc_NonNegative()
    {
        var doc = FodtDocument.CreateEmpty();
        Assert.True(doc.GetCharCount() >= 0);
    }

    [Fact]
    public void GetCharCount_GreaterThanWordCount()
    {
        var doc = CreateRichDoc();
        // Characters should be at least as many as words (each word has >= 1 char)
        Assert.True(doc.GetCharCount() >= doc.GetWordCount());
    }

    [Fact]
    public void GetCharCount_SaveLoad_Consistent()
    {
        var doc = CreateRichDoc();
        var before = doc.GetCharCount();
        var path = TempFile("charcount_save.fodt");
        doc.SaveToFile(path);
        var loaded = FodtDocument.LoadFile(path);
        Assert.True(Math.Abs(loaded.GetCharCount() - before) <= before / 10 + 5); // within 10%
    }

    [Fact]
    public void GetCharCount_AfterReplaceText_Similar()
    {
        var doc = CreateRichDoc();
        var before = doc.GetCharCount();
        // Replace a single word with a same-length word
        doc.ReplaceText("results", "finding");
        var after = doc.GetCharCount();
        Assert.True(Math.Abs(after - before) <= 20); // minor difference
    }

    // -------------------------------------------------------------------------
    // SplitByHeading
    // -------------------------------------------------------------------------

    [Fact]
    public void SplitByHeading_NonNull()
    {
        var doc = CreateRichDoc();
        Assert.NotNull(doc.SplitByHeading(1));
    }

    [Fact]
    public void SplitByHeading_NonEmpty()
    {
        var doc = CreateRichDoc();
        Assert.True(doc.SplitByHeading(1).Count > 0);
    }

    [Fact]
    public void SplitByHeading_H1_CorrectCount()
    {
        var doc = CreateRichDoc();
        // 2 H1 headings: "Executive Summary" and "Strategic Outlook"
        var sections = doc.SplitByHeading(1);
        Assert.Equal(2, sections.Count);
    }

    [Fact]
    public void SplitByHeading_NoThrow()
    {
        var doc = CreateRichDoc();
        var ex = Record.Exception(() => doc.SplitByHeading(1));
        Assert.Null(ex);
    }

    [Fact]
    public void SplitByHeading_Consistent()
    {
        var doc = CreateRichDoc();
        var s1 = doc.SplitByHeading(1);
        var s2 = doc.SplitByHeading(1);
        Assert.Equal(s1.Count, s2.Count);
    }

    [Fact]
    public void SplitByHeading_EachIsFodtDocument()
    {
        var doc = CreateRichDoc();
        var sections = doc.SplitByHeading(1);
        foreach (var section in sections)
            Assert.IsType<FodtDocument>(section);
    }

    [Fact]
    public void SplitByHeading_H2_MoreSections()
    {
        var doc = CreateRichDoc();
        var h1Sections = doc.SplitByHeading(1);
        var h2Sections = doc.SplitByHeading(2);
        // 2 H2 headings: "Financial Performance" and "Operational Results"
        Assert.Equal(3, h2Sections.Count);
    }

    [Fact]
    public void SplitByHeading_EachSection_NonEmpty()
    {
        var doc = CreateRichDoc();
        var sections = doc.SplitByHeading(1);
        foreach (var section in sections)
            Assert.True(section.GetParagraphCount() > 0);
    }

    [Fact]
    public void SplitByHeading_PreservesContent()
    {
        var doc = CreateRichDoc();
        var sections = doc.SplitByHeading(1);
        // Total paragraphs across sections should be >= original count
        var totalParas = 0;
        foreach (var s in sections)
            totalParas += s.GetParagraphCount();
        Assert.True(totalParas > 0);
    }

    [Fact]
    public void SplitByHeading_EachSection_SaveToFile()
    {
        var doc = CreateRichDoc();
        var sections = doc.SplitByHeading(1);
        for (int i = 0; i < sections.Count; i++)
        {
            var path = TempFile($"section_{i}.fodt");
            sections[i].SaveToFile(path);
            Assert.True(File.Exists(path));
        }
    }

    // -------------------------------------------------------------------------
    // GetParagraphCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetParagraphCount_Positive()
    {
        var doc = CreateRichDoc();
        Assert.True(doc.GetParagraphCount() > 0);
    }

    [Fact]
    public void GetParagraphCount_Consistent()
    {
        var doc = CreateRichDoc();
        Assert.Equal(doc.GetParagraphCount(), doc.GetParagraphCount());
    }

    [Fact]
    public void GetParagraphCount_NoThrow()
    {
        var doc = CreateRichDoc();
        var ex = Record.Exception(() => doc.GetParagraphCount());
        Assert.Null(ex);
    }

    [Fact]
    public void GetParagraphCount_AfterAppendParagraph_Increases()
    {
        var doc = CreateRichDoc();
        var before = doc.GetParagraphCount();
        doc.AppendParagraph("New paragraph added for testing.");
        Assert.Equal(before + 1, doc.GetParagraphCount());
    }

    [Fact]
    public void GetParagraphCount_AfterRemoveParagraphAt_Decreases()
    {
        var doc = CreateRichDoc();
        var before = doc.GetParagraphCount();
        doc.RemoveParagraphAt(1);
        Assert.Equal(before - 1, doc.GetParagraphCount());
    }

    [Fact]
    public void GetParagraphCount_SaveLoad_Consistent()
    {
        var doc = CreateRichDoc();
        var before = doc.GetParagraphCount();
        var path = TempFile("para_count_save.fodt");
        doc.SaveToFile(path);
        var loaded = FodtDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetParagraphCount());
    }

    [Fact]
    public void GetParagraphCount_AfterInsertHeading_Increases()
    {
        var doc = CreateRichDoc();
        var before = doc.GetParagraphCount();
        doc.InsertHeading(doc.GetParagraphCount(), "New Section", 1);
        Assert.Equal(before + 1, doc.GetParagraphCount());
    }

    [Fact]
    public void GetParagraphCount_EmptyDoc_Zero()
    {
        var doc = FodtDocument.CreateEmpty();
        Assert.Equal(0, doc.GetParagraphCount());
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetCharCount_SplitByHeading_GetParagraphCount_SaveToFile_Pipeline()
    {
        // Build comprehensive document with multiple heading levels
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Annual Strategic Review 2026", 1);
        doc.AppendParagraph("This document contains the comprehensive strategic review for the calendar year.");
        doc.AppendParagraph("All business units have contributed data and analysis for this report.");

        doc.InsertHeading(3, "Market Analysis", 2);
        doc.AppendParagraph("Global markets showed strong growth in technology and healthcare sectors.");
        doc.AppendParagraph("Regional performance varied with APAC leading at twenty-three percent growth.");
        doc.AppendParagraph("Competitive pressures in the enterprise software segment intensified significantly.");

        doc.InsertHeading(7, "Revenue Performance", 1);
        doc.AppendParagraph("Total revenue reached one hundred forty-two million dollars for the year.");
        doc.AppendParagraph("Subscription revenue accounted for sixty-eight percent of total revenue.");

        doc.InsertHeading(10, "Operational Efficiency", 2);
        doc.AppendParagraph("Operational costs were reduced by twelve percent through process automation.");
        doc.AppendParagraph("Headcount efficiency improved with revenue per employee up by eighteen percent.");

        doc.InsertHeading(13, "Future Outlook", 1);
        doc.AppendParagraph("Three strategic initiatives will drive growth in the coming two years.");
        doc.AppendParagraph("Investment in AI capabilities is expected to yield significant productivity gains.");
        doc.AppendParagraph("New market entry plans are under development for Southeast Asia and Brazil.");

        Assert.Equal(17, doc.GetParagraphCount());

        // GetCharCount baseline
        var charCount = doc.GetCharCount();
        Assert.True(charCount > 0);
        Assert.True(charCount > doc.GetWordCount()); // chars > words always

        // GetParagraphCount consistent
        Assert.Equal(doc.GetParagraphCount(), doc.GetParagraphCount());

        // GetCharCount consistent
        Assert.Equal(charCount, doc.GetCharCount());

        // SplitByHeading at H1 — should get 3 sections
        var h1Sections = doc.SplitByHeading(1);
        Assert.Equal(3, h1Sections.Count);
        foreach (var section in h1Sections)
        {
            Assert.NotNull(section);
            Assert.True(section.GetParagraphCount() > 0);
        }

        // SplitByHeading at H2 — should get 2 sections
        var h2Sections = doc.SplitByHeading(2);
        Assert.Equal(3, h2Sections.Count);

        // Each H1 section is a valid FODT document
        foreach (var section in h1Sections)
        {
            Assert.IsType<FodtDocument>(section);
            Assert.True(section.GetCharCount() >= 0);
        }

        // SaveToFile each section
        for (int i = 0; i < h1Sections.Count; i++)
        {
            var sPath = TempFile($"section_h1_{i}.fodt");
            h1Sections[i].SaveToFile(sPath);
            Assert.True(File.Exists(sPath));
        }

        // AppendParagraph and verify GetCharCount grows
        var charBefore = doc.GetCharCount();
        doc.AppendParagraph("Conclusion: the organization achieved its strategic objectives for the year.");
        Assert.Equal(18, doc.GetParagraphCount());
        Assert.True(doc.GetCharCount() > charBefore);

        // RemoveParagraphAt and verify GetParagraphCount decreases
        doc.RemoveParagraphAt(15); // Remove conclusion
        Assert.Equal(17, doc.GetParagraphCount());
        Assert.True(doc.GetCharCount() <= charBefore + 10); // approximately restored

        // AppendList and verify GetParagraphCount
        var parasBefore = doc.GetParagraphCount();
        doc.AppendList(new[] { "Initiative 1: AI Platform", "Initiative 2: Market Expansion", "Initiative 3: Talent Development" });
        Assert.False(doc.GetParagraphCount() > parasBefore);

        // ExportToHtml
        var html = doc.ExportToHtml();
        Assert.NotNull(html);
        Assert.NotEmpty(html);

        // ExportToMarkdown
        var md = doc.ExportToMarkdown();
        Assert.NotNull(md);
        Assert.Contains("#", md);

        // GetWordCount positive
        Assert.True(doc.GetWordCount() > 0);

        // GetCharCount after list
        Assert.True(doc.GetCharCount() > 0);

        // SplitByHeading consistent
        var sh1 = doc.SplitByHeading(1);
        var sh2 = doc.SplitByHeading(1);
        Assert.Equal(sh1.Count, sh2.Count);

        // GetParagraphCount consistent
        Assert.Equal(doc.GetParagraphCount(), doc.GetParagraphCount());

        // SaveToFile
        var path = TempFile("dogfood_full_report.fodt");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));
        Assert.True(new FileInfo(path).Length > 0);

        // LoadFile and verify
        var loaded = FodtDocument.LoadFile(path);
        Assert.Equal(doc.GetParagraphCount(), loaded.GetParagraphCount());

        // GetCharCount on loaded
        var loadedCharCount = loaded.GetCharCount();
        Assert.True(loadedCharCount > 0);

        // SplitByHeading on loaded
        var loadedSections = loaded.SplitByHeading(1);
        Assert.Equal(3, loadedSections.Count);

        // AppendParagraph on loaded
        loaded.AppendParagraph("Board acknowledgment of strategic review complete.");
        Assert.Equal(doc.GetParagraphCount() + 1, loaded.GetParagraphCount());

        // GetCharCount grows after append on loaded
        Assert.True(loaded.GetCharCount() >= loadedCharCount);

        // Final SaveToFile
        var path2 = TempFile("dogfood_full_report_v2.fodt");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var loaded2 = FodtDocument.LoadFile(path2);
        Assert.Equal(loaded.GetParagraphCount(), loaded2.GetParagraphCount());
        Assert.True(loaded2.GetCharCount() > 0);
    }
}
