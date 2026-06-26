// Tests for FodtDocument.GetParagraphTexts dedicated coverage.
// Sprint: ff-sprint-s181-dotnet-deepening-20260628
// Ledger: PC-FODT-R190

using System.Collections.Generic;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R190: Dedicated tests for FodtDocument.GetParagraphTexts().
/// Returns IReadOnlyList&lt;string&gt; of all paragraph texts in document order.
/// Headings (text:h) are included alongside body paragraphs (text:p).
/// Empty paragraphs contribute empty string (not null).
/// Covers: empty doc returns empty; single paragraph; multiple in order;
/// headings included; returns IReadOnlyList; count matches ParagraphCount;
/// no nulls in result; empty paragraph is empty string; dogfood mixed content;
/// dogfood after RemoveAllParagraphs.
/// </summary>
public class FodtR190GetParagraphTextsTests
{
    // -------------------------------------------------------------------------
    // Basic tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetParagraphTexts_EmptyDocument_ReturnsEmpty()
    {
        var doc = FodtDocument.CreateEmpty();
        var texts = doc.GetParagraphTexts();
        Assert.Empty(texts);
    }

    [Fact]
    public void GetParagraphTexts_SingleParagraph_ReturnsOneElement()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Hello");
        var texts = doc.GetParagraphTexts();
        Assert.Single(texts);
        Assert.Equal("Hello", texts[0]);
    }

    [Fact]
    public void GetParagraphTexts_MultipleParagraphs_InDocumentOrder()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("First");
        doc.AppendParagraph("Second");
        doc.AppendParagraph("Third");
        var texts = doc.GetParagraphTexts();
        Assert.Equal(3, texts.Count);
        Assert.Equal("First", texts[0]);
        Assert.Equal("Second", texts[1]);
        Assert.Equal("Third", texts[2]);
    }

    [Fact]
    public void GetParagraphTexts_HeadingsIncluded()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("Chapter 1", 1);
        var texts = doc.GetParagraphTexts();
        Assert.Single(texts);
        Assert.Equal("Chapter 1", texts[0]);
    }

    [Fact]
    public void GetParagraphTexts_ReturnsIReadOnlyList()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Test");
        var texts = doc.GetParagraphTexts();
        Assert.IsAssignableFrom<IReadOnlyList<string>>(texts);
    }

    [Fact]
    public void GetParagraphTexts_Count_MatchesParagraphCount()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("A");
        doc.AppendHeading("B", 1);
        doc.AppendParagraph("C");
        var texts = doc.GetParagraphTexts();
        Assert.Equal(doc.ParagraphCount, texts.Count);
    }

    [Fact]
    public void GetParagraphTexts_NoNullsInResult()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Text");
        doc.AppendHeading("Heading", 2);
        var texts = doc.GetParagraphTexts();
        foreach (var t in texts)
            Assert.NotNull(t);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipelines
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_MixedContent_AllTextsPresent()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("Title", 1);
        doc.AppendParagraph("Body paragraph");
        doc.AppendHeading("Section", 2);
        var texts = doc.GetParagraphTexts();
        Assert.Equal(3, texts.Count);
        Assert.Contains("Title", texts);
        Assert.Contains("Body paragraph", texts);
        Assert.Contains("Section", texts);
    }

    [Fact]
    public void DogfoodPipeline_AfterRemoveAllParagraphs_ReturnsEmpty()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("First");
        doc.AppendParagraph("Second");
        doc.RemoveAllParagraphs();
        var texts = doc.GetParagraphTexts();
        Assert.Empty(texts);
    }
}
