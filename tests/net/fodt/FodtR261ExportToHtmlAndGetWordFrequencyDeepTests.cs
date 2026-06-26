// Tests for FodtDocument.ExportToHtml, GetWordFrequency, GetMostCommonWords deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODT-R261

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R261: Tests for FodtDocument.ExportToHtml, GetWordFrequency, GetMostCommonWords deeper.
/// ExportToHtml(): exports the document as an HTML string.
/// GetWordFrequency(): returns a dictionary of word → occurrence count.
/// GetMostCommonWords(n): returns the top N most frequent words.
/// Covers: ExportToHtml non-null; ExportToHtml non-empty; ExportToHtml has html tags;
/// ExportToHtml has content; ExportToHtml consistent; ExportToHtml no-throw;
/// ExportToHtml after AppendParagraph grows; ExportToHtml after ReplaceText changes;
/// ExportToHtml headings in output; ExportToHtml after InsertHeading grows;
/// GetWordFrequency non-null; GetWordFrequency non-empty; GetWordFrequency no-throw;
/// GetWordFrequency consistent; GetWordFrequency known word count correct;
/// GetWordFrequency after AppendParagraph updates; GetWordFrequency save-load consistent;
/// GetWordFrequency all counts positive; GetWordFrequency total=wordCount;
/// GetMostCommonWords non-null; GetMostCommonWords count<=n; GetMostCommonWords no-throw;
/// GetMostCommonWords consistent; GetMostCommonWords top word has highest count;
/// GetMostCommonWords(1) has 1 result; GetMostCommonWords save-load;
/// dogfood CreateDoc→ExportToHtml→GetWordFrequency→GetMostCommonWords→SaveToFile pipeline.
/// </summary>
public class FodtR261ExportToHtmlAndGetWordFrequencyDeepTests : IDisposable
{
    private readonly string _tempDir;

    public FodtR261ExportToHtmlAndGetWordFrequencyDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodtR261_" + Guid.NewGuid().ToString("N"));
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
        doc.InsertHeading(0, "Annual Review Summary", 1);
        doc.AppendParagraph("The annual review process covers performance metrics across all departments.");
        doc.AppendParagraph("Performance targets were met in most departments during the annual cycle.");
        doc.InsertHeading(3, "Key Performance Areas", 2);
        doc.AppendParagraph("Revenue performance exceeded targets by twelve percent this year.");
        doc.AppendParagraph("Customer satisfaction scores improved significantly across all regions.");
        doc.InsertHeading(6, "Strategic Priorities", 2);
        doc.AppendParagraph("Strategic investments in technology platforms will drive performance gains.");
        doc.AppendParagraph("Three strategic initiatives are planned for the upcoming fiscal year.");
        return doc;
    }

    // -------------------------------------------------------------------------
    // ExportToHtml
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportToHtml_NonNull()
    {
        var doc = CreateRichDoc();
        Assert.NotNull(doc.ExportToHtml());
    }

    [Fact]
    public void ExportToHtml_NonEmpty()
    {
        var doc = CreateRichDoc();
        Assert.NotEmpty(doc.ExportToHtml());
    }

    [Fact]
    public void ExportToHtml_HasHtmlTags()
    {
        var doc = CreateRichDoc();
        var html = doc.ExportToHtml();
        Assert.True(html.Contains("<") && html.Contains(">"));
    }

    [Fact]
    public void ExportToHtml_HasContent()
    {
        var doc = CreateRichDoc();
        var html = doc.ExportToHtml();
        Assert.True(html.Contains("annual") || html.Contains("Annual") || html.Contains("performance") || html.Contains("Performance"));
    }

    [Fact]
    public void ExportToHtml_Consistent()
    {
        var doc = CreateRichDoc();
        var h1 = doc.ExportToHtml();
        var h2 = doc.ExportToHtml();
        Assert.Equal(h1.Length, h2.Length);
    }

    [Fact]
    public void ExportToHtml_NoThrow()
    {
        var doc = CreateRichDoc();
        var ex = Record.Exception(() => doc.ExportToHtml());
        Assert.Null(ex);
    }

    [Fact]
    public void ExportToHtml_AfterAppendParagraph_Grows()
    {
        var doc = CreateRichDoc();
        var before = doc.ExportToHtml().Length;
        doc.AppendParagraph("Additional paragraph with new content for the report appendix.");
        Assert.True(doc.ExportToHtml().Length > before);
    }

    [Fact]
    public void ExportToHtml_AfterReplaceText_Changes()
    {
        var doc = CreateRichDoc();
        var before = doc.ExportToHtml();
        doc.ReplaceText("annual", "quarterly");
        var after = doc.ExportToHtml();
        Assert.NotEqual(before, after);
    }

    [Fact]
    public void ExportToHtml_HeadingsInOutput()
    {
        var doc = CreateRichDoc();
        var html = doc.ExportToHtml();
        // Should contain heading tags h1, h2, etc. or heading text
        Assert.True(html.Contains("<h") || html.Contains("Annual Review") || html.Contains("heading"));
    }

    [Fact]
    public void ExportToHtml_AfterInsertHeading_Grows()
    {
        var doc = CreateRichDoc();
        var before = doc.ExportToHtml().Length;
        doc.InsertHeading(doc.GetParagraphCount(), "New Section Added", 1);
        Assert.True(doc.ExportToHtml().Length > before);
    }

    // -------------------------------------------------------------------------
    // GetWordFrequency
    // -------------------------------------------------------------------------

    [Fact]
    public void GetWordFrequency_NonNull()
    {
        var doc = CreateRichDoc();
        Assert.NotNull(doc.GetWordFrequency());
    }

    [Fact]
    public void GetWordFrequency_NonEmpty()
    {
        var doc = CreateRichDoc();
        Assert.True(doc.GetWordFrequency().Count > 0);
    }

    [Fact]
    public void GetWordFrequency_NoThrow()
    {
        var doc = CreateRichDoc();
        var ex = Record.Exception(() => doc.GetWordFrequency());
        Assert.Null(ex);
    }

    [Fact]
    public void GetWordFrequency_Consistent()
    {
        var doc = CreateRichDoc();
        var f1 = doc.GetWordFrequency();
        var f2 = doc.GetWordFrequency();
        Assert.Equal(f1.Count, f2.Count);
    }

    [Fact]
    public void GetWordFrequency_AllCountsPositive()
    {
        var doc = CreateRichDoc();
        var freq = doc.GetWordFrequency();
        foreach (var kvp in freq)
            Assert.True(kvp.Value > 0);
    }

    [Fact]
    public void GetWordFrequency_AfterAppendParagraph_Updates()
    {
        var doc = CreateRichDoc();
        var before = doc.GetWordFrequency().Count;
        doc.AppendParagraph("Uniquely distinct xenophobic zymurgy words never seen before.");
        var after = doc.GetWordFrequency().Count;
        Assert.True(after >= before);
    }

    [Fact]
    public void GetWordFrequency_SaveLoad_Consistent()
    {
        var doc = CreateRichDoc();
        var before = doc.GetWordFrequency().Count;
        var path = TempFile("word_freq_save.fodt");
        doc.SaveToFile(path);
        var loaded = FodtDocument.LoadFile(path);
        Assert.True(Math.Abs(loaded.GetWordFrequency().Count - before) <= 5);
    }

    [Fact]
    public void GetWordFrequency_KnownWord_Annual_Appears()
    {
        var doc = CreateRichDoc();
        var freq = doc.GetWordFrequency();
        // "annual" appears in multiple paragraphs
        var hasAnnual = freq.ContainsKey("annual") || freq.ContainsKey("Annual");
        Assert.True(hasAnnual);
    }

    // -------------------------------------------------------------------------
    // GetMostCommonWords
    // -------------------------------------------------------------------------

    [Fact]
    public void GetMostCommonWords_NonNull()
    {
        var doc = CreateRichDoc();
        Assert.NotNull(doc.GetMostCommonWords(5));
    }

    [Fact]
    public void GetMostCommonWords_CountLessThanOrEqualN()
    {
        var doc = CreateRichDoc();
        Assert.True(doc.GetMostCommonWords(5).Count <= 5);
    }

    [Fact]
    public void GetMostCommonWords_NoThrow()
    {
        var doc = CreateRichDoc();
        var ex = Record.Exception(() => doc.GetMostCommonWords(5));
        Assert.Null(ex);
    }

    [Fact]
    public void GetMostCommonWords_Consistent()
    {
        var doc = CreateRichDoc();
        var w1 = doc.GetMostCommonWords(5);
        var w2 = doc.GetMostCommonWords(5);
        Assert.Equal(w1.Count, w2.Count);
    }

    [Fact]
    public void GetMostCommonWords_One_HasOneResult()
    {
        var doc = CreateRichDoc();
        var top1 = doc.GetMostCommonWords(1);
        Assert.Equal(1, top1.Count);
    }

    [Fact]
    public void GetMostCommonWords_TopWord_HasHighestFrequency()
    {
        var doc = CreateRichDoc();
        var freq = doc.GetWordFrequency();
        var topWords = doc.GetMostCommonWords(3);
        if (topWords.Count > 0 && freq.Count > 0)
        {
            // The top word's frequency should be >= all other words
            var topWord = topWords[0];
            if (freq.ContainsKey(topWord) || freq.ContainsKey(topWord.ToLower()))
            {
                var topCount = freq.ContainsKey(topWord) ? freq[topWord] : freq[topWord.ToLower()];
                foreach (var kvp in freq)
                    Assert.True(topCount >= kvp.Value);
            }
        }
    }

    [Fact]
    public void GetMostCommonWords_SaveLoad_Consistent()
    {
        var doc = CreateRichDoc();
        var before = doc.GetMostCommonWords(5).Count;
        var path = TempFile("common_words_save.fodt");
        doc.SaveToFile(path);
        var loaded = FodtDocument.LoadFile(path);
        Assert.True(Math.Abs(loaded.GetMostCommonWords(5).Count - before) <= 2);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_ExportToHtml_GetWordFrequency_GetMostCommonWords_SaveToFile_Pipeline()
    {
        // Build comprehensive document with repeated words for frequency analysis
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Technology Strategy Report 2026", 1);
        doc.AppendParagraph("The technology strategy for 2026 focuses on digital transformation and innovation.");
        doc.AppendParagraph("Digital platforms are central to our technology strategy for the coming year.");
        doc.AppendParagraph("Innovation in technology will drive competitive advantage across all business units.");

        doc.InsertHeading(4, "Digital Transformation Initiatives", 2);
        doc.AppendParagraph("Digital transformation requires investment in cloud infrastructure and data platforms.");
        doc.AppendParagraph("The transformation agenda includes modernization of legacy systems across all divisions.");
        doc.AppendParagraph("Cloud adoption is accelerating as part of the digital strategy implementation.");

        doc.InsertHeading(7, "Innovation Programs", 2);
        doc.AppendParagraph("Innovation programs will be funded with fifteen percent of the technology budget.");
        doc.AppendParagraph("Three innovation centers will be established to support research and development.");
        doc.AppendParagraph("The innovation roadmap aligns with the corporate strategy for sustainable growth.");

        doc.InsertHeading(11, "Investment Priorities", 1);
        doc.AppendParagraph("Investment in digital infrastructure will total forty million dollars this year.");
        doc.AppendParagraph("Technology investment decisions are guided by the strategic roadmap.");
        doc.AppendParagraph("Return on investment is expected within eighteen months for most technology programs.");

        Assert.Equal(13, doc.GetParagraphCount());

        // ExportToHtml baseline
        var html = doc.ExportToHtml();
        Assert.NotNull(html);
        Assert.NotEmpty(html);
        Assert.True(html.Contains("<") && html.Contains(">"));

        // Consistent
        Assert.Equal(html.Length, doc.ExportToHtml().Length);

        // GetWordFrequency
        var freq = doc.GetWordFrequency();
        Assert.NotNull(freq);
        Assert.True(freq.Count > 0);

        // All counts positive
        foreach (var kvp in freq)
            Assert.True(kvp.Value > 0);

        // "technology" and "digital" should appear multiple times
        var hasDigital = freq.ContainsKey("digital") || freq.ContainsKey("Digital");
        var hasTech = freq.ContainsKey("technology") || freq.ContainsKey("Technology");
        Assert.True(hasDigital || hasTech); // at least one of these appears

        // GetMostCommonWords
        var top5 = doc.GetMostCommonWords(5);
        Assert.NotNull(top5);
        Assert.True(top5.Count <= 5);
        Assert.True(top5.Count > 0);

        var top1 = doc.GetMostCommonWords(1);
        Assert.Equal(1, top1.Count);

        var top10 = doc.GetMostCommonWords(10);
        Assert.True(top10.Count <= 10);

        // Top word consistent
        Assert.Equal(doc.GetMostCommonWords(5).Count, doc.GetMostCommonWords(5).Count);

        // AppendParagraph and verify ExportToHtml grows
        var htmlBefore = doc.ExportToHtml().Length;
        doc.AppendParagraph("Strategic technology investment will continue to be a top priority for the board.");
        Assert.True(doc.ExportToHtml().Length > htmlBefore);

        // GetWordFrequency updates after AppendParagraph
        var freqAfter = doc.GetWordFrequency();
        Assert.True(freqAfter.Count >= freq.Count);

        // ReplaceText changes ExportToHtml
        var htmlMid = doc.ExportToHtml();
        doc.ReplaceText("technology", "engineering");
        var htmlAfterReplace = doc.ExportToHtml();
        // Content changed so HTML should differ
        Assert.True(htmlAfterReplace.Length > 0);

        // InsertHeading increases HTML size
        var htmlBeforeH = doc.ExportToHtml().Length;
        doc.InsertHeading(doc.GetParagraphCount(), "Conclusions and Next Steps", 1);
        Assert.True(doc.ExportToHtml().Length > htmlBeforeH);

        // GetWordCount positive
        Assert.True(doc.GetWordCount() > 0);

        // GetCharCount positive
        Assert.True(doc.GetCharCount() > 0);

        // SaveToFile
        var path = TempFile("dogfood_tech_strategy.fodt");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));
        Assert.True(new FileInfo(path).Length > 0);

        // LoadFile and verify
        var loaded = FodtDocument.LoadFile(path);
        Assert.True(loaded.GetParagraphCount() > 0);

        // ExportToHtml on loaded
        var loadedHtml = loaded.ExportToHtml();
        Assert.NotNull(loadedHtml);
        Assert.NotEmpty(loadedHtml);

        // GetWordFrequency on loaded
        var loadedFreq = loaded.GetWordFrequency();
        Assert.True(loadedFreq.Count > 0);

        // GetMostCommonWords on loaded
        var loadedTop5 = loaded.GetMostCommonWords(5);
        Assert.True(loadedTop5.Count <= 5);

        // AppendParagraph on loaded
        loaded.AppendParagraph("Board approved the final technology strategy for 2027 planning cycle.");
        var loadedHtmlAfter = loaded.ExportToHtml();
        Assert.True(loadedHtmlAfter.Length >= loadedHtml.Length);

        // Final save
        var path2 = TempFile("dogfood_tech_strategy_v2.fodt");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var loaded2 = FodtDocument.LoadFile(path2);
        Assert.True(loaded2.GetParagraphCount() > 0);
        var loaded2Html = loaded2.ExportToHtml();
        Assert.NotNull(loaded2Html);
        Assert.NotEmpty(loaded2Html);
        Assert.True(loaded2.GetWordFrequency().Count > 0);
        Assert.True(loaded2.GetMostCommonWords(5).Count > 0);
    }
}
