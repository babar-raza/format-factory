// R104 Wave 1: FODT .NET SetParagraphText tests
// Governed skill: /add-dotnet-api
// Ledger: R104-GOVERNED-DOTNET-FODT-SETPARAGRAPHTEXT-001

using System;
using System.IO;
using FormatFactory.Fodt;
using Xunit;

namespace FormatFactory.Fodt.Tests;

public class FodtR104SetParagraphTextTests
{
    private static readonly string SamplesDir = Path.GetFullPath(
        Path.Combine(AppContext.BaseDirectory,
            "../../../../../../samples/by-format/fodt"));

    private static string MinimalPath =>
        Path.Combine(SamplesDir, "minimal-document.fodt");

    [Fact]
    public void SetParagraphText_ChangesText()
    {
        var doc = FodtDocument.Load(MinimalPath);
        doc.SetParagraphText(0, "Replaced");
        Assert.Equal("Replaced", doc.Paragraphs[0].Text);
    }

    [Fact]
    public void SetParagraphText_OtherParagraphsUnchanged()
    {
        var doc = FodtDocument.Load(MinimalPath);
        if (doc.ParagraphCount < 2) doc.AppendParagraph("Second");
        var secondText = doc.Paragraphs[1].Text;
        doc.SetParagraphText(0, "Changed");
        Assert.Equal(secondText, doc.Paragraphs[1].Text);
    }

    [Fact]
    public void SetParagraphText_EmptyString()
    {
        var doc = FodtDocument.Load(MinimalPath);
        doc.SetParagraphText(0, "");
        Assert.Equal("", doc.Paragraphs[0].Text);
    }

    [Fact]
    public void SetParagraphText_NegativeIndex_Throws()
    {
        var doc = FodtDocument.Load(MinimalPath);
        Assert.Throws<ArgumentOutOfRangeException>(() => doc.SetParagraphText(-1, "Bad"));
    }

    [Fact]
    public void SetParagraphText_OutOfRange_Throws()
    {
        var doc = FodtDocument.Load(MinimalPath);
        Assert.Throws<ArgumentOutOfRangeException>(() => doc.SetParagraphText(doc.ParagraphCount, "Bad"));
    }

    [Fact]
    public void SetParagraphText_PersistsAfterSaveReload()
    {
        var doc = FodtDocument.Load(MinimalPath);
        doc.SetParagraphText(0, "Persistent");
        var tmp = Path.GetTempFileName() + ".fodt";
        try
        {
            doc.Save(tmp);
            var reloaded = FodtDocument.Load(tmp);
            Assert.Equal("Persistent", reloaded.Paragraphs[0].Text);
        }
        finally { if (File.Exists(tmp)) File.Delete(tmp); }
    }

    [Fact]
    public void SetParagraphText_PreservesParagraphCount()
    {
        var doc = FodtDocument.Load(MinimalPath);
        int count = doc.ParagraphCount;
        doc.SetParagraphText(0, "New content");
        Assert.Equal(count, doc.ParagraphCount);
    }

    [Fact]
    public void SetParagraphText_AffectsPlainText()
    {
        var doc = FodtDocument.Load(MinimalPath);
        doc.SetParagraphText(0, "Updated");
        Assert.Contains("Updated", doc.GetPlainText());
    }

    [Fact]
    public void SetParagraphText_AffectsWordCount()
    {
        var doc = FodtDocument.Load(MinimalPath);
        doc.SetParagraphText(0, "one two three four five");
        Assert.True(doc.WordCount >= 5);
    }

    [Fact]
    public void SetParagraphText_MultipleEdits()
    {
        var doc = FodtDocument.Load(MinimalPath);
        doc.SetParagraphText(0, "First edit");
        doc.SetParagraphText(0, "Second edit");
        Assert.Equal("Second edit", doc.Paragraphs[0].Text);
    }
}
