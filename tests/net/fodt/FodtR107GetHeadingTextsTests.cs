// R107 Wave 2: FODT GetHeadingTexts tests
// Ledger: R107-FODT-GETHEADINGTEXTS

using System;
using System.IO;
using System.Linq;
using FormatFactory.Fodt;
using Xunit;

namespace FormatFactory.Fodt.Tests;

public class FodtR107GetHeadingTextsTests
{
    private static readonly string SamplesDir = Path.GetFullPath(
        Path.Combine(AppContext.BaseDirectory,
            "../../../../../../samples/by-format/fodt"));

    private static string MinimalPath =>
        Path.Combine(SamplesDir, "minimal-document.fodt");

    [Fact]
    public void GetHeadingTexts_ReturnsOnlyHeadingText()
    {
        var doc = FodtDocument.Load(MinimalPath);
        var headings = doc.GetHeadingTexts();
        // All returned texts should match heading paragraphs
        var headingParas = doc.GetHeadingParagraphs();
        Assert.Equal(headingParas.Count, headings.Count);
        for (int i = 0; i < headings.Count; i++)
            Assert.Equal(headingParas[i].Text ?? "", headings[i]);
    }

    [Fact]
    public void GetHeadingTexts_EmptyDoc_ReturnsEmptyList()
    {
        var doc = FodtDocument.Load(MinimalPath);
        doc.RemoveAllParagraphs();
        var headings = doc.GetHeadingTexts();
        Assert.Empty(headings);
    }

    [Fact]
    public void GetHeadingTexts_NoParagraphsIncluded()
    {
        var doc = FodtDocument.Load(MinimalPath);
        var headings = doc.GetHeadingTexts();
        var allTexts = doc.GetParagraphTexts();
        // Headings should be a subset of all paragraph texts
        Assert.True(headings.Count <= allTexts.Count);
    }

    [Fact]
    public void GetHeadingTexts_AfterAppendParagraph_NotIncluded()
    {
        var doc = FodtDocument.Load(MinimalPath);
        int before = doc.GetHeadingTexts().Count;
        doc.AppendParagraph("Not a heading");
        Assert.Equal(before, doc.GetHeadingTexts().Count);
    }

    [Fact]
    public void GetHeadingTexts_MatchesGetHeadingCount()
    {
        var doc = FodtDocument.Load(MinimalPath);
        Assert.Equal(doc.GetHeadingCount(), doc.GetHeadingTexts().Count);
    }

    [Fact]
    public void GetHeadingTexts_AfterRemoveAllParagraphs_Empty()
    {
        var doc = FodtDocument.Load(MinimalPath);
        doc.RemoveAllParagraphs();
        Assert.Empty(doc.GetHeadingTexts());
    }

    [Fact]
    public void GetHeadingTexts_ReturnType_IsReadOnly()
    {
        var doc = FodtDocument.Load(MinimalPath);
        var headings = doc.GetHeadingTexts();
        Assert.IsAssignableFrom<System.Collections.Generic.IReadOnlyList<string>>(headings);
    }

    [Fact]
    public void GetHeadingTexts_ContainsNonEmptyStrings()
    {
        var doc = FodtDocument.Load(MinimalPath);
        var headings = doc.GetHeadingTexts();
        if (headings.Count > 0)
        {
            // At least one heading should have non-empty text
            Assert.Contains(headings, h => h.Length > 0);
        }
    }
}
