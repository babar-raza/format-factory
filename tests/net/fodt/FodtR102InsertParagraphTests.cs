// R102 Train B: FODT .NET InsertParagraph tests
// Governed skill: /add-dotnet-object-model-feature
// Ledger: R102-GOVERNED-DOTNET-FODT-INSERTPARAGRAPH-001

using System;
using System.IO;
using FormatFactory.Fodt;
using Xunit;

namespace FormatFactory.Fodt.Tests;

public class FodtR102InsertParagraphTests
{
    private static readonly string SamplesDir = Path.GetFullPath(
        Path.Combine(AppContext.BaseDirectory,
            "../../../../../../samples/by-format/fodt"));

    private static string MinimalPath =>
        Path.Combine(SamplesDir, "minimal-document.fodt");

    [Fact]
    public void InsertParagraph_AtZero_BecomesFirst()
    {
        var doc = FodtDocument.Load(MinimalPath);
        doc.InsertParagraph(0, "InsertedFirst");
        Assert.Equal("InsertedFirst", doc.Paragraphs[0].Text);
    }

    [Fact]
    public void InsertParagraph_IncreasesCount()
    {
        var doc = FodtDocument.Load(MinimalPath);
        int before = doc.ParagraphCount;
        doc.InsertParagraph(0, "New");
        Assert.Equal(before + 1, doc.ParagraphCount);
    }

    [Fact]
    public void InsertParagraph_AtEnd_SameAsAppend()
    {
        var doc = FodtDocument.Load(MinimalPath);
        int count = doc.ParagraphCount;
        doc.InsertParagraph(count, "AtEnd");
        Assert.Equal("AtEnd", doc.Paragraphs[doc.ParagraphCount - 1].Text);
    }

    [Fact]
    public void InsertParagraph_NegativeIndex_Throws()
    {
        var doc = FodtDocument.Load(MinimalPath);
        Assert.Throws<ArgumentOutOfRangeException>(() => doc.InsertParagraph(-1, "Bad"));
    }

    [Fact]
    public void InsertParagraph_OutOfRange_Throws()
    {
        var doc = FodtDocument.Load(MinimalPath);
        int count = doc.ParagraphCount;
        Assert.Throws<ArgumentOutOfRangeException>(() => doc.InsertParagraph(count + 1, "Bad"));
    }

    [Fact]
    public void InsertParagraph_PreservesExisting()
    {
        var doc = FodtDocument.Load(MinimalPath);
        var originalTexts = doc.GetParagraphTexts();
        doc.InsertParagraph(0, "Prepended");
        var newTexts = doc.GetParagraphTexts();
        for (int i = 0; i < originalTexts.Count; i++)
            Assert.Equal(originalTexts[i], newTexts[i + 1]);
    }

    [Fact]
    public void InsertParagraph_PersistsAfterSaveReload()
    {
        var doc = FodtDocument.Load(MinimalPath);
        doc.InsertParagraph(0, "Persisted");
        var tmp = Path.GetTempFileName() + ".fodt";
        try
        {
            doc.Save(tmp);
            var reloaded = FodtDocument.Load(tmp);
            Assert.Equal("Persisted", reloaded.Paragraphs[0].Text);
        }
        finally { if (File.Exists(tmp)) File.Delete(tmp); }
    }

    [Fact]
    public void InsertParagraph_Middle_CorrectPosition()
    {
        var doc = FodtDocument.Load(MinimalPath);
        if (doc.ParagraphCount < 2) return; // need at least 2 paragraphs
        doc.InsertParagraph(1, "Middle");
        Assert.Equal("Middle", doc.Paragraphs[1].Text);
    }
}
