// R103 Train B: FODT .NET GetPlainTextRange tests
// Governed skill: /add-dotnet-object-model-feature
// Ledger: R103-GOVERNED-DOTNET-FODT-GETPLAINTEXTRANGE-001

using System;
using System.IO;
using FormatFactory.Fodt;
using Xunit;

namespace FormatFactory.Fodt.Tests;

public class FodtR103GetPlainTextRangeTests
{
    private static readonly string SamplesDir = Path.GetFullPath(
        Path.Combine(AppContext.BaseDirectory,
            "../../../../../../samples/by-format/fodt"));

    private static string MinimalPath =>
        Path.Combine(SamplesDir, "minimal-document.fodt");

    [Fact]
    public void GetPlainTextRange_FullRange_MatchesGetPlainText()
    {
        var doc = FodtDocument.Load(MinimalPath);
        var full = doc.GetPlainText();
        var range = doc.GetPlainTextRange(0, doc.ParagraphCount);
        Assert.Equal(full, range);
    }

    [Fact]
    public void GetPlainTextRange_SingleParagraph()
    {
        var doc = FodtDocument.Load(MinimalPath);
        if (doc.ParagraphCount == 0) return;
        var range = doc.GetPlainTextRange(0, 1);
        Assert.Equal(doc.Paragraphs[0].Text ?? "", range);
    }

    [Fact]
    public void GetPlainTextRange_EmptyRange_ReturnsEmpty()
    {
        var doc = FodtDocument.Load(MinimalPath);
        var range = doc.GetPlainTextRange(0, 0);
        Assert.Equal(string.Empty, range);
    }

    [Fact]
    public void GetPlainTextRange_NegativeStart_Throws()
    {
        var doc = FodtDocument.Load(MinimalPath);
        Assert.Throws<ArgumentOutOfRangeException>(() => doc.GetPlainTextRange(-1, 1));
    }

    [Fact]
    public void GetPlainTextRange_EndBeyondCount_Throws()
    {
        var doc = FodtDocument.Load(MinimalPath);
        Assert.Throws<ArgumentOutOfRangeException>(
            () => doc.GetPlainTextRange(0, doc.ParagraphCount + 1));
    }

    [Fact]
    public void GetPlainTextRange_StartEqualsEnd_ReturnsEmpty()
    {
        var doc = FodtDocument.Load(MinimalPath);
        if (doc.ParagraphCount < 2) return;
        var range = doc.GetPlainTextRange(1, 1);
        Assert.Equal(string.Empty, range);
    }

    [Fact]
    public void GetPlainTextRange_AfterAppend_IncludesNew()
    {
        var doc = FodtDocument.Load(MinimalPath);
        doc.AppendParagraph("RangeTest");
        int count = doc.ParagraphCount;
        var range = doc.GetPlainTextRange(count - 1, count);
        Assert.Equal("RangeTest", range);
    }

    [Fact]
    public void GetPlainTextRange_MiddleSlice_ContainsExpected()
    {
        var doc = FodtDocument.Load(MinimalPath);
        if (doc.ParagraphCount < 3) return;
        var range = doc.GetPlainTextRange(1, 3);
        Assert.Contains(doc.Paragraphs[1].Text ?? "", range);
        Assert.Contains(doc.Paragraphs[2].Text ?? "", range);
    }
}
