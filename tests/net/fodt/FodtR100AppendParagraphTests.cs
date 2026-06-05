// R100 Train C: FODT .NET AppendParagraph deep product lane tests
// Governed skill: /add-dotnet-api
// Ledger: R100-GOVERNED-DOTNET-FODT-APPENDPARAGRAPH-001

using System;
using System.IO;
using FormatFactory.Fodt;
using Xunit;

namespace FormatFactory.Fodt.Tests;

public class FodtR100AppendParagraphTests
{
    private static readonly string SamplesDir = Path.GetFullPath(
        Path.Combine(AppContext.BaseDirectory,
            "../../../../../../samples/by-format/fodt"));

    private static string MinimalPath =>
        Path.Combine(SamplesDir, "minimal-document.fodt");

    [Fact]
    public void AppendParagraph_IncreasesCount()
    {
        var doc = FodtDocument.Load(MinimalPath);
        int before = doc.GetParagraphCount();
        doc.AppendParagraph("New paragraph");
        Assert.Equal(before + 1, doc.GetParagraphCount());
    }

    [Fact]
    public void AppendParagraph_TextIsAccessible()
    {
        var doc = FodtDocument.Load(MinimalPath);
        var p = doc.AppendParagraph("R100-TEST-CONTENT");
        Assert.Equal("R100-TEST-CONTENT", p.Text);
    }

    [Fact]
    public void AppendParagraph_IsNotHeading()
    {
        var doc = FodtDocument.Load(MinimalPath);
        var p = doc.AppendParagraph("Plain paragraph");
        Assert.False(p.IsHeading);
    }

    [Fact]
    public void AppendParagraph_PersistsAfterSaveReload()
    {
        var doc = FodtDocument.Load(MinimalPath);
        doc.AppendParagraph("PERSIST-R100");
        var tmp = Path.GetTempFileName() + ".fodt";
        try
        {
            doc.Save(tmp);
            var reloaded = FodtDocument.Load(tmp);
            var texts = reloaded.GetParagraphTexts();
            Assert.Contains("PERSIST-R100", texts);
        }
        finally { if (File.Exists(tmp)) File.Delete(tmp); }
    }

    [Fact]
    public void AppendParagraph_InPlainText()
    {
        var doc = FodtDocument.Load(MinimalPath);
        doc.AppendParagraph("PLAINTEXT-CHECK");
        Assert.Contains("PLAINTEXT-CHECK", doc.GetPlainText());
    }

    [Fact]
    public void AppendParagraph_WordCountIncreases()
    {
        var doc = FodtDocument.Load(MinimalPath);
        int before = doc.GetWordCount();
        doc.AppendParagraph("three new words");
        Assert.Equal(before + 3, doc.GetWordCount());
    }

    [Fact]
    public void AppendParagraph_MultipleAppends()
    {
        var doc = FodtDocument.Load(MinimalPath);
        int before = doc.GetParagraphCount();
        doc.AppendParagraph("First");
        doc.AppendParagraph("Second");
        doc.AppendParagraph("Third");
        Assert.Equal(before + 3, doc.GetParagraphCount());
    }

    [Fact]
    public void AppendParagraph_EmptyString_Works()
    {
        var doc = FodtDocument.Load(MinimalPath);
        var p = doc.AppendParagraph("");
        Assert.Equal("", p.Text);
    }

    [Fact]
    public void AppendParagraph_SearchText_FindsIt()
    {
        var doc = FodtDocument.Load(MinimalPath);
        doc.AppendParagraph("UNIQUE-SEARCH-R100");
        var results = doc.SearchText("UNIQUE-SEARCH-R100");
        Assert.NotEmpty(results);
    }

    [Fact]
    public void AppendParagraph_CharCountIncreases()
    {
        var doc = FodtDocument.Load(MinimalPath);
        int before = doc.GetCharCount();
        doc.AppendParagraph("ABCDE");
        Assert.Equal(before + 5, doc.GetCharCount());
    }
}
