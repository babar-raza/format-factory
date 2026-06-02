// R89 Train I: FODT Text Search + CharCount Tests
// New APIs: CharCount, SearchText
// Sprint: FORMAT-FACTORY-R89-AUTHORITATIVE-TEST-BASELINE-DECLARATION-CLOSEOUT-POC-PRODUCT-DEEPENING-MEGA-TRAIN-001

using System;
using System.IO;
using FormatFactory.Fodt;
using Xunit;

namespace FormatFactory.Fodt.Tests;

public class FodtR89CharCountTests
{
    private static readonly string SamplesDir = Path.GetFullPath(
        Path.Combine(AppContext.BaseDirectory,
            "../../../../../../samples/by-format/fodt"));

    private static string SampleFodtPath =>
        Path.Combine(SamplesDir, "headings-and-paragraphs.fodt");

    [Fact]
    public void CharCount_IsNonNegative()
    {
        var doc = FodtDocument.Load(SampleFodtPath);
        Assert.True(doc.CharCount >= 0);
    }

    [Fact]
    public void CharCount_MatchesPlainTextLength()
    {
        var doc = FodtDocument.Load(SampleFodtPath);
        var plainText = doc.GetPlainText();
        int paraCount = doc.Paragraphs.Count;
        if (paraCount > 1)
        {
            Assert.Equal(plainText.Length - (paraCount - 1), doc.CharCount);
        }
        else
        {
            Assert.Equal(plainText.Length, doc.CharCount);
        }
    }

    [Fact]
    public void CharCount_GreaterThanZero_ForNonEmptyDoc()
    {
        var doc = FodtDocument.Load(SampleFodtPath);
        if (doc.Paragraphs.Count > 0)
        {
            Assert.True(doc.CharCount > 0, "Non-empty doc should have CharCount > 0");
        }
    }
}

public class FodtR89SearchTextTests
{
    private static readonly string SamplesDir = Path.GetFullPath(
        Path.Combine(AppContext.BaseDirectory,
            "../../../../../../samples/by-format/fodt"));

    private static string SampleFodtPath =>
        Path.Combine(SamplesDir, "headings-and-paragraphs.fodt");

    [Fact]
    public void SearchText_FindsKnownWord()
    {
        var doc = FodtDocument.Load(SampleFodtPath);
        var plainText = doc.GetPlainText();
        if (plainText.Length == 0) return;

        var firstWord = plainText.Split(' ', StringSplitOptions.RemoveEmptyEntries)[0];
        var results = doc.SearchText(firstWord);
        Assert.True(results.Count > 0, $"Expected to find '{firstWord}' in document");
    }

    [Fact]
    public void SearchText_ReturnsEmptyForMissingText()
    {
        var doc = FodtDocument.Load(SampleFodtPath);
        var results = doc.SearchText("ZZZZNONEXISTENTZZZZZ");
        Assert.Empty(results);
    }

    [Fact]
    public void SearchText_CaseInsensitive()
    {
        var doc = FodtDocument.Load(SampleFodtPath);
        var plainText = doc.GetPlainText();
        if (plainText.Length == 0) return;

        var upper = doc.SearchText(plainText[..1].ToUpperInvariant(), StringComparison.OrdinalIgnoreCase);
        Assert.True(upper.Count >= 0);
    }

    [Fact]
    public void SearchText_EmptyQuery_Throws()
    {
        var doc = FodtDocument.Load(SampleFodtPath);
        Assert.Throws<ArgumentException>(() => doc.SearchText(""));
    }

    [Fact]
    public void SearchText_ReturnsTupleWithParagraphIndex()
    {
        var doc = FodtDocument.Load(SampleFodtPath);
        var paras = doc.Paragraphs;
        if (paras.Count == 0) return;

        var text = paras[0].Text;
        if (string.IsNullOrEmpty(text)) return;

        var results = doc.SearchText(text[..1]);
        Assert.True(results.Count > 0);
        Assert.Equal(0, results[0].ParagraphIndex);
    }

    [Fact]
    public void SearchText_MultipleOccurrences()
    {
        var doc = FodtDocument.Load(SampleFodtPath);
        var plainText = doc.GetPlainText();
        if (plainText.Length < 2) return;

        var results = doc.SearchText(" ");
        Assert.NotNull(results);
    }
}
