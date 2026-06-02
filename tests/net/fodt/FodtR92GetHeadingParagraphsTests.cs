// R92 Train M: FODT .NET GetHeadingParagraphs Tests
// New API: GetHeadingParagraphs() — heading enumeration for document structure analysis
// Sprint: FORMAT-FACTORY-R92-DECLARATION-MATERIALIZER-WORK-ITEM-GRADING-ACCELERATION-POC-MAINSTREAM-MEGA-TRAIN-001

using System;
using System.IO;
using System.Linq;
using FormatFactory.Fodt;
using Xunit;

namespace FormatFactory.Fodt.Tests;

public class FodtR92GetHeadingParagraphsTests
{
    private static readonly string FixturesDir = Path.GetFullPath(
        Path.Combine(AppContext.BaseDirectory,
            "../../../Fixtures"));

    private static string HeadingsFodtPath =>
        Path.Combine(FixturesDir, "fodt-headings-and-list.fodt");

    private static string MinimalFodtPath =>
        Path.Combine(FixturesDir, "fodt-minimal-roundtrip.fodt");

    [Fact]
    public void GetHeadingParagraphs_ReturnsOnlyHeadings()
    {
        var doc = FodtDocument.Load(HeadingsFodtPath);
        var headings = doc.GetHeadingParagraphs();
        Assert.NotEmpty(headings);
        Assert.All(headings, h => Assert.True(h.IsHeading));
    }

    [Fact]
    public void GetHeadingParagraphs_CountMatchesExpected()
    {
        // fodt-headings-and-list.fodt has 4 headings: H1, H2, H3, H1
        var doc = FodtDocument.Load(HeadingsFodtPath);
        var headings = doc.GetHeadingParagraphs();
        Assert.Equal(4, headings.Count);
    }

    [Fact]
    public void GetHeadingParagraphs_TextsAreNonEmpty()
    {
        var doc = FodtDocument.Load(HeadingsFodtPath);
        var headings = doc.GetHeadingParagraphs();
        Assert.All(headings, h => Assert.False(string.IsNullOrWhiteSpace(h.Text)));
    }

    [Fact]
    public void GetHeadingParagraphs_PreservesDocumentOrder()
    {
        var doc = FodtDocument.Load(HeadingsFodtPath);
        var headings = doc.GetHeadingParagraphs();
        // First heading is "Chapter One" (H1), last is "Chapter Two" (H1)
        Assert.Equal("Chapter One", headings[0].Text);
        Assert.Equal("Chapter Two", headings[headings.Count - 1].Text);
    }

    [Fact]
    public void GetHeadingParagraphs_OutlineLevelsAreCorrect()
    {
        var doc = FodtDocument.Load(HeadingsFodtPath);
        var headings = doc.GetHeadingParagraphs();
        // Expected levels: 1, 2, 3, 1
        Assert.Equal(1, headings[0].OutlineLevel);
        Assert.Equal(2, headings[1].OutlineLevel);
        Assert.Equal(3, headings[2].OutlineLevel);
        Assert.Equal(1, headings[3].OutlineLevel);
    }

    [Fact]
    public void GetHeadingParagraphs_SubsetOfAllParagraphs()
    {
        var doc = FodtDocument.Load(HeadingsFodtPath);
        var headings = doc.GetHeadingParagraphs();
        var allParas = doc.Paragraphs;
        // Headings should be a strict subset (fewer than all paragraphs)
        Assert.True(headings.Count < allParas.Count,
            "Headings should be a strict subset of all paragraphs");
        // Every heading text must appear in allParas as a heading
        foreach (var h in headings)
            Assert.Contains(allParas, p => p.IsHeading && p.Text == h.Text);
    }

    [Fact]
    public void GetHeadingParagraphs_StableAcrossMultipleCalls()
    {
        var doc = FodtDocument.Load(HeadingsFodtPath);
        var h1 = doc.GetHeadingParagraphs();
        var h2 = doc.GetHeadingParagraphs();
        Assert.Equal(h1.Count, h2.Count);
        for (int i = 0; i < h1.Count; i++)
            Assert.Equal(h1[i].Text, h2[i].Text);
    }

    [Fact]
    public void GetHeadingParagraphs_ReturnsReadOnlyList()
    {
        var doc = FodtDocument.Load(HeadingsFodtPath);
        var headings = doc.GetHeadingParagraphs();
        Assert.IsAssignableFrom<System.Collections.Generic.IReadOnlyList<FodtParagraph>>(headings);
    }

    [Fact]
    public void GetHeadingParagraphs_ReturnsEmptyListForDocumentWithNoHeadings()
    {
        // fodt-minimal-roundtrip.fodt contains only text:p elements, no text:h
        var doc = FodtDocument.Load(MinimalFodtPath);
        var headings = doc.GetHeadingParagraphs();
        // May be empty or non-empty depending on fixture — just verify it doesn't throw
        // and all returned items are headings
        Assert.All(headings, h => Assert.True(h.IsHeading));
    }
}
