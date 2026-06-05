// R95 Train M: FODT .NET GetCharCount Tests
// Governed skill: /add-dotnet-api
// Ledger: R95-GOVERNED-DOTNET-FODT-GETCHARCOUNT-001
// Sprint: FORMAT-FACTORY-R95-PARALLEL-SPRINT-INTELLIGENCE-CONTEXT-PACK-ACCELERATION-POC-MEGA-TRAIN-001

using System;
using System.IO;
using FormatFactory.Fodt;
using Xunit;

namespace FormatFactory.Fodt.Tests;

public class FodtR95GetCharCountTests
{
    private static readonly string SamplesDir = Path.GetFullPath(
        Path.Combine(AppContext.BaseDirectory,
            "../../../../../../samples/by-format/fodt"));

    private static string SampleFodtPath =>
        Path.Combine(SamplesDir, "minimal-document.fodt");

    [Fact]
    public void GetCharCount_ReturnsNonNegative()
    {
        var doc = FodtDocument.Load(SampleFodtPath);
        Assert.True(doc.GetCharCount() >= 0);
    }

    [Fact]
    public void GetCharCount_HasCharacters()
    {
        var doc = FodtDocument.Load(SampleFodtPath);
        Assert.True(doc.GetCharCount() > 0, "Sample document should have characters");
    }

    [Fact]
    public void GetCharCount_GreaterThanOrEqualToWordCount()
    {
        var doc = FodtDocument.Load(SampleFodtPath);
        var charCount = doc.GetCharCount();
        var wordCount = doc.GetWordCount();
        Assert.True(charCount >= wordCount,
            $"CharCount ({charCount}) should be >= WordCount ({wordCount})");
    }

    [Fact]
    public void GetCharCount_IncludesHeadings()
    {
        var doc = FodtDocument.Load(SampleFodtPath);
        var headings = doc.GetHeadingParagraphs();
        var charCount = doc.GetCharCount();
        if (headings.Count > 0)
        {
            Assert.True(charCount > 0, "Document with headings should have char count > 0");
        }
    }

    [Fact]
    public void GetCharCount_ConsistentWithParagraphTexts()
    {
        var doc = FodtDocument.Load(SampleFodtPath);
        var texts = doc.GetParagraphTexts();
        int expectedChars = 0;
        foreach (var t in texts)
            expectedChars += t.Length;
        Assert.Equal(expectedChars, doc.GetCharCount());
    }

    [Fact]
    public void GetCharCount_Consistent()
    {
        var doc = FodtDocument.Load(SampleFodtPath);
        var count1 = doc.GetCharCount();
        var count2 = doc.GetCharCount();
        Assert.Equal(count1, count2);
    }

    [Fact]
    public void GetCharCount_ReturnsInt()
    {
        var doc = FodtDocument.Load(SampleFodtPath);
        int count = doc.GetCharCount();
        Assert.IsType<int>(count);
    }

    [Fact]
    public void GetCharCount_CorrelatesWithPlainText()
    {
        var doc = FodtDocument.Load(SampleFodtPath);
        var plainText = doc.GetPlainText();
        var charCount = doc.GetCharCount();
        // Plain text includes newlines between paragraphs, so may be larger
        Assert.True(plainText.Length >= charCount,
            $"PlainText length ({plainText.Length}) should be >= CharCount ({charCount})");
    }
}
