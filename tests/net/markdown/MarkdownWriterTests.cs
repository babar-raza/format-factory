// FormatFactory.Markdown.Tests — MarkdownWriter unit tests
// Sprint: FORMAT-FACTORY-DOTNET-TARGET-WRITER-MWP-DOGFOOD-UNBLOCKING-001

using System;
using System.Collections.Generic;
using System.IO;
using FormatFactory.Markdown;
using Xunit;

namespace FormatFactory.Markdown.Tests;

public class MarkdownWriterTests
{
    // -------------------------------------------------------------------------
    // WriteHeading
    // -------------------------------------------------------------------------

    [Fact]
    public void WriteHeading_Level1_SingleHash()
    {
        Assert.Equal("# Title", MarkdownWriter.WriteHeading("Title", 1));
    }

    [Fact]
    public void WriteHeading_Level2_TwoHashes()
    {
        Assert.Equal("## Section", MarkdownWriter.WriteHeading("Section", 2));
    }

    [Fact]
    public void WriteHeading_Level6_SixHashes()
    {
        Assert.Equal("###### Deep", MarkdownWriter.WriteHeading("Deep", 6));
    }

    [Fact]
    public void WriteHeading_LevelAbove6_ClampedTo6()
    {
        var result = MarkdownWriter.WriteHeading("X", 10);
        Assert.StartsWith("######", result);
    }

    [Fact]
    public void WriteHeading_LevelBelow1_ClampedTo1()
    {
        var result = MarkdownWriter.WriteHeading("X", 0);
        Assert.StartsWith("# ", result);
        Assert.False(result.StartsWith("## "), "Level 0 should clamp to # not ##");
    }

    [Fact]
    public void WriteHeading_NullText_HandledGracefully()
    {
        var result = MarkdownWriter.WriteHeading(null!, 1);
        Assert.Equal("# ", result);
    }

    // -------------------------------------------------------------------------
    // WriteParagraphs
    // -------------------------------------------------------------------------

    [Fact]
    public void WriteParagraphs_TwoParagraphs_JoinedWithLf()
    {
        var result = MarkdownWriter.WriteParagraphs(new[] { "Hello", "World" });
        Assert.Equal("Hello\nWorld", result);
    }

    [Fact]
    public void WriteParagraphs_NullParagraph_TreatedAsEmpty()
    {
        var result = MarkdownWriter.WriteParagraphs(new string?[] { "a", null });
        Assert.Equal("a\n", result);
    }

    [Fact]
    public void WriteParagraphs_Empty_ReturnsEmpty()
    {
        var result = MarkdownWriter.WriteParagraphs(new List<string?>());
        Assert.Equal(string.Empty, result);
    }

    // -------------------------------------------------------------------------
    // WriteLinesToFile — physical file output
    // -------------------------------------------------------------------------

    [Fact]
    public void WriteLinesToFile_CreatesFile()
    {
        var path = Path.Combine(Path.GetTempPath(), $"ff_md_test_{Guid.NewGuid():N}.md");
        try
        {
            MarkdownWriter.WriteLinesToFile(new[] { "# Title", "paragraph" }, path);
            Assert.True(File.Exists(path));
            var content = File.ReadAllText(path);
            Assert.Contains("# Title", content);
            Assert.Contains("paragraph", content);
        }
        finally
        {
            if (File.Exists(path)) File.Delete(path);
        }
    }

    [Fact]
    public void WriteLinesToFile_NullPath_Throws()
    {
        Assert.Throws<MarkdownWriterException>(() =>
            MarkdownWriter.WriteLinesToFile(new[] { "x" }, null!));
    }
}
