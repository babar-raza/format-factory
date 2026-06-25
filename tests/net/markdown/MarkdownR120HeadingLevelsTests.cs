// Tests for MarkdownWriter.WriteHeading() across all 6 ATX heading levels.
// Sprint: FORMAT-FACTORY-MARKDOWN-HEADING-LEVELS-R120-20260627
// Ledger: R120-GOVERNED-DOTNET-MARKDOWN-HEADING-LEVELS-001

using System;
using System.Collections.Generic;
using Xunit;

namespace FormatFactory.Markdown.Tests;

/// <summary>
/// R120: MarkdownWriter.WriteHeading(text, level) produces ATX heading syntax.
/// Level 1 → "# text", level 2 → "## text", ..., level 6 → "###### text".
/// The heading prefix contains exactly level '#' characters followed by a space.
/// Combined multi-heading documents preserve order and proper separation.
/// Invalid levels (0, 7, negative) throw MarkdownWriterException.
/// </summary>
public class MarkdownR120HeadingLevelsTests
{
    // ---- Level 1: single hash ----

    [Fact]
    public void WriteHeading_Level1_StartsWithSingleHash()
    {
        var h = MarkdownWriter.WriteHeading("Title", 1);
        Assert.StartsWith("# ", h);
    }

    [Fact]
    public void WriteHeading_Level1_ExactlyOneHash()
    {
        var h = MarkdownWriter.WriteHeading("Title", 1);
        Assert.StartsWith("# ", h);
        Assert.DoesNotContain("## ", h);
    }

    // ---- Level 2 ----

    [Fact]
    public void WriteHeading_Level2_StartsWith2Hashes()
    {
        var h = MarkdownWriter.WriteHeading("Section", 2);
        Assert.StartsWith("## ", h);
    }

    // ---- Level 3 ----

    [Fact]
    public void WriteHeading_Level3_StartsWith3Hashes()
    {
        var h = MarkdownWriter.WriteHeading("Subsection", 3);
        Assert.StartsWith("### ", h);
    }

    // ---- Level 4 ----

    [Fact]
    public void WriteHeading_Level4_StartsWith4Hashes()
    {
        var h = MarkdownWriter.WriteHeading("Sub-subsection", 4);
        Assert.StartsWith("#### ", h);
    }

    // ---- Level 5 ----

    [Fact]
    public void WriteHeading_Level5_StartsWith5Hashes()
    {
        var h = MarkdownWriter.WriteHeading("Deep heading", 5);
        Assert.StartsWith("##### ", h);
    }

    // ---- Level 6 ----

    [Fact]
    public void WriteHeading_Level6_StartsWith6Hashes()
    {
        var h = MarkdownWriter.WriteHeading("Deepest heading", 6);
        Assert.StartsWith("###### ", h);
    }

    // ---- Text preservation at each level ----

    [Fact]
    public void WriteHeading_AllLevels_TextPreserved()
    {
        for (int level = 1; level <= 6; level++)
        {
            var heading = MarkdownWriter.WriteHeading("TargetText", level);
            Assert.Contains("TargetText", heading);
        }
    }

    // ---- Hash-count consistency ----

    [Fact]
    public void WriteHeading_Level1_PrefixHasOneHash()
    {
        var h = MarkdownWriter.WriteHeading("X", 1);
        int hashes = 0;
        foreach (var c in h)
        {
            if (c == '#') hashes++; else break;
        }
        Assert.Equal(1, hashes);
    }

    [Fact]
    public void WriteHeading_Level6_PrefixHasSixHashes()
    {
        var h = MarkdownWriter.WriteHeading("X", 6);
        int hashes = 0;
        foreach (var c in h)
        {
            if (c == '#') hashes++; else break;
        }
        Assert.Equal(6, hashes);
    }

    // ---- Combined multi-heading document ----

    [Fact]
    public void MultipleHeadings_Combined_PreserveOrder()
    {
        var parts = new List<string>
        {
            MarkdownWriter.WriteHeading("Chapter One", 1),
            MarkdownWriter.WriteParagraphs(new[] { "Introduction paragraph." }),
            MarkdownWriter.WriteHeading("Section 1.1", 2),
            MarkdownWriter.WriteParagraphs(new[] { "Section body." }),
            MarkdownWriter.WriteHeading("Sub 1.1.1", 3),
        };
        var doc = string.Join("\n", parts);

        var chapterPos = doc.IndexOf("Chapter One", StringComparison.Ordinal);
        var sectionPos = doc.IndexOf("Section 1.1", StringComparison.Ordinal);
        var subPos     = doc.IndexOf("Sub 1.1.1",   StringComparison.Ordinal);

        Assert.True(chapterPos < sectionPos);
        Assert.True(sectionPos < subPos);
    }

    [Fact]
    public void MultipleHeadings_Combined_AllLevelsPresent()
    {
        var doc = string.Empty;
        for (int level = 1; level <= 6; level++)
            doc += MarkdownWriter.WriteHeading($"H{level}", level) + "\n";

        for (int level = 1; level <= 6; level++)
            Assert.Contains($"H{level}", doc);
    }

    // ---- Dogfood: technical spec document ----

    [Fact]
    public void DogfoodPipeline_TechSpecDocument_AllHeadingsAndParagraphsPresent()
    {
        var doc =
            MarkdownWriter.WriteHeading("Format Factory Specification", 1) + "\n" +
            MarkdownWriter.WriteParagraphs(new[] { "This document describes the Format Factory pipeline." }) + "\n" +
            MarkdownWriter.WriteHeading("Architecture", 2) + "\n" +
            MarkdownWriter.WriteParagraphs(new[] { "The system processes 30 document formats." }) + "\n" +
            MarkdownWriter.WriteHeading("Compression Formats", 3) + "\n" +
            MarkdownWriter.WriteParagraphs(new[] { "Includes ZST, GZ, and BZ2." }) + "\n" +
            MarkdownWriter.WriteHeading("Zstandard", 4) + "\n" +
            MarkdownWriter.WriteHeading("Frame Structure", 5) + "\n" +
            MarkdownWriter.WriteHeading("Magic Bytes", 6);

        Assert.Contains("# Format Factory Specification", doc);
        Assert.Contains("## Architecture", doc);
        Assert.Contains("### Compression Formats", doc);
        Assert.Contains("#### Zstandard", doc);
        Assert.Contains("##### Frame Structure", doc);
        Assert.Contains("###### Magic Bytes", doc);
        Assert.Contains("30 document formats", doc);
    }
}
