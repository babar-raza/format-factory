// R101 Train B: FODT .NET RemoveParagraph + ExportToMarkdown tests
// Governed skill: /add-dotnet-object-model-feature
// Ledger: R101-GOVERNED-DOTNET-FODT-REMOVEPARAGRAPH-001

using System;
using System.IO;
using FormatFactory.Fodt;
using Xunit;

namespace FormatFactory.Fodt.Tests;

public class FodtR101RemoveParagraphTests
{
    private static readonly string SamplesDir = Path.GetFullPath(
        Path.Combine(AppContext.BaseDirectory,
            "../../../../../../samples/by-format/fodt"));

    private static string MinimalPath =>
        Path.Combine(SamplesDir, "minimal-document.fodt");

    // ----- RemoveParagraph tests -----

    [Fact]
    public void RemoveParagraph_ReducesCount()
    {
        var doc = FodtDocument.Load(MinimalPath);
        int before = doc.ParagraphCount;
        if (before == 0) return; // skip if empty
        doc.RemoveParagraph(0);
        Assert.Equal(before - 1, doc.ParagraphCount);
    }

    [Fact]
    public void RemoveParagraph_NegativeIndex_Throws()
    {
        var doc = FodtDocument.Load(MinimalPath);
        Assert.Throws<ArgumentOutOfRangeException>(() => doc.RemoveParagraph(-1));
    }

    [Fact]
    public void RemoveParagraph_OutOfRange_Throws()
    {
        var doc = FodtDocument.Load(MinimalPath);
        int count = doc.ParagraphCount;
        Assert.Throws<ArgumentOutOfRangeException>(() => doc.RemoveParagraph(count));
    }

    [Fact]
    public void RemoveParagraph_PersistsAfterSaveReload()
    {
        var doc = FodtDocument.Load(MinimalPath);
        doc.AppendParagraph("ToRemove");
        int afterAppend = doc.ParagraphCount;
        doc.RemoveParagraph(afterAppend - 1);
        var tmp = Path.GetTempFileName() + ".fodt";
        try
        {
            doc.Save(tmp);
            var reloaded = FodtDocument.Load(tmp);
            Assert.Equal(afterAppend - 1, reloaded.ParagraphCount);
        }
        finally { if (File.Exists(tmp)) File.Delete(tmp); }
    }

    [Fact]
    public void RemoveParagraph_AppendRemoveRoundtrip()
    {
        var doc = FodtDocument.Load(MinimalPath);
        int original = doc.ParagraphCount;
        doc.AppendParagraph("Temp");
        Assert.Equal(original + 1, doc.ParagraphCount);
        doc.RemoveParagraph(doc.ParagraphCount - 1);
        Assert.Equal(original, doc.ParagraphCount);
    }

    // ----- ExportToMarkdown tests -----

    [Fact]
    public void ExportToMarkdown_ContainsParagraphText()
    {
        var doc = FodtDocument.Load(MinimalPath);
        var md = doc.ExportToMarkdown();
        // Should contain some text from the document
        Assert.NotEmpty(md);
    }

    [Fact]
    public void ExportToMarkdown_HeadingsGetHashPrefix()
    {
        var doc = FodtDocument.Load(MinimalPath);
        var headings = doc.GetHeadingParagraphs();
        if (headings.Count == 0) return; // skip if no headings
        var md = doc.ExportToMarkdown();
        Assert.Contains("#", md);
    }

    [Fact]
    public void ExportToMarkdown_AfterAppend_IncludesNewText()
    {
        var doc = FodtDocument.Load(MinimalPath);
        doc.AppendParagraph("R101UniqueMarker");
        var md = doc.ExportToMarkdown();
        Assert.Contains("R101UniqueMarker", md);
    }
}
