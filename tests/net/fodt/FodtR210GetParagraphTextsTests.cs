// Tests for FodtDocument.GetParagraphTexts dedicated coverage.
// Sprint: ff-sprint-s196-dotnet-deepening-20260629
// Ledger: PC-FODT-R210

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R210: Dedicated tests for FodtDocument.GetParagraphTexts().
/// Returns an IReadOnlyList of all paragraph texts (both body paragraphs and headings).
/// Empty document returns empty list.
/// Single paragraph returns list with one element.
/// Multiple paragraphs returned in document order.
/// Headings are included in the result.
/// Returns IReadOnlyList&lt;string&gt; type.
/// Count matches ParagraphCount.
/// No nulls in result (null text becomes empty string).
/// Covers: empty doc empty list; single para; multiple paras in order;
/// heading included; IReadOnlyList type; count matches; no nulls;
/// mixed content order correct; dogfood three paras all present; dogfood append updates result.
/// </summary>
public class FodtR210GetParagraphTextsTests
{
    // -------------------------------------------------------------------------
    // Basic tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetParagraphTexts_EmptyDocument_ReturnsEmpty()
    {
        var doc = FodtDocument.CreateEmpty();
        Assert.Empty(doc.GetParagraphTexts());
    }

    [Fact]
    public void GetParagraphTexts_SingleParagraph_ReturnsOneElement()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Hello");
        var result = doc.GetParagraphTexts();
        Assert.Single(result);
        Assert.Equal("Hello", result[0]);
    }

    [Fact]
    public void GetParagraphTexts_MultipleParagraphs_InDocumentOrder()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("First");
        doc.AppendParagraph("Second");
        doc.AppendParagraph("Third");
        var result = doc.GetParagraphTexts();
        Assert.Equal(3, result.Count);
        Assert.Equal("First", result[0]);
        Assert.Equal("Second", result[1]);
        Assert.Equal("Third", result[2]);
    }

    [Fact]
    public void GetParagraphTexts_HeadingIncluded()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("MyTitle", 1);
        var result = doc.GetParagraphTexts();
        Assert.Single(result);
        Assert.Equal("MyTitle", result[0]);
    }

    [Fact]
    public void GetParagraphTexts_ReturnsIReadOnlyList()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Text");
        Assert.IsAssignableFrom<System.Collections.Generic.IReadOnlyList<string>>(doc.GetParagraphTexts());
    }

    [Fact]
    public void GetParagraphTexts_CountMatchesParagraphCount()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("A");
        doc.AppendHeading("B", 1);
        doc.AppendParagraph("C");
        Assert.Equal(doc.ParagraphCount, doc.GetParagraphTexts().Count);
    }

    [Fact]
    public void GetParagraphTexts_NoNullsInResult()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Hello");
        doc.AppendParagraph("World");
        foreach (var t in doc.GetParagraphTexts())
            Assert.NotNull(t);
    }

    [Fact]
    public void GetParagraphTexts_MixedContent_OrderCorrect()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Intro");
        doc.AppendHeading("Section", 1);
        doc.AppendParagraph("Body");
        var result = doc.GetParagraphTexts();
        Assert.Equal("Intro", result[0]);
        Assert.Equal("Section", result[1]);
        Assert.Equal("Body", result[2]);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipelines
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_ThreeParagraphs_AllPresent()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Alpha");
        doc.AppendParagraph("Beta");
        doc.AppendParagraph("Gamma");
        var result = doc.GetParagraphTexts();
        Assert.Contains("Alpha", result);
        Assert.Contains("Beta", result);
        Assert.Contains("Gamma", result);
    }

    [Fact]
    public void DogfoodPipeline_AppendUpdatesResult()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("First");
        var before = doc.GetParagraphTexts().Count;
        doc.AppendParagraph("Second");
        var after = doc.GetParagraphTexts().Count;
        Assert.Equal(before + 1, after);
        Assert.Contains("Second", doc.GetParagraphTexts());
    }
}
