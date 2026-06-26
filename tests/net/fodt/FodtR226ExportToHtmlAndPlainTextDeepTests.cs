// Tests for FodtDocument.ExportToHtml, ExportToPlainText, GetDocumentStats deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODT-R226

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R226: Tests for FodtDocument.ExportToHtml, ExportToPlainText, GetDocumentStats deeper.
/// ExportToHtml(): exports document as HTML string.
/// ExportToPlainText(): exports document as plain text string.
/// GetDocumentStats(): returns stats object with WordCount, CharCount, ParagraphCount, HeadingCount.
/// Covers: ExportToHtml non-null; ExportToHtml non-empty; ExportToHtml has HTML structure;
/// ExportToHtml contains heading text; ExportToHtml contains body text;
/// ExportToHtml after AppendParagraph longer; ExportToHtml after ReplaceText reflects;
/// ExportToPlainText non-null; ExportToPlainText non-empty;
/// ExportToPlainText contains heading; ExportToPlainText contains body;
/// ExportToPlainText after AppendParagraph longer; ExportToPlainText after ReplaceText reflects;
/// GetDocumentStats non-null; GetDocumentStats WordCount positive; GetDocumentStats CharCount positive;
/// GetDocumentStats ParagraphCount correct; GetDocumentStats HeadingCount correct;
/// GetDocumentStats matches GetParagraphCount and GetHeadingCount;
/// dogfood CreateDoc→GetDocumentStats→ExportToHtml→ExportToPlainText→mutation→verify pipeline.
/// </summary>
public class FodtR226ExportToHtmlAndPlainTextDeepTests : IDisposable
{
    private readonly string _tempDir;

    public FodtR226ExportToHtmlAndPlainTextDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodtR226_" + Guid.NewGuid().ToString("N"));
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
        doc.InsertHeading(0, "Overview", 1);
        doc.AppendParagraph("This overview provides a summary of the project goals and timeline.");
        doc.AppendParagraph("Stakeholders should review this section before proceeding further.");
        doc.InsertHeading(3, "Technical Details", 2);
        doc.AppendParagraph("The technical details describe the implementation architecture.");
        doc.InsertHeading(5, "Summary", 1);
        doc.AppendParagraph("The summary concludes the document with key action items.");
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
    public void ExportToHtml_HasHtmlStructure()
    {
        var doc = CreateRichDoc();
        var html = doc.ExportToHtml();
        Assert.True(html.Contains("<") && html.Length > 0);
    }

    [Fact]
    public void ExportToHtml_ContainsHeadingText()
    {
        var doc = CreateRichDoc();
        var html = doc.ExportToHtml();
        Assert.True(html.Contains("Overview") || html.Contains("Summary"));
    }

    [Fact]
    public void ExportToHtml_ContainsBodyText()
    {
        var doc = CreateRichDoc();
        var html = doc.ExportToHtml();
        Assert.True(html.Contains("overview") || html.Contains("technical") || html.Contains("summary"));
    }

    [Fact]
    public void ExportToHtml_AfterAppendParagraph_Longer()
    {
        var doc = CreateRichDoc();
        var before = doc.ExportToHtml().Length;
        doc.AppendParagraph("An additional paragraph was inserted for further context.");
        var after = doc.ExportToHtml().Length;
        Assert.True(after > before);
    }

    [Fact]
    public void ExportToHtml_AfterReplaceText_Reflects()
    {
        var doc = CreateRichDoc();
        doc.ReplaceText("Overview", "EXECUTIVE_OVERVIEW");
        var html = doc.ExportToHtml();
        Assert.Contains("EXECUTIVE_OVERVIEW", html);
    }

    // -------------------------------------------------------------------------
    // ExportToPlainText
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportToPlainText_NonNull()
    {
        var doc = CreateRichDoc();
        Assert.NotNull(doc.ExportToPlainText());
    }

    [Fact]
    public void ExportToPlainText_NonEmpty()
    {
        var doc = CreateRichDoc();
        Assert.NotEmpty(doc.ExportToPlainText());
    }

    [Fact]
    public void ExportToPlainText_ContainsHeading()
    {
        var doc = CreateRichDoc();
        var text = doc.ExportToPlainText();
        Assert.True(text.Contains("Overview") || text.Contains("Summary"));
    }

    [Fact]
    public void ExportToPlainText_ContainsBodyText()
    {
        var doc = CreateRichDoc();
        var text = doc.ExportToPlainText();
        Assert.True(text.Contains("overview") || text.Contains("technical") || text.Contains("summary"));
    }

    [Fact]
    public void ExportToPlainText_AfterAppendParagraph_Longer()
    {
        var doc = CreateRichDoc();
        var before = doc.ExportToPlainText().Length;
        doc.AppendParagraph("Additional paragraph content for plain text export.");
        var after = doc.ExportToPlainText().Length;
        Assert.True(after > before);
    }

    [Fact]
    public void ExportToPlainText_AfterReplaceText_Reflects()
    {
        var doc = CreateRichDoc();
        doc.ReplaceText("Summary", "CONCLUSION");
        var text = doc.ExportToPlainText();
        Assert.Contains("CONCLUSION", text);
    }

    // -------------------------------------------------------------------------
    // GetDocumentStats
    // -------------------------------------------------------------------------

    [Fact]
    public void GetDocumentStats_NonNull()
    {
        var doc = CreateRichDoc();
        Assert.NotNull(doc.GetDocumentStats());
    }

    [Fact]
    public void GetDocumentStats_WordCountPositive()
    {
        var doc = CreateRichDoc();
        Assert.True(doc.GetDocumentStats().WordCount > 0);
    }

    [Fact]
    public void GetDocumentStats_CharCountPositive()
    {
        var doc = CreateRichDoc();
        Assert.True(doc.GetDocumentStats().CharCount > 0);
    }

    [Fact]
    public void GetDocumentStats_ParagraphCountCorrect()
    {
        var doc = CreateRichDoc();
        Assert.Equal(doc.GetParagraphCount(), doc.GetDocumentStats().ParagraphCount);
    }

    [Fact]
    public void GetDocumentStats_HeadingCountCorrect()
    {
        var doc = CreateRichDoc();
        Assert.Equal(doc.GetHeadingCount(), doc.GetDocumentStats().HeadingCount);
    }

    [Fact]
    public void GetDocumentStats_CharCountGreaterThanWordCount()
    {
        var doc = CreateRichDoc();
        var stats = doc.GetDocumentStats();
        Assert.True(stats.CharCount > stats.WordCount);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CreateDoc_GetDocumentStats_ExportToHtml_ExportToPlainText_Mutation_Pipeline()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Project Proposal", 1);
        doc.AppendParagraph("This proposal outlines the scope and objectives of the project.");
        doc.AppendParagraph("The team will deliver results within the agreed-upon timeline.");
        doc.InsertHeading(3, "Budget Overview", 2);
        doc.AppendParagraph("The budget covers personnel, infrastructure, and operational costs.");
        doc.InsertHeading(5, "Next Steps", 1);
        doc.AppendParagraph("The next steps include stakeholder review and final approval.");

        // GetDocumentStats
        var stats = doc.GetDocumentStats();
        Assert.NotNull(stats);
        Assert.Equal(3, stats.HeadingCount);
        Assert.Equal(6, stats.ParagraphCount); // 3 headings + 3 body paras
        Assert.True(stats.WordCount > 20);
        Assert.True(stats.CharCount > stats.WordCount);

        // ExportToHtml
        var html = doc.ExportToHtml();
        Assert.NotNull(html);
        Assert.True(html.Contains("<") && html.Length > 0);
        Assert.True(html.Contains("Project Proposal") || html.Contains("Budget"));

        // ExportToPlainText
        var text = doc.ExportToPlainText();
        Assert.NotNull(text);
        Assert.NotEmpty(text);
        Assert.True(text.Contains("Project Proposal") || text.Contains("proposal"));

        // AppendParagraph — stats and exports should grow
        doc.AppendParagraph("An additional paragraph provides supplementary information.");
        var updatedStats = doc.GetDocumentStats();
        Assert.True(updatedStats.ParagraphCount > stats.ParagraphCount);
        Assert.True(updatedStats.WordCount > stats.WordCount);

        var updatedHtml = doc.ExportToHtml();
        Assert.True(updatedHtml.Length > html.Length);
        var updatedText = doc.ExportToPlainText();
        Assert.True(updatedText.Length > text.Length);

        // ReplaceText and verify reflection
        doc.ReplaceText("proposal", "initiative");
        doc.ReplaceText("Proposal", "Initiative");
        var replacedHtml = doc.ExportToHtml();
        Assert.True(replacedHtml.Contains("Initiative") || replacedHtml.Contains("initiative"));
        var replacedText = doc.ExportToPlainText();
        Assert.True(replacedText.Contains("Initiative") || replacedText.Contains("initiative"));

        // SaveToFile and reload
        var path = TempFile("dogfood_export.fodt");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));

        var loaded = FodtDocument.LoadFile(path);
        Assert.NotNull(loaded);
        var loadedHtml = loaded.ExportToHtml();
        Assert.NotNull(loadedHtml);
        Assert.NotEmpty(loadedHtml);
        var loadedStats = loaded.GetDocumentStats();
        Assert.Equal(3, loadedStats.HeadingCount);
    }
}
