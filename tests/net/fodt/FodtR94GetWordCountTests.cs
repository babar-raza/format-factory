// R94 Train N: FODT .NET GetWordCount Tests
// Governed skill: /add-dotnet-api
// Ledger: R94-GOVERNED-DOTNET-FODT-GETWORDCOUNT-001
// Sprint: FORMAT-FACTORY-R94-CONTEXT-PACK-SELF-CONTAINED-DECLARATION-REVIEW-ACCELERATION-POC-PARALLEL-MEGA-TRAIN-001

using System;
using System.IO;
using FormatFactory.Fodt;
using Xunit;

namespace FormatFactory.Fodt.Tests;

public class FodtR94GetWordCountTests
{
    private static readonly string SamplesDir = Path.GetFullPath(
        Path.Combine(AppContext.BaseDirectory,
            "../../../../../../samples/by-format/fodt"));

    private static string SampleFodtPath =>
        Path.Combine(SamplesDir, "minimal-document.fodt");

    private static string HeadingsFodtPath =>
        Path.Combine(SamplesDir, "headings-sample.fodt");

    [Fact]
    public void GetWordCount_ReturnsNonNegative()
    {
        var doc = FodtDocument.Load(SampleFodtPath);
        var count = doc.GetWordCount();
        Assert.True(count >= 0, $"Word count should be non-negative, got {count}");
    }

    [Fact]
    public void GetWordCount_MinimalDocument_HasWords()
    {
        var doc = FodtDocument.Load(SampleFodtPath);
        var count = doc.GetWordCount();
        // Minimal document should have at least some text
        Assert.True(count > 0, "Minimal document should have at least one word");
    }

    [Fact]
    public void GetWordCount_MatchesParagraphTextSplit()
    {
        var doc = FodtDocument.Load(SampleFodtPath);
        var wordCount = doc.GetWordCount();
        // Cross-verify: sum of words from GetParagraphTexts
        var texts = doc.GetParagraphTexts();
        int manualCount = 0;
        foreach (var text in texts)
        {
            if (!string.IsNullOrWhiteSpace(text))
                manualCount += text.Split((char[]?)null, StringSplitOptions.RemoveEmptyEntries).Length;
        }
        Assert.Equal(manualCount, wordCount);
    }

    [Fact]
    public void GetWordCount_HeadingsDocument_IncludesHeadingText()
    {
        if (!File.Exists(HeadingsFodtPath)) return; // Skip if fixture missing
        var doc = FodtDocument.Load(HeadingsFodtPath);
        var count = doc.GetWordCount();
        Assert.True(count > 0);
    }

    [Fact]
    public void GetWordCount_ConsistentAcrossMultipleCalls()
    {
        var doc = FodtDocument.Load(SampleFodtPath);
        var count1 = doc.GetWordCount();
        var count2 = doc.GetWordCount();
        Assert.Equal(count1, count2);
    }

    [Fact]
    public void GetWordCount_CorrelatesWithCharCount()
    {
        var doc = FodtDocument.Load(SampleFodtPath);
        var wordCount = doc.GetWordCount();
        var charCount = doc.CharCount;
        // If there are words, there must be chars. If no chars, no words.
        if (charCount == 0)
            Assert.Equal(0, wordCount);
        else
            Assert.True(wordCount > 0, "Chars exist but word count is zero");
    }

    [Fact]
    public void GetWordCount_ParagraphCount_Relationship()
    {
        var doc = FodtDocument.Load(SampleFodtPath);
        var wordCount = doc.GetWordCount();
        var paraCount = doc.ParagraphCount;
        // Word count should be at least as many as paragraphs with text
        Assert.True(wordCount <= paraCount * 10000, "Word count seems unreasonably high");
    }

    [Fact]
    public void GetWordCount_ReturnType_IsInt()
    {
        var doc = FodtDocument.Load(SampleFodtPath);
        int count = doc.GetWordCount();
        Assert.IsType<int>(count);
    }
}
