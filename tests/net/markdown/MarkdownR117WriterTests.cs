// Tests for MarkdownWriter static API: WriteHeading, WriteParagraphs, WriteLines.
// Sprint: FORMAT-FACTORY-MARKDOWN-WRITER-R117-20260626
// Ledger: R117-GOVERNED-DOTNET-MARKDOWN-WRITER-001

using System;
using System.Collections.Generic;
using Xunit;

namespace FormatFactory.Markdown.Tests;

/// <summary>
/// R117: MarkdownWriter static API — WriteHeading(text, level) produces ATX heading
/// syntax (# for H1, ## for H2, etc.). WriteParagraphs(lines) produces paragraph
/// text with newlines. WriteLines(lines) produces plain text lines. All return
/// non-null strings for valid inputs.
/// </summary>
public class MarkdownR117WriterTests
{
    // ---- WriteHeading: ATX syntax ----

    [Fact]
    public void WriteHeading_Level1_ContainsSingleHash()
    {
        var md = MarkdownWriter.WriteHeading("Main Title", level: 1);
        Assert.Contains("# ", md);
    }

    [Fact]
    public void WriteHeading_Level2_ContainsTwoHashes()
    {
        var md = MarkdownWriter.WriteHeading("Section", level: 2);
        Assert.Contains("## ", md);
    }

    [Fact]
    public void WriteHeading_Level3_ContainsThreeHashes()
    {
        var md = MarkdownWriter.WriteHeading("Subsection", level: 3);
        Assert.Contains("### ", md);
    }

    [Fact]
    public void WriteHeading_Level6_ContainsSixHashes()
    {
        var md = MarkdownWriter.WriteHeading("Deep", level: 6);
        Assert.Contains("###### ", md);
    }

    [Fact]
    public void WriteHeading_ContentPresent()
    {
        var md = MarkdownWriter.WriteHeading("My Header Text", level: 1);
        Assert.Contains("My Header Text", md);
    }

    [Fact]
    public void WriteHeading_H1_DoesNotStartWithDoubleHash()
    {
        var md = MarkdownWriter.WriteHeading("Title", level: 1);
        Assert.DoesNotContain("## Title", md);
    }

    // ---- WriteParagraphs ----

    [Fact]
    public void WriteParagraphs_SingleLine_ContentPresent()
    {
        var md = MarkdownWriter.WriteParagraphs(new[] { "Hello World" });
        Assert.Contains("Hello World", md);
    }

    [Fact]
    public void WriteParagraphs_MultipleLines_AllPresent()
    {
        var md = MarkdownWriter.WriteParagraphs(new[] { "Alpha", "Beta", "Gamma" });
        Assert.Contains("Alpha", md);
        Assert.Contains("Beta", md);
        Assert.Contains("Gamma", md);
    }

    [Fact]
    public void WriteParagraphs_MultipleLines_ContainsNewlines()
    {
        var md = MarkdownWriter.WriteParagraphs(new[] { "First", "Second" });
        Assert.Contains("\n", md);
    }

    // ---- WriteLines ----

    [Fact]
    public void WriteLines_SingleLine_ContentPresent()
    {
        var output = MarkdownWriter.WriteLines(new[] { "Line one" });
        Assert.Contains("Line one", output);
    }

    [Fact]
    public void WriteLines_MultipleLines_AllPresent()
    {
        var output = MarkdownWriter.WriteLines(new[] { "A", "B", "C" });
        Assert.Contains("A", output);
        Assert.Contains("B", output);
        Assert.Contains("C", output);
    }

    [Fact]
    public void WriteLines_EmptyList_DoesNotThrow()
    {
        var output = MarkdownWriter.WriteLines(Array.Empty<string>());
        Assert.NotNull(output);
    }

    // ---- Dogfood: combined Markdown document ----

    [Fact]
    public void DogfoodPipeline_HeadingAndParagraphsAndLines_AllPresent()
    {
        var h1   = MarkdownWriter.WriteHeading("Document Title", level: 1);
        var h2   = MarkdownWriter.WriteHeading("Introduction", level: 2);
        var body = MarkdownWriter.WriteParagraphs(new[] { "First para.", "Second para." });
        var list = MarkdownWriter.WriteLines(new[] { "- Item A", "- Item B" });

        var doc = h1 + h2 + body + list;

        Assert.Contains("# Document Title", doc);
        Assert.Contains("## Introduction", doc);
        Assert.Contains("First para.", doc);
        Assert.Contains("Second para.", doc);
        Assert.Contains("Item A", doc);
        Assert.Contains("Item B", doc);
    }
}
