// Tests for FodtDocument.ExportToMarkdown, ExportToHtml string methods and Tables.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODT-R184

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R184: Tests for FodtDocument.ExportToMarkdown, ExportToHtml string methods, and Tables.
/// ExportToMarkdown(): returns a Markdown string from the document.
/// ExportToHtml(): returns an HTML string from the document.
/// Tables: list of FodtTable in the document.
/// Covers: ExportToMarkdown non-null; ExportToMarkdown non-empty;
/// ExportToMarkdown contains paragraph text; ExportToHtml non-null;
/// ExportToHtml non-empty; ExportToHtml contains html tag;
/// ExportToHtml contains paragraph content; ExportToMarkdown after AppendParagraph;
/// ExportToHtml after AppendParagraph; Tables is non-null;
/// WordCount positive for loaded doc; CharCount positive for loaded doc;
/// GetHeadingTexts returns list; ParagraphCount positive for loaded doc;
/// dogfood Load->AppendParagraph->ExportMarkdown->ExportHtml->WordCount.
/// </summary>
public class FodtR184ExportToMarkdownAndHtmlTests : IDisposable
{
    private readonly string _tempDir;
    private static readonly string FodtFixturePath =
        Path.Combine(AppContext.BaseDirectory, "..", "..", "..", "..", "..", "..",
            "samples", "by-format", "fodt", "valid", "two-paragraphs.fodt");

    public FodtR184ExportToMarkdownAndHtmlTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodtR184_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private FodtDocument LoadFixture() =>
        FodtDocument.Load(Path.GetFullPath(FodtFixturePath));

    // -------------------------------------------------------------------------
    // ExportToMarkdown (string method)
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportToMarkdown_IsNotNull()
    {
        var doc = LoadFixture();
        Assert.NotNull(doc.ExportToMarkdown());
    }

    [Fact]
    public void ExportToMarkdown_IsNonEmpty()
    {
        var doc = LoadFixture();
        Assert.False(string.IsNullOrEmpty(doc.ExportToMarkdown()));
    }

    [Fact]
    public void ExportToMarkdown_AfterAppendParagraph_ContainsNewText()
    {
        var doc = LoadFixture();
        doc.AppendParagraph("R184 markdown probe");
        var md = doc.ExportToMarkdown();
        Assert.Contains("R184 markdown probe", md);
    }

    [Fact]
    public void ExportToMarkdown_CreatedDoc_ReturnsContent()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Hello Markdown World");
        var md = doc.ExportToMarkdown();
        Assert.Contains("Hello Markdown World", md);
    }

    // -------------------------------------------------------------------------
    // ExportToHtml (string method)
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportToHtml_IsNotNull()
    {
        var doc = LoadFixture();
        Assert.NotNull(doc.ExportToHtml());
    }

    [Fact]
    public void ExportToHtml_IsNonEmpty()
    {
        var doc = LoadFixture();
        Assert.False(string.IsNullOrEmpty(doc.ExportToHtml()));
    }

    [Fact]
    public void ExportToHtml_ContainsHtmlTag()
    {
        var doc = LoadFixture();
        var html = doc.ExportToHtml();
        Assert.Contains("html", html, StringComparison.OrdinalIgnoreCase);
    }

    [Fact]
    public void ExportToHtml_AfterAppendParagraph_ContainsNewText()
    {
        var doc = LoadFixture();
        doc.AppendParagraph("R184 html probe");
        var html = doc.ExportToHtml();
        Assert.Contains("R184 html probe", html);
    }

    [Fact]
    public void ExportToHtml_CreatedDoc_ContainsContent()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Hello HTML World");
        var html = doc.ExportToHtml();
        Assert.Contains("Hello HTML World", html);
    }

    // -------------------------------------------------------------------------
    // Tables, WordCount, CharCount, GetHeadingTexts
    // -------------------------------------------------------------------------

    [Fact]
    public void Tables_IsNotNull()
    {
        var doc = LoadFixture();
        Assert.NotNull(doc.Tables);
    }

    [Fact]
    public void WordCount_Positive_ForLoadedDoc()
    {
        var doc = LoadFixture();
        Assert.True(doc.WordCount > 0);
    }

    [Fact]
    public void CharCount_Positive_ForLoadedDoc()
    {
        var doc = LoadFixture();
        Assert.True(doc.CharCount > 0);
    }

    [Fact]
    public void GetHeadingTexts_ReturnsNonNullList()
    {
        var doc = LoadFixture();
        var headings = doc.GetHeadingTexts();
        Assert.NotNull(headings);
    }

    [Fact]
    public void ParagraphCount_Positive_ForLoadedDoc()
    {
        var doc = LoadFixture();
        Assert.True(doc.ParagraphCount > 0);
    }

    // -------------------------------------------------------------------------
    // Dogfood: Load->AppendParagraph->ExportMarkdown->ExportHtml->WordCount
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_AppendExportMarkdownHtmlWordCount_Pipeline()
    {
        var doc = LoadFixture();
        var initialWords = doc.WordCount;
        var initialParas = doc.ParagraphCount;

        // Append paragraph
        doc.AppendParagraph("Additional content for R184 dogfood test");
        Assert.Equal(initialParas + 1, doc.ParagraphCount);
        Assert.True(doc.WordCount >= initialWords);

        // Export to Markdown string
        var md = doc.ExportToMarkdown();
        Assert.False(string.IsNullOrEmpty(md));
        Assert.Contains("R184 dogfood test", md);

        // Export to HTML string
        var html = doc.ExportToHtml();
        Assert.False(string.IsNullOrEmpty(html));
        Assert.Contains("R184 dogfood test", html);

        // CharCount positive
        Assert.True(doc.CharCount > 0);
    }
}
