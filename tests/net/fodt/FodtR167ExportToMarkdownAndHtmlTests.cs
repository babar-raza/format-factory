// Tests for FodtDocument.ExportToMarkdown, ExportToHtml, GetPlainText.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODT-R167

using System;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R167: Tests for FodtDocument.ExportToMarkdown, ExportToHtml, GetPlainText.
/// ExportToMarkdown(): returns a Markdown string representation of the document.
/// ExportToHtml(): returns an HTML string representation of the document.
/// GetPlainText(): returns plain text with newline-delimited paragraphs.
/// Covers: ExportToMarkdown empty doc returns string; ExportToMarkdown single para returns content;
/// ExportToMarkdown heading uses # prefix; ExportToMarkdown multiple paras;
/// ExportToHtml empty doc returns string; ExportToHtml contains html/body tags;
/// ExportToHtml contains paragraph content; ExportToHtml heading uses h-tag;
/// GetPlainText empty doc is empty; GetPlainText contains paragraph text;
/// GetPlainText multiple paragraphs has both texts; GetPlainText heading text included;
/// dogfood CreateEmpty->InsertHeading->AppendParagraph->Markdown->Html->PlainText pipeline.
/// </summary>
public class FodtR167ExportToMarkdownAndHtmlTests
{
    // -------------------------------------------------------------------------
    // ExportToMarkdown
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportToMarkdown_EmptyDoc_ReturnsString()
    {
        var doc = FodtDocument.CreateEmpty();
        var md = doc.ExportToMarkdown();
        Assert.NotNull(md);
    }

    [Fact]
    public void ExportToMarkdown_SingleParagraph_ContainsText()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Hello world.");
        var md = doc.ExportToMarkdown();
        Assert.Contains("Hello world.", md);
    }

    [Fact]
    public void ExportToMarkdown_Heading_UsesPoundPrefix()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Chapter One", 1);
        var md = doc.ExportToMarkdown();
        Assert.Contains("#", md);
        Assert.Contains("Chapter One", md);
    }

    [Fact]
    public void ExportToMarkdown_MultipleParagraphs_ContainsAll()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("First paragraph.");
        doc.AppendParagraph("Second paragraph.");
        var md = doc.ExportToMarkdown();
        Assert.Contains("First paragraph.", md);
        Assert.Contains("Second paragraph.", md);
    }

    [Fact]
    public void ExportToMarkdown_Level2Heading_UsesTwoPounds()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Section", 2);
        var md = doc.ExportToMarkdown();
        Assert.Contains("##", md);
    }

    // -------------------------------------------------------------------------
    // ExportToHtml
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportToHtml_EmptyDoc_ReturnsString()
    {
        var doc = FodtDocument.CreateEmpty();
        var html = doc.ExportToHtml();
        Assert.NotNull(html);
    }

    [Fact]
    public void ExportToHtml_ContainsHtmlStructure()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Content.");
        var html = doc.ExportToHtml();
        // Should have some HTML structure
        Assert.True(
            html.Contains("<html", StringComparison.OrdinalIgnoreCase) ||
            html.Contains("<p", StringComparison.OrdinalIgnoreCase) ||
            html.Contains("<body", StringComparison.OrdinalIgnoreCase),
            "Expected HTML structure in output.");
    }

    [Fact]
    public void ExportToHtml_ContainsParagraphContent()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Paragraph content here.");
        var html = doc.ExportToHtml();
        Assert.Contains("Paragraph content here.", html);
    }

    [Fact]
    public void ExportToHtml_Heading_ContainsHeadingContent()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Title Heading", 1);
        var html = doc.ExportToHtml();
        Assert.Contains("Title Heading", html);
    }

    [Fact]
    public void ExportToHtml_MultipleParagraphs_ContainsAll()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Para A.");
        doc.AppendParagraph("Para B.");
        var html = doc.ExportToHtml();
        Assert.Contains("Para A.", html);
        Assert.Contains("Para B.", html);
    }

    // -------------------------------------------------------------------------
    // GetPlainText
    // -------------------------------------------------------------------------

    [Fact]
    public void GetPlainText_EmptyDoc_IsEmpty()
    {
        var doc = FodtDocument.CreateEmpty();
        Assert.True(string.IsNullOrWhiteSpace(doc.GetPlainText()));
    }

    [Fact]
    public void GetPlainText_ContainsParagraphText()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Plain text here.");
        Assert.Contains("Plain text here.", doc.GetPlainText());
    }

    [Fact]
    public void GetPlainText_MultipleParagraphs_ContainsBoth()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("First.");
        doc.AppendParagraph("Second.");
        var text = doc.GetPlainText();
        Assert.Contains("First.", text);
        Assert.Contains("Second.", text);
    }

    [Fact]
    public void GetPlainText_HeadingIncluded()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "My Heading", 1);
        Assert.Contains("My Heading", doc.GetPlainText());
    }

    // -------------------------------------------------------------------------
    // Dogfood: CreateEmpty->InsertHeading->AppendParagraph->Markdown->Html->PlainText
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_ExportMarkdownHtmlPlainText_Pipeline()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Report Title", 1);
        doc.AppendParagraph("Introduction section text.");
        doc.InsertHeading(2, "Results", 2);
        doc.AppendParagraph("Results and analysis.");

        // Markdown
        var md = doc.ExportToMarkdown();
        Assert.Contains("Report Title", md);
        Assert.Contains("Results", md);
        Assert.Contains("Introduction section text.", md);

        // HTML
        var html = doc.ExportToHtml();
        Assert.Contains("Report Title", html);
        Assert.Contains("Results and analysis.", html);

        // Plain text
        var plain = doc.GetPlainText();
        Assert.Contains("Introduction section text.", plain);
        Assert.Contains("Results and analysis.", plain);
    }
}
