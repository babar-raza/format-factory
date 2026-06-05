// R104 Wave 1: FODT .NET GetDocumentStats tests
// Governed skill: /add-dotnet-api
// Ledger: R104-GOVERNED-DOTNET-FODT-GETDOCUMENTSTATS-001

using System;
using System.IO;
using FormatFactory.Fodt;
using Xunit;

namespace FormatFactory.Fodt.Tests;

public class FodtR104GetDocumentStatsTests
{
    private static readonly string SamplesDir = Path.GetFullPath(
        Path.Combine(AppContext.BaseDirectory,
            "../../../../../../samples/by-format/fodt"));

    private static string MinimalPath =>
        Path.Combine(SamplesDir, "minimal-document.fodt");

    private static string HeadingsPath =>
        Path.Combine(SamplesDir, "headings-and-paragraphs.fodt");

    [Fact]
    public void GetDocumentStats_MinimalDocument_HasParagraphs()
    {
        var doc = FodtDocument.Load(MinimalPath);
        var stats = doc.GetDocumentStats();
        Assert.True(stats.ParagraphCount > 0);
    }

    [Fact]
    public void GetDocumentStats_WordCountMatchesProperty()
    {
        var doc = FodtDocument.Load(MinimalPath);
        var stats = doc.GetDocumentStats();
        Assert.Equal(doc.GetWordCount(), stats.WordCount);
    }

    [Fact]
    public void GetDocumentStats_CharCountMatchesProperty()
    {
        var doc = FodtDocument.Load(MinimalPath);
        var stats = doc.GetDocumentStats();
        Assert.Equal(doc.GetCharCount(), stats.CharCount);
    }

    [Fact]
    public void GetDocumentStats_ParagraphCountMatchesProperty()
    {
        var doc = FodtDocument.Load(MinimalPath);
        var stats = doc.GetDocumentStats();
        Assert.Equal(doc.GetParagraphCount(), stats.ParagraphCount);
    }

    [Fact]
    public void GetDocumentStats_HeadingCountMatchesMethod()
    {
        var doc = FodtDocument.Load(HeadingsPath);
        var stats = doc.GetDocumentStats();
        Assert.Equal(doc.GetHeadingCount(), stats.HeadingCount);
    }

    [Fact]
    public void GetDocumentStats_AfterAppend_Increments()
    {
        var doc = FodtDocument.Load(MinimalPath);
        var before = doc.GetDocumentStats();
        doc.AppendParagraph("extra words here");
        var after = doc.GetDocumentStats();
        Assert.Equal(before.ParagraphCount + 1, after.ParagraphCount);
        Assert.True(after.WordCount > before.WordCount);
    }

    [Fact]
    public void GetDocumentStats_AfterRemove_Decrements()
    {
        var doc = FodtDocument.Load(MinimalPath);
        doc.AppendParagraph("removable");
        var before = doc.GetDocumentStats();
        doc.RemoveParagraph(doc.ParagraphCount - 1);
        var after = doc.GetDocumentStats();
        Assert.Equal(before.ParagraphCount - 1, after.ParagraphCount);
    }

    [Fact]
    public void GetDocumentStats_AllFieldsNonNegative()
    {
        var doc = FodtDocument.Load(MinimalPath);
        var stats = doc.GetDocumentStats();
        Assert.True(stats.WordCount >= 0);
        Assert.True(stats.CharCount >= 0);
        Assert.True(stats.ParagraphCount >= 0);
        Assert.True(stats.HeadingCount >= 0);
    }

    [Fact]
    public void GetDocumentStats_TupleDestructuring()
    {
        var doc = FodtDocument.Load(MinimalPath);
        var (words, chars, paras, headings) = doc.GetDocumentStats();
        Assert.True(words >= 0);
        Assert.True(chars >= 0);
        Assert.True(paras >= 0);
        Assert.True(headings >= 0);
    }
}
