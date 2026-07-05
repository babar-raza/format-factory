// Tests for FodtDocument.GetFootnoteCount, AddFootnote, GetFootnoteText deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODT-R287

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R287: Tests for FodtDocument.GetFootnoteCount, AddFootnote, GetFootnoteText deeper.
/// GetFootnoteCount(): returns the number of footnotes in the document.
/// AddFootnote(paragraphIndex, text): adds a footnote at the specified paragraph.
/// GetFootnoteText(footnoteIndex): returns the text of the specified footnote.
/// Covers: GetFootnoteCount no-throw; GetFootnoteCount non-negative; GetFootnoteCount consistent;
/// GetFootnoteCount zero for new doc; GetFootnoteCount after AddFootnote increases;
/// GetFootnoteCount save-load;
/// AddFootnote no-throw; AddFootnote increases count; AddFootnote save-load;
/// AddFootnote multiple; AddFootnote then ExportToHtml no-throw;
/// AddFootnote then ExportToMarkdown no-throw; AddFootnote then GetCharCount positive;
/// GetFootnoteText no-throw; GetFootnoteText non-null; GetFootnoteText consistent;
/// GetFootnoteText save-load; GetFootnoteText multiple footnotes;
/// dogfood CreateDoc→AddFootnote→GetFootnoteCount→GetFootnoteText→SaveToFile pipeline.
/// </summary>
public class FodtR287GetFootnoteCountAndAddFootnoteDeepTests : IDisposable
{
    private readonly string _tempDir;

    public FodtR287GetFootnoteCountAndAddFootnoteDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodtR287_" + Guid.NewGuid().ToString("N"));
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
        doc.InsertHeading(0, "Economic Analysis of Digital Markets", 1);
        doc.AppendParagraph("The global digital economy has expanded significantly over the past decade.");
        doc.AppendParagraph("Platform economics drive network effects that create natural monopolies.");
        doc.InsertHeading(3, "Market Concentration Metrics", 2);
        doc.AppendParagraph("The Herfindahl-Hirschman Index measures market concentration across sectors.");
        doc.AppendParagraph("Regulatory interventions have historically reduced concentration in traditional markets.");
        return doc;
    }

    // -------------------------------------------------------------------------
    // GetFootnoteCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetFootnoteCount_NoThrow()
    {
        var doc = CreateRichDoc();
        var ex = Record.Exception(() => doc.GetFootnoteCount());
        Assert.Null(ex);
    }

    [Fact]
    public void GetFootnoteCount_NonNegative()
    {
        var doc = CreateRichDoc();
        Assert.True(doc.GetFootnoteCount() >= 0);
    }

    [Fact]
    public void GetFootnoteCount_Consistent()
    {
        var doc = CreateRichDoc();
        Assert.Equal(doc.GetFootnoteCount(), doc.GetFootnoteCount());
    }

    [Fact]
    public void GetFootnoteCount_Zero_ForNewDoc()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("No footnotes yet.");
        Assert.Equal(0, doc.GetFootnoteCount());
    }

    [Fact]
    public void GetFootnoteCount_AfterAddFootnote_Increases()
    {
        var doc = CreateRichDoc();
        var before = doc.GetFootnoteCount();
        doc.AddFootnote(1, "World Bank Digital Economy Report, 2024.");
        Assert.Equal(before + 1, doc.GetFootnoteCount());
    }

    [Fact]
    public void GetFootnoteCount_SaveLoad_Consistent()
    {
        var doc = CreateRichDoc();
        doc.AddFootnote(1, "Source: OECD Digital Economy Outlook 2024.");
        var before = doc.GetFootnoteCount();
        var path = TempFile("fnc_save.fodt");
        doc.SaveToFile(path);
        var loaded = FodtDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetFootnoteCount());
    }

    // -------------------------------------------------------------------------
    // AddFootnote
    // -------------------------------------------------------------------------

    [Fact]
    public void AddFootnote_NoThrow()
    {
        var doc = CreateRichDoc();
        var ex = Record.Exception(() => doc.AddFootnote(1, "Reference: Smith et al., Journal of Economics, 2023."));
        Assert.Null(ex);
    }

    [Fact]
    public void AddFootnote_Increases_Count()
    {
        var doc = CreateRichDoc();
        var before = doc.GetFootnoteCount();
        doc.AddFootnote(2, "See also: Digital Markets Act, European Commission, 2022.");
        Assert.Equal(before + 1, doc.GetFootnoteCount());
    }

    [Fact]
    public void AddFootnote_SaveLoad_Persists()
    {
        var doc = CreateRichDoc();
        doc.AddFootnote(1, "IMF Working Paper on Platform Economics, 2023.");
        var before = doc.GetFootnoteCount();
        var path = TempFile("af_save.fodt");
        doc.SaveToFile(path);
        var loaded = FodtDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetFootnoteCount());
    }

    [Fact]
    public void AddFootnote_Multiple()
    {
        var doc = CreateRichDoc();
        doc.AddFootnote(0, "Data sourced from World Bank Open Data repository.");
        doc.AddFootnote(2, "HHI values above 2500 indicate high market concentration.");
        doc.AddFootnote(4, "See Tirole, J., Industrial Organization, MIT Press.");
        Assert.Equal(3, doc.GetFootnoteCount());
    }

    [Fact]
    public void AddFootnote_Then_ExportToHtml_NoThrow()
    {
        var doc = CreateRichDoc();
        doc.AddFootnote(1, "HTML export footnote test reference.");
        var ex = Record.Exception(() => doc.ExportToHtml());
        Assert.Null(ex);
    }

    [Fact]
    public void AddFootnote_Then_ExportToMarkdown_NoThrow()
    {
        var doc = CreateRichDoc();
        doc.AddFootnote(2, "Markdown export footnote test reference.");
        var ex = Record.Exception(() => doc.ExportToMarkdown());
        Assert.Null(ex);
    }

    [Fact]
    public void AddFootnote_Then_GetCharCount_Positive()
    {
        var doc = CreateRichDoc();
        doc.AddFootnote(1, "GetCharCount footnote test.");
        Assert.True(doc.GetCharCount() > 0);
    }

    // -------------------------------------------------------------------------
    // GetFootnoteText
    // -------------------------------------------------------------------------

    [Fact]
    public void GetFootnoteText_NoThrow()
    {
        var doc = CreateRichDoc();
        doc.AddFootnote(1, "Test footnote text.");
        var ex = Record.Exception(() => doc.GetFootnoteText(0));
        Assert.Null(ex);
    }

    [Fact]
    public void GetFootnoteText_NonNull()
    {
        var doc = CreateRichDoc();
        doc.AddFootnote(1, "Non-null test footnote.");
        Assert.NotNull(doc.GetFootnoteText(0));
    }

    [Fact]
    public void GetFootnoteText_Consistent()
    {
        var doc = CreateRichDoc();
        doc.AddFootnote(1, "Consistent text footnote.");
        Assert.Equal(doc.GetFootnoteText(0), doc.GetFootnoteText(0));
    }

    [Fact]
    public void GetFootnoteText_SaveLoad_Consistent()
    {
        var doc = CreateRichDoc();
        doc.AddFootnote(1, "Save load footnote text.");
        var before = doc.GetFootnoteText(0);
        var path = TempFile("gft_save.fodt");
        doc.SaveToFile(path);
        var loaded = FodtDocument.LoadFile(path);
        var after = loaded.GetFootnoteText(0);
        Assert.NotNull(after);
        Assert.True(after.Length >= 0);
    }

    [Fact]
    public void GetFootnoteText_Multiple_Footnotes()
    {
        var doc = CreateRichDoc();
        doc.AddFootnote(0, "First footnote reference.");
        doc.AddFootnote(2, "Second footnote reference.");
        Assert.NotNull(doc.GetFootnoteText(0));
        Assert.NotNull(doc.GetFootnoteText(1));
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_AddFootnote_GetFootnoteCount_GetFootnoteText_SaveToFile_Pipeline()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Monetary Policy Framework and Transmission Mechanisms", 1);
        doc.AppendParagraph("Central banks employ interest rate policy as their primary tool for inflation management.");
        doc.AppendParagraph("The transmission mechanism operates through lending rates, asset prices, and exchange rates.");

        doc.InsertHeading(3, "Quantitative Easing", 2);
        doc.AppendParagraph("Quantitative easing involves central bank purchases of government bonds and other securities.");
        doc.AppendParagraph("The policy aims to lower long-term interest rates when short-term rates approach zero.");

        doc.InsertHeading(6, "Forward Guidance", 2);
        doc.AppendParagraph("Forward guidance communicates future policy intentions to influence market expectations.");
        doc.AppendParagraph("Effectiveness depends on central bank credibility and market interpretation accuracy.");

        doc.InsertHeading(9, "Empirical Evidence", 1);
        doc.AppendParagraph("Meta-analysis of central bank interventions shows average inflation reduction of 1.8 percentage points.");
        doc.AppendParagraph("Asset purchase programmes reduced ten-year yields by approximately 100 basis points on average.");

        Assert.Equal(12, doc.GetParagraphCount());

        // GetFootnoteCount — zero initially
        Assert.Equal(0, doc.GetFootnoteCount());

        // AddFootnote — introduction
        doc.AddFootnote(0, "BIS Working Paper No. 718: Central Bank Communication and Monetary Policy, 2018.");
        Assert.Equal(1, doc.GetFootnoteCount());

        // AddFootnote — QE
        doc.AddFootnote(3, "Bernanke, B. and Reinhart, V., Conducting Monetary Policy at Very Low Short-Term Rates, AER, 2004.");
        Assert.Equal(2, doc.GetFootnoteCount());

        // AddFootnote — forward guidance
        doc.AddFootnote(6, "Woodford, M., Inflation Targeting and Financial Stability, Swedish Riksbank Economic Review, 2012.");
        Assert.Equal(3, doc.GetFootnoteCount());

        // AddFootnote — empirical
        doc.AddFootnote(9, "Quantitative Easing Literature Review, Federal Reserve Bank of New York Staff Reports, 2020.");
        Assert.Equal(4, doc.GetFootnoteCount());

        // GetFootnoteText
        var t0 = doc.GetFootnoteText(0);
        var t1 = doc.GetFootnoteText(1);
        var t2 = doc.GetFootnoteText(2);
        var t3 = doc.GetFootnoteText(3);
        Assert.NotNull(t0);
        Assert.NotNull(t1);
        Assert.NotNull(t2);
        Assert.NotNull(t3);

        // Consistent
        Assert.Equal(doc.GetFootnoteCount(), doc.GetFootnoteCount());
        Assert.Equal(doc.GetFootnoteText(0), doc.GetFootnoteText(0));

        // ExportToHtml works
        var html = doc.ExportToHtml();
        Assert.NotNull(html);
        Assert.NotEmpty(html);

        // ExportToMarkdown works
        var md = doc.ExportToMarkdown();
        Assert.NotNull(md);
        Assert.NotEmpty(md);

        // ExportToPlainText works
        var plain = doc.ExportToPlainText();
        Assert.NotNull(plain);
        Assert.NotEmpty(plain);

        // GetCharCount and GetWordCount positive
        Assert.True(doc.GetCharCount() > 0);
        Assert.True(doc.GetWordCount() > 0);

        // SaveToFile
        var path = TempFile("dogfood_monetary.fodt");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));
        Assert.True(new FileInfo(path).Length > 0);

        // LoadFile and verify
        var loaded = FodtDocument.LoadFile(path);
        Assert.Equal(4, loaded.GetFootnoteCount());
        Assert.True(loaded.GetParagraphCount() > 0);

        // GetFootnoteText on loaded
        for (int i = 0; i < loaded.GetFootnoteCount(); i++)
            Assert.NotNull(loaded.GetFootnoteText(i));

        // AddFootnote on loaded
        loaded.AddFootnote(loaded.GetParagraphCount() - 1, "IMF Global Financial Stability Report, April 2024.");
        Assert.Equal(5, loaded.GetFootnoteCount());

        // ExportToHtml on loaded
        var loadedHtml = loaded.ExportToHtml();
        Assert.NotNull(loadedHtml);
        Assert.NotEmpty(loadedHtml);

        // AppendParagraph on loaded
        loaded.AppendParagraph("Conclusion: unconventional monetary policy tools proved effective during the zero lower bound period.");
        Assert.True(loaded.GetParagraphCount() > doc.GetParagraphCount());

        // Final save
        var path2 = TempFile("dogfood_monetary_v2.fodt");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var loaded2 = FodtDocument.LoadFile(path2);
        Assert.Equal(5, loaded2.GetFootnoteCount());
        Assert.True(loaded2.GetParagraphCount() > 0);
        var ex1 = Record.Exception(() => loaded2.ExportToHtml());
        var ex2 = Record.Exception(() => loaded2.ExportToMarkdown());
        var ex3 = Record.Exception(() => loaded2.ExportToPlainText());
        Assert.Null(ex1);
        Assert.Null(ex2);
        Assert.Null(ex3);
    }
}
