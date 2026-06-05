// R106 Wave 2: FODT GetTextBetweenParagraphs tests
// Ledger: R106-GOVERNED-DOTNET-FODT-GETTEXTBETWEEN-001

using System;
using System.IO;
using FormatFactory.Fodt;
using Xunit;

namespace FormatFactory.Fodt.Tests;

public class FodtR106GetTextBetweenTests
{
    private static readonly string SamplesDir = Path.GetFullPath(
        Path.Combine(AppContext.BaseDirectory,
            "../../../../../../samples/by-format/fodt"));

    private static string MinimalPath =>
        Path.Combine(SamplesDir, "minimal-document.fodt");

    [Fact]
    public void GetTextBetween_ValidRange_ReturnsText()
    {
        var doc = FodtDocument.Load(MinimalPath);
        if (doc.ParagraphCount >= 2)
        {
            var text = doc.GetTextBetweenParagraphs(0, 2);
            Assert.NotNull(text);
            Assert.Contains("\n", text);
        }
    }

    [Fact]
    public void GetTextBetween_SingleParagraph()
    {
        var doc = FodtDocument.Load(MinimalPath);
        doc.RemoveAllParagraphs();
        doc.AppendParagraph("Only");
        var text = doc.GetTextBetweenParagraphs(0, 1);
        Assert.Equal("Only", text);
    }

    [Fact]
    public void GetTextBetween_MultipleParagraphs()
    {
        var doc = FodtDocument.Load(MinimalPath);
        doc.RemoveAllParagraphs();
        doc.AppendParagraph("First");
        doc.AppendParagraph("Second");
        doc.AppendParagraph("Third");
        var text = doc.GetTextBetweenParagraphs(0, 3);
        Assert.Equal("First\nSecond\nThird", text);
    }

    [Fact]
    public void GetTextBetween_PartialRange()
    {
        var doc = FodtDocument.Load(MinimalPath);
        doc.RemoveAllParagraphs();
        doc.AppendParagraph("A");
        doc.AppendParagraph("B");
        doc.AppendParagraph("C");
        var text = doc.GetTextBetweenParagraphs(1, 3);
        Assert.Equal("B\nC", text);
    }

    [Fact]
    public void GetTextBetween_NegativeStart_ReturnsNull()
    {
        var doc = FodtDocument.Load(MinimalPath);
        Assert.Null(doc.GetTextBetweenParagraphs(-1, 1));
    }

    [Fact]
    public void GetTextBetween_StartEqualsEnd_ReturnsNull()
    {
        var doc = FodtDocument.Load(MinimalPath);
        Assert.Null(doc.GetTextBetweenParagraphs(0, 0));
    }

    [Fact]
    public void GetTextBetween_StartGreaterThanEnd_ReturnsNull()
    {
        var doc = FodtDocument.Load(MinimalPath);
        Assert.Null(doc.GetTextBetweenParagraphs(2, 1));
    }

    [Fact]
    public void GetTextBetween_EndBeyondCount_ReturnsNull()
    {
        var doc = FodtDocument.Load(MinimalPath);
        Assert.Null(doc.GetTextBetweenParagraphs(0, 9999));
    }
}
