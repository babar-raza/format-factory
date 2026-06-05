// R101 Train C: FODT .NET InsertParagraph deep product lane tests
// Governed skill: /add-dotnet-api
// Ledger: R101-GOVERNED-DOTNET-FODT-INSERTPARAGRAPH-001

using System;
using System.IO;
using FormatFactory.Fodt;
using Xunit;

namespace FormatFactory.Fodt.Tests;

public class FodtR101InsertParagraphTests
{
    private static readonly string SamplesDir = Path.GetFullPath(
        Path.Combine(AppContext.BaseDirectory,
            "../../../../../../samples/by-format/fodt"));

    private static string MinimalPath =>
        Path.Combine(SamplesDir, "minimal-document.fodt");

    [Fact]
    public void InsertParagraph_AtZero_BecomeFirst()
    {
        var doc = FodtDocument.Load(MinimalPath);
        doc.InsertParagraph(0, "Inserted");
        Assert.Equal("Inserted", doc.Paragraphs[0].Text);
    }

    [Fact]
    public void InsertParagraph_AtEnd_SameAsAppend()
    {
        var doc = FodtDocument.Load(MinimalPath);
        int count = doc.ParagraphCount;
        doc.InsertParagraph(count, "AtEnd");
        Assert.Equal("AtEnd", doc.Paragraphs[count].Text);
    }

    [Fact]
    public void InsertParagraph_InMiddle_ShiftsOthers()
    {
        var doc = FodtDocument.Load(MinimalPath);
        if (doc.ParagraphCount < 2)
        {
            doc.AppendParagraph("P1");
            doc.AppendParagraph("P2");
        }
        var textBefore = doc.Paragraphs[1].Text;
        doc.InsertParagraph(1, "Middle");
        Assert.Equal("Middle", doc.Paragraphs[1].Text);
        Assert.Equal(textBefore, doc.Paragraphs[2].Text);
    }

    [Fact]
    public void InsertParagraph_IncreasesParagraphCount()
    {
        var doc = FodtDocument.Load(MinimalPath);
        int before = doc.ParagraphCount;
        doc.InsertParagraph(0, "New");
        Assert.Equal(before + 1, doc.ParagraphCount);
    }

    [Fact]
    public void InsertParagraph_NegativeIndex_Throws()
    {
        var doc = FodtDocument.Load(MinimalPath);
        Assert.Throws<ArgumentOutOfRangeException>(() => doc.InsertParagraph(-1, "Bad"));
    }

    [Fact]
    public void InsertParagraph_IndexBeyondCount_Throws()
    {
        var doc = FodtDocument.Load(MinimalPath);
        int count = doc.ParagraphCount;
        Assert.Throws<ArgumentOutOfRangeException>(() => doc.InsertParagraph(count + 1, "Bad"));
    }

    [Fact]
    public void InsertParagraph_PersistsAfterSaveReload()
    {
        var doc = FodtDocument.Load(MinimalPath);
        doc.InsertParagraph(0, "Persistent");
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
    public void InsertParagraph_ReturnsParagraphWithCorrectText()
    {
        var doc = FodtDocument.Load(MinimalPath);
        var para = doc.InsertParagraph(0, "Check");
        Assert.NotNull(para);
        Assert.Equal("Check", para.Text);
    }

    [Fact]
    public void InsertParagraph_EmptyText_Allowed()
    {
        var doc = FodtDocument.Load(MinimalPath);
        var para = doc.InsertParagraph(0, "");
        Assert.Equal("", para.Text);
    }

    [Fact]
    public void InsertParagraph_MultipleInserts_CorrectOrder()
    {
        var doc = FodtDocument.Load(MinimalPath);
        doc.InsertParagraph(0, "First");
        doc.InsertParagraph(1, "Second");
        doc.InsertParagraph(2, "Third");
        Assert.Equal("First", doc.Paragraphs[0].Text);
        Assert.Equal("Second", doc.Paragraphs[1].Text);
        Assert.Equal("Third", doc.Paragraphs[2].Text);
    }
}
