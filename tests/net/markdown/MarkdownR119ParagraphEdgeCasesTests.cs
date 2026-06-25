// Tests for MarkdownWriter edge cases: WriteParagraphs CRLF, WriteHeading special chars,
// WriteParagraphs large counts, and combined output correctness.
// Sprint: FORMAT-FACTORY-MARKDOWN-WRITER-R119-20260626
// Ledger: R119-GOVERNED-DOTNET-MARKDOWN-PARAGRAPH-EDGECASES-001

using System;
using System.Collections.Generic;
using System.Linq;
using Xunit;

namespace FormatFactory.Markdown.Tests;

/// <summary>
/// R119: MarkdownWriter edge cases — WriteParagraphs normalizes CRLF inputs to LF,
/// WriteHeading handles special characters in text, large paragraph counts produce
/// the correct separator count, and combined heading+paragraph output composes correctly.
/// </summary>
public class MarkdownR119ParagraphEdgeCasesTests
{
    // ---- WriteParagraphs: CRLF normalization ----

    [Fact]
    public void WriteParagraphs_CrLfInInput_NormalizedToLf()
    {
        var result = MarkdownWriter.WriteParagraphs(new[] { "Line A\r\nLine A continued", "Line B" });
        Assert.DoesNotContain("\r\n", result);
        Assert.Contains("\n", result);
    }

    [Fact]
    public void WriteParagraphs_BareCarriageReturn_Handled()
    {
        var result = MarkdownWriter.WriteParagraphs(new[] { "before\rafter", "next" });
        // Should not crash and should still contain the textual content
        Assert.Contains("before", result);
        Assert.Contains("next", result);
    }

    // ---- WriteParagraphs: large input ----

    [Fact]
    public void WriteParagraphs_TenParagraphs_NineNewlinesPresent()
    {
        var paras = Enumerable.Range(1, 10).Select(i => $"Paragraph {i}").ToList();
        var result = MarkdownWriter.WriteParagraphs(paras);
        var newlineCount = result.Count(c => c == '\n');
        Assert.Equal(9, newlineCount);
    }

    [Fact]
    public void WriteParagraphs_AllNullEntries_ProducesNewlinesOnly()
    {
        var result = MarkdownWriter.WriteParagraphs(new string?[] { null, null, null });
        // Three null entries joined by LF → "\n\n"
        Assert.Equal("\n\n", result);
    }

    // ---- WriteHeading: special characters in text ----

    [Fact]
    public void WriteHeading_TextWithAmpersand_AmpersandPreservedVerbatim()
    {
        // Markdown does not HTML-escape heading text
        var result = MarkdownWriter.WriteHeading("Rock & Roll", 1);
        Assert.Contains("Rock & Roll", result);
        Assert.DoesNotContain("&amp;", result);
    }

    [Fact]
    public void WriteHeading_TextWithHashInBody_NotConfusedWithLevel()
    {
        // The # in text should appear after the level prefix
        var result = MarkdownWriter.WriteHeading("C# Programming", 2);
        Assert.StartsWith("## ", result);
        Assert.Contains("C#", result);
    }

    [Fact]
    public void WriteHeading_EmptyString_ProducesJustHashPrefix()
    {
        var result = MarkdownWriter.WriteHeading(string.Empty, 3);
        Assert.Equal("### ", result);
    }

    // ---- Combined heading + paragraphs output ----

    [Fact]
    public void Combined_HeadingPlusParagraphs_OrderPreserved()
    {
        var heading  = MarkdownWriter.WriteHeading("Introduction", 1);
        var body     = MarkdownWriter.WriteParagraphs(new[] { "First sentence.", "Second sentence." });
        var combined = $"{heading}\n{body}";

        var posH = combined.IndexOf("# Introduction", StringComparison.Ordinal);
        var posB = combined.IndexOf("First sentence.", StringComparison.Ordinal);

        Assert.True(posH >= 0);
        Assert.True(posB > posH, "Body should appear after heading");
    }

    [Fact]
    public void Combined_H2PlusBodyPlusH3_AllThreeSectionsPresent()
    {
        var section1 = MarkdownWriter.WriteHeading("Background", 2);
        var para1    = MarkdownWriter.WriteParagraphs(new[] { "Background text here." });
        var section2 = MarkdownWriter.WriteHeading("Detail", 3);
        var para2    = MarkdownWriter.WriteParagraphs(new[] { "Detail text here." });

        var doc = string.Join("\n", section1, para1, section2, para2);

        Assert.Contains("## Background",  doc);
        Assert.Contains("Background text", doc);
        Assert.Contains("### Detail",     doc);
        Assert.Contains("Detail text",    doc);
    }

    // ---- Dogfood: technical specification document ----

    [Fact]
    public void DogfoodPipeline_TechSpecDocument_CorrectMarkdownStructure()
    {
        var lines = new List<string>
        {
            MarkdownWriter.WriteHeading("Format Factory: TXT Writer Spec", 1),
            MarkdownWriter.WriteParagraphs(new[] { "This specification describes the TXT output writer." }),
            MarkdownWriter.WriteHeading("Requirements", 2),
            MarkdownWriter.WriteParagraphs(new[] {
                "REQ-001: Output is UTF-8 without BOM.",
                "REQ-002: Line endings are LF (not CRLF).",
                "REQ-003: Null lines are treated as empty strings."
            }),
            MarkdownWriter.WriteHeading("API Surface", 2),
            MarkdownWriter.WriteParagraphs(new[] {
                "WriteLines(lines) → string",
                "WriteLinesToFile(lines, path) → void"
            }),
            MarkdownWriter.WriteHeading("Error Handling", 3),
            MarkdownWriter.WriteParagraphs(new[] { "Null or empty path throws TxtWriterException." }),
        };

        var doc = string.Join("\n", lines);

        // Structural markers
        Assert.Contains("# Format Factory",  doc);
        Assert.Contains("## Requirements",   doc);
        Assert.Contains("## API Surface",    doc);
        Assert.Contains("### Error Handling",doc);

        // Content
        Assert.Contains("UTF-8 without BOM", doc);
        Assert.Contains("WriteLinesToFile",  doc);
        Assert.Contains("TxtWriterException",doc);
    }
}
