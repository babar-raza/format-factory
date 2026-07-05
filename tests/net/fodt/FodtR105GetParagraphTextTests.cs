// R105 Wave 2: FODT .NET GetParagraphText tests
// Governed skill: /add-dotnet-api
// Ledger: R105-GOVERNED-DOTNET-FODT-GETPARAGRAPHTEXT-001

using System;
using System.IO;
using FormatFactory.Fodt;
using Xunit;

namespace FormatFactory.Fodt.Tests;

public class FodtR105GetParagraphTextTests
{
    private static readonly string SamplesDir = Path.GetFullPath(
        Path.Combine(AppContext.BaseDirectory,
            "../../../../../../samples/by-format/fodt"));

    private static string MinimalPath =>
        Path.Combine(SamplesDir, "minimal-document.fodt");

    [Fact]
    public void GetParagraphText_ValidIndex_ReturnsText()
    {
        var doc = FodtDocument.Load(MinimalPath);
        var text = doc.GetParagraphText(0);
        Assert.NotNull(text);
    }

    [Fact]
    public void GetParagraphText_NegativeIndex_ReturnsNull()
    {
        var doc = FodtDocument.Load(MinimalPath);
        Assert.ThrowsAny<Exception>(() => doc.GetParagraphText(-1));
    }

    [Fact]
    public void GetParagraphText_OutOfRange_ReturnsNull()
    {
        var doc = FodtDocument.Load(MinimalPath);
        Assert.ThrowsAny<Exception>(() => doc.GetParagraphText(9999));
    }

    [Fact]
    public void GetParagraphText_MatchesParagraphsProperty()
    {
        var doc = FodtDocument.Load(MinimalPath);
        for (int i = 0; i < doc.ParagraphCount; i++)
            Assert.Equal(doc.Paragraphs[i].Text, doc.GetParagraphText(i));
    }

    [Fact]
    public void GetParagraphText_AfterEdit_ReflectsChange()
    {
        var doc = FodtDocument.Load(MinimalPath);
        doc.SetParagraphText(0, "Modified");
        Assert.Equal("Modified", doc.GetParagraphText(0));
    }

    [Fact]
    public void GetParagraphText_AfterAppend_ReturnsNew()
    {
        var doc = FodtDocument.Load(MinimalPath);
        doc.AppendParagraph("Appended");
        Assert.Equal("Appended", doc.GetParagraphText(doc.ParagraphCount - 1));
    }

    [Fact]
    public void GetParagraphText_AllIndices()
    {
        var doc = FodtDocument.Load(MinimalPath);
        for (int i = 0; i < doc.ParagraphCount; i++)
            Assert.NotNull(doc.GetParagraphText(i));
    }

    [Fact]
    public void GetParagraphText_PersistsAfterSaveReload()
    {
        var doc = FodtDocument.Load(MinimalPath);
        doc.SetParagraphText(0, "Persist");
        var tmp = Path.GetTempFileName() + ".fodt";
        try
        {
            doc.Save(tmp);
            var reloaded = FodtDocument.Load(tmp);
            Assert.Equal("Persist", reloaded.GetParagraphText(0));
        }
        finally { if (File.Exists(tmp)) File.Delete(tmp); }
    }
}
