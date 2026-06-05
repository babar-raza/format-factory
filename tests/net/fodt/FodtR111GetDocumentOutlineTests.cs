// R111 Wave 5: FODT GetDocumentOutline tests
// Ledger: R111-GOVERNED-DOTNET-FODT-GETDOCUMENTOUTLINE-001

using System;
using System.IO;
using FormatFactory.Fodt;
using Xunit;

namespace FormatFactory.Fodt.Tests;

public class FodtR111GetDocumentOutlineTests
{
    private static readonly string SamplesDir = Path.GetFullPath(
        Path.Combine(AppContext.BaseDirectory,
            "../../../../../../samples/by-format/fodt"));

    private static string MinimalPath =>
        Path.Combine(SamplesDir, "minimal-document.fodt");

    [Fact]
    public void GetDocumentOutline_WithHeadings_ReturnsList()
    {
        var doc = FodtDocument.Load(MinimalPath);
        doc.InsertHeading(0, "Chapter 1", 1);
        doc.InsertHeading(1, "Section 1.1", 2);
        doc.InsertHeading(2, "Section 1.2", 2);

        var outline = doc.GetDocumentOutline();
        Assert.True(outline.Count >= 3);
        Assert.Equal(1, outline[0].Level);
        Assert.Equal("Chapter 1", outline[0].Text);
        Assert.Equal(2, outline[1].Level);
        Assert.Equal("Section 1.1", outline[1].Text);
    }

    [Fact]
    public void GetDocumentOutline_NoHeadings_ReturnsEmpty()
    {
        var doc = FodtDocument.Load(MinimalPath);
        doc.RemoveAllParagraphs();
        doc.AppendParagraph("Just a paragraph");

        var outline = doc.GetDocumentOutline();
        Assert.Empty(outline);
    }

    [Fact]
    public void GetDocumentOutline_MixedLevels_ReportsCorrectLevels()
    {
        var doc = FodtDocument.Load(MinimalPath);
        doc.RemoveAllParagraphs();
        doc.InsertHeading(0, "H1", 1);
        doc.AppendParagraph("text");
        doc.InsertHeading(doc.ParagraphCount, "H3", 3);
        doc.InsertHeading(doc.ParagraphCount, "H6", 6);

        var outline = doc.GetDocumentOutline();
        Assert.Equal(3, outline.Count);
        Assert.Equal(1, outline[0].Level);
        Assert.Equal(3, outline[1].Level);
        Assert.Equal(6, outline[2].Level);
    }

    [Fact]
    public void GetDocumentOutline_PreservesTextContent()
    {
        var doc = FodtDocument.Load(MinimalPath);
        doc.InsertHeading(0, "Special chars: <>&\"'", 1);

        var outline = doc.GetDocumentOutline();
        Assert.Contains(outline, o => o.Text.Contains("Special chars"));
    }

    [Fact]
    public void GetDocumentOutline_EmptyHeadingText()
    {
        var doc = FodtDocument.Load(MinimalPath);
        doc.InsertHeading(0, "", 2);

        var outline = doc.GetDocumentOutline();
        Assert.Contains(outline, o => o.Level == 2 && o.Text == string.Empty);
    }

    [Fact]
    public void GetDocumentOutline_AfterRemoveHeading_UpdatesList()
    {
        var doc = FodtDocument.Load(MinimalPath);
        doc.RemoveAllParagraphs();
        doc.InsertHeading(0, "Keep", 1);
        doc.InsertHeading(1, "Remove", 2);

        doc.RemoveHeading(1);
        var outline = doc.GetDocumentOutline();
        Assert.Single(outline);
        Assert.Equal("Keep", outline[0].Text);
    }

    [Fact]
    public void GetDocumentOutline_SurvivesSaveRoundtrip()
    {
        var doc = FodtDocument.Load(MinimalPath);
        doc.InsertHeading(0, "RoundtripH1", 1);
        doc.InsertHeading(1, "RoundtripH2", 2);

        var tmp = Path.GetTempFileName() + ".fodt";
        try
        {
            doc.Save(tmp);
            var reloaded = FodtDocument.Load(tmp);
            var outline = reloaded.GetDocumentOutline();
            Assert.True(outline.Count >= 2);
            Assert.Equal("RoundtripH1", outline[0].Text);
        }
        finally
        {
            if (File.Exists(tmp)) File.Delete(tmp);
        }
    }

    [Fact]
    public void GetDocumentOutline_LargeDocument_HandlesMany()
    {
        var doc = FodtDocument.Load(MinimalPath);
        doc.RemoveAllParagraphs();
        for (int i = 0; i < 20; i++)
        {
            doc.InsertHeading(i, $"Heading {i}", (i % 6) + 1);
        }
        var outline = doc.GetDocumentOutline();
        Assert.Equal(20, outline.Count);
    }
}
