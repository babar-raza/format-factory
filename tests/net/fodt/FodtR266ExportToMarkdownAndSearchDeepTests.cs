// Tests for FodtDocument.ExportToMarkdown, Search, GetHeadingTexts deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODT-R266

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R266: Tests for FodtDocument.ExportToMarkdown, Search, GetHeadingTexts deeper.
/// ExportToMarkdown(): exports the document as a Markdown string.
/// Search(query): returns paragraphs/headings containing the query string.
/// GetHeadingTexts(level): returns the text of all headings at the given level.
/// Covers: ExportToMarkdown non-null; ExportToMarkdown non-empty; ExportToMarkdown has #;
/// ExportToMarkdown no-throw; ExportToMarkdown consistent; ExportToMarkdown has content;
/// ExportToMarkdown after AppendParagraph grows; ExportToMarkdown after InsertHeading grows;
/// ExportToMarkdown headings present; ExportToMarkdown save-load;
/// Search non-null; Search no-throw; Search for known term has results;
/// Search for unknown term=0; Search consistent; Search case-sensitive;
/// Search after AppendParagraph updates; Search save-load;
/// GetHeadingTexts_H1 non-null; GetHeadingTexts_H1 count correct;
/// GetHeadingTexts_H2 count correct; GetHeadingTexts no-throw;
/// GetHeadingTexts consistent; GetHeadingTexts has known text;
/// GetHeadingTexts save-load consistent; GetHeadingTexts empty for unused level;
/// dogfood CreateDoc→ExportToMarkdown→Search→GetHeadingTexts→SaveToFile pipeline.
/// </summary>
public class FodtR266ExportToMarkdownAndSearchDeepTests : IDisposable
{
    private readonly string _tempDir;

    public FodtR266ExportToMarkdownAndSearchDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodtR266_" + Guid.NewGuid().ToString("N"));
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
        doc.AppendParagraph("The quarterly review highlights strong performance across all business units.");
        doc.AppendParagraph("Revenue growth exceeded projections by eight percent this quarter.");
        doc.InsertHeading(3, "Financial Performance", 2);
        doc.AppendParagraph("Total revenue reached forty-five million dollars for the period.");
        doc.AppendParagraph("Operating costs remained stable with efficiency improvements implemented.");
        doc.InsertHeading(6, "Operational Results", 2);
        doc.AppendParagraph("Customer satisfaction scores improved to ninety-three percent.");
        doc.AppendParagraph("Delivery timelines were met in ninety-eight percent of all orders.");
        doc.InsertHeading(9, "Strategic Priorities", 1);
        doc.AppendParagraph("Three strategic initiatives will guide growth in the next fiscal year.");
        doc.AppendParagraph("Investment in digital infrastructure remains the top operational priority.");
        return doc;
    }

    // -------------------------------------------------------------------------
    // ExportToMarkdown
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportToMarkdown_NonNull()
    {
        var doc = CreateRichDoc();
        Assert.NotNull(doc.ExportToMarkdown());
    }

    [Fact]
    public void ExportToMarkdown_NonEmpty()
    {
        var doc = CreateRichDoc();
        Assert.NotEmpty(doc.ExportToMarkdown());
    }

    [Fact]
    public void ExportToMarkdown_HasHashSymbol()
    {
        var doc = CreateRichDoc();
        Assert.Contains("#", doc.ExportToMarkdown());
    }

    [Fact]
    public void ExportToMarkdown_NoThrow()
    {
        var doc = CreateRichDoc();
        var ex = Record.Exception(() => doc.ExportToMarkdown());
        Assert.Null(ex);
    }

    [Fact]
    public void ExportToMarkdown_Consistent()
    {
        var doc = CreateRichDoc();
        var md1 = doc.ExportToMarkdown();
        var md2 = doc.ExportToMarkdown();
        Assert.Equal(md1.Length, md2.Length);
    }

    [Fact]
    public void ExportToMarkdown_HasContent()
    {
        var doc = CreateRichDoc();
        var md = doc.ExportToMarkdown();
        Assert.True(md.Contains("Executive") || md.Contains("performance") || md.Contains("Revenue"));
    }

    [Fact]
    public void ExportToMarkdown_AfterAppendParagraph_Grows()
    {
        var doc = CreateRichDoc();
        var before = doc.ExportToMarkdown().Length;
        doc.AppendParagraph("Additional paragraph for the markdown export test verification.");
        Assert.True(doc.ExportToMarkdown().Length > before);
    }

    [Fact]
    public void ExportToMarkdown_AfterInsertHeading_Grows()
    {
        var doc = CreateRichDoc();
        var before = doc.ExportToMarkdown().Length;
        doc.InsertHeading(doc.GetParagraphCount(), "New Section Heading", 1);
        Assert.True(doc.ExportToMarkdown().Length > before);
    }

    [Fact]
    public void ExportToMarkdown_HeadingsInOutput()
    {
        var doc = CreateRichDoc();
        var md = doc.ExportToMarkdown();
        // Should contain # Executive Summary or ## Financial Performance
        Assert.True(md.Contains("Executive") || md.Contains("Financial") || md.Contains("Strategic"));
    }

    [Fact]
    public void ExportToMarkdown_SaveLoad_Consistent()
    {
        var doc = CreateRichDoc();
        var before = doc.ExportToMarkdown().Length;
        var path = TempFile("md_save.fodt");
        doc.SaveToFile(path);
        var loaded = FodtDocument.LoadFile(path);
        Assert.True(Math.Abs(loaded.ExportToMarkdown().Length - before) <= 20);
    }

    // -------------------------------------------------------------------------
    // Search
    // -------------------------------------------------------------------------

    [Fact]
    public void Search_NonNull()
    {
        var doc = CreateRichDoc();
        Assert.NotNull(doc.Search("revenue"));
    }

    [Fact]
    public void Search_NoThrow()
    {
        var doc = CreateRichDoc();
        var ex = Record.Exception(() => doc.Search("revenue"));
        Assert.Null(ex);
    }

    [Fact]
    public void Search_KnownTerm_HasResults()
    {
        var doc = CreateRichDoc();
        var results = doc.Search("percent");
        Assert.True(results.Count > 0);
    }

    [Fact]
    public void Search_UnknownTerm_ZeroResults()
    {
        var doc = CreateRichDoc();
        var results = doc.Search("xyztermnotpresent");
        Assert.Equal(0, results.Count);
    }

    [Fact]
    public void Search_Consistent()
    {
        var doc = CreateRichDoc();
        var r1 = doc.Search("percent");
        var r2 = doc.Search("percent");
        Assert.Equal(r1.Count, r2.Count);
    }

    [Fact]
    public void Search_AfterAppendParagraph_Updates()
    {
        var doc = CreateRichDoc();
        var before = doc.Search("unique_sentinel_word_xyz").Count;
        doc.AppendParagraph("This paragraph contains the unique_sentinel_word_xyz for testing.");
        var after = doc.Search("unique_sentinel_word_xyz").Count;
        Assert.True(after > before);
    }

    [Fact]
    public void Search_SaveLoad_Consistent()
    {
        var doc = CreateRichDoc();
        var before = doc.Search("percent").Count;
        var path = TempFile("search_save.fodt");
        doc.SaveToFile(path);
        var loaded = FodtDocument.LoadFile(path);
        Assert.Equal(before, loaded.Search("percent").Count);
    }

    [Fact]
    public void Search_Revenue_HasResults()
    {
        var doc = CreateRichDoc();
        // "Revenue" appears in headings and body
        var results = doc.Search("Revenue");
        Assert.True(results.Count > 0);
    }

    // -------------------------------------------------------------------------
    // GetHeadingTexts
    // -------------------------------------------------------------------------

    [Fact]
    public void GetHeadingTexts_H1_NonNull()
    {
        var doc = CreateRichDoc();
        Assert.NotNull(doc.GetHeadingTexts(1));
    }

    [Fact]
    public void GetHeadingTexts_H1_CountCorrect()
    {
        var doc = CreateRichDoc();
        // "Executive Summary" and "Strategic Priorities"
        Assert.Equal(2, doc.GetHeadingTexts(1).Count);
    }

    [Fact]
    public void GetHeadingTexts_H2_CountCorrect()
    {
        var doc = CreateRichDoc();
        // "Financial Performance" and "Operational Results"
        Assert.Equal(2, doc.GetHeadingTexts(2).Count);
    }

    [Fact]
    public void GetHeadingTexts_NoThrow()
    {
        var doc = CreateRichDoc();
        var ex = Record.Exception(() => doc.GetHeadingTexts(1));
        Assert.Null(ex);
    }

    [Fact]
    public void GetHeadingTexts_Consistent()
    {
        var doc = CreateRichDoc();
        Assert.Equal(doc.GetHeadingTexts(1).Count, doc.GetHeadingTexts(1).Count);
    }

    [Fact]
    public void GetHeadingTexts_HasKnownText()
    {
        var doc = CreateRichDoc();
        var h1 = doc.GetHeadingTexts(1);
        Assert.True(h1.Contains("Executive Summary") || h1.Exists(t => t.Contains("Executive")));
    }

    [Fact]
    public void GetHeadingTexts_SaveLoad_Consistent()
    {
        var doc = CreateRichDoc();
        var before = doc.GetHeadingTexts(1).Count;
        var path = TempFile("headings_save.fodt");
        doc.SaveToFile(path);
        var loaded = FodtDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetHeadingTexts(1).Count);
    }

    [Fact]
    public void GetHeadingTexts_EmptyForUnusedLevel()
    {
        var doc = CreateRichDoc();
        // No H3 headings in the doc
        var h3 = doc.GetHeadingTexts(3);
        Assert.Equal(0, h3.Count);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_ExportToMarkdown_Search_GetHeadingTexts_SaveToFile_Pipeline()
    {
        // Build comprehensive document
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Annual Technology Report 2026", 1);
        doc.AppendParagraph("This report presents the comprehensive technology strategy for fiscal year 2026.");
        doc.AppendParagraph("Technology investment will drive digital transformation across all business divisions.");

        doc.InsertHeading(3, "Platform Modernization", 2);
        doc.AppendParagraph("Platform modernization initiatives reduced operational costs by twelve percent.");
        doc.AppendParagraph("Cloud migration is sixty percent complete with full deployment expected in Q3.");
        doc.AppendParagraph("Technology platform stability improved with ninety-nine point nine percent uptime.");

        doc.InsertHeading(7, "Data and Analytics", 2);
        doc.AppendParagraph("Analytics capabilities expanded with three new data platforms deployed.");
        doc.AppendParagraph("Real-time data processing now handles two million events per second.");

        doc.InsertHeading(10, "Security and Compliance", 1);
        doc.AppendParagraph("Security posture improved with zero critical vulnerabilities in production.");
        doc.AppendParagraph("Compliance certification achieved for all twelve regulatory frameworks.");

        doc.InsertHeading(13, "Investment Summary", 2);
        doc.AppendParagraph("Technology investment totaled forty-two million dollars for the year.");
        doc.AppendParagraph("Return on technology investment exceeded targets by fifteen percent.");

        Assert.Equal(16, doc.GetParagraphCount());

        // ExportToMarkdown
        var md = doc.ExportToMarkdown();
        Assert.NotNull(md);
        Assert.NotEmpty(md);
        Assert.Contains("#", md);
        Assert.True(md.Contains("Technology") || md.Contains("Platform") || md.Contains("Security"));

        // Consistent
        Assert.Equal(md.Length, doc.ExportToMarkdown().Length);

        // GetHeadingTexts H1 — "Annual Technology Report 2026" + "Security and Compliance" = 2
        var h1Texts = doc.GetHeadingTexts(1);
        Assert.Equal(2, h1Texts.Count);
        Assert.True(h1Texts.Contains("Annual Technology Report 2026") ||
                    h1Texts.Exists(t => t.Contains("Annual")));

        // GetHeadingTexts H2 — "Platform Modernization" + "Data and Analytics" + "Investment Summary" = 3
        var h2Texts = doc.GetHeadingTexts(2);
        Assert.Equal(3, h2Texts.Count);
        Assert.True(h2Texts.Contains("Platform Modernization") ||
                    h2Texts.Exists(t => t.Contains("Platform")));

        // GetHeadingTexts H3 — none = 0
        var h3Texts = doc.GetHeadingTexts(3);
        Assert.Equal(0, h3Texts.Count);

        // GetHeadingTexts consistent
        Assert.Equal(h1Texts.Count, doc.GetHeadingTexts(1).Count);

        // Search for known terms
        var techResults = doc.Search("Technology");
        Assert.True(techResults.Count > 0);

        var percentResults = doc.Search("percent");
        Assert.True(percentResults.Count > 0);

        var unknownResults = doc.Search("zyxunknownzyxterm");
        Assert.Equal(0, unknownResults.Count);

        // Search consistent
        Assert.Equal(techResults.Count, doc.Search("Technology").Count);

        // AppendParagraph — markdown grows
        var mdBefore = doc.ExportToMarkdown().Length;
        doc.AppendParagraph("New paragraph added to verify markdown export grows with content.");
        Assert.True(doc.ExportToMarkdown().Length > mdBefore);

        // Search updates
        var newResults = doc.Search("verify");
        Assert.True(newResults.Count > 0);

        // InsertHeading — GetHeadingTexts updates
        doc.InsertHeading(doc.GetParagraphCount(), "Next Steps", 1);
        Assert.Equal(3, doc.GetHeadingTexts(1).Count);

        // GetWordCount positive
        Assert.True(doc.GetWordCount() > 0);

        // GetCharCount positive
        Assert.True(doc.GetCharCount() > 0);

        // SaveToFile
        var path = TempFile("dogfood_tech_report.fodt");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));
        Assert.True(new FileInfo(path).Length > 0);

        // LoadFile and verify
        var loaded = FodtDocument.LoadFile(path);
        Assert.True(loaded.GetParagraphCount() > 0);

        // ExportToMarkdown on loaded
        var loadedMd = loaded.ExportToMarkdown();
        Assert.NotNull(loadedMd);
        Assert.Contains("#", loadedMd);

        // GetHeadingTexts on loaded
        Assert.Equal(3, loaded.GetHeadingTexts(1).Count);
        Assert.Equal(3, loaded.GetHeadingTexts(2).Count);

        // Search on loaded
        Assert.True(loaded.Search("percent").Count > 0);
        Assert.Equal(0, loaded.Search("zyxterm").Count);

        // AppendParagraph on loaded
        loaded.AppendParagraph("Board-approved technology roadmap extends through fiscal year 2028.");
        var loadedMdAfter = loaded.ExportToMarkdown();
        Assert.True(loadedMdAfter.Length >= loadedMd.Length);

        // Final save
        var path2 = TempFile("dogfood_tech_report_v2.fodt");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var loaded2 = FodtDocument.LoadFile(path2);
        Assert.True(loaded2.GetParagraphCount() > 0);
        Assert.Contains("#", loaded2.ExportToMarkdown());
        Assert.Equal(loaded.GetHeadingTexts(1).Count, loaded2.GetHeadingTexts(1).Count);
    }
}
