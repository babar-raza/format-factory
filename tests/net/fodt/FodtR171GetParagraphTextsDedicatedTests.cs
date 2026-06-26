// Tests for FodtDocument.GetParagraphTexts dedicated coverage.
// Sprint: ff-sprint-s162-dotnet-deepening-20260628
// Ledger: PC-FODT-R171

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R171: Dedicated tests for FodtDocument.GetParagraphTexts().
/// GetParagraphTexts returns the text of all paragraphs (both body and headings) in document order.
/// Returns empty list for empty document.
/// Covers: empty document returns empty; single paragraph returns one text;
/// text matches AppendParagraph text; multiple paragraphs returned in order;
/// heading text included in results; mixed heading and paragraph both returned;
/// count matches ParagraphCount; returns IReadOnlyList;
/// dogfood AppendParagraph->GetParagraphTexts pipeline;
/// dogfood multiple appends preserved in insertion order.
/// </summary>
public class FodtR171GetParagraphTextsDedicatedTests
{
    // -------------------------------------------------------------------------
    // Zero / empty tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetParagraphTexts_EmptyDocument_ReturnsEmpty()
    {
        var doc = FodtDocument.CreateEmpty();
        Assert.Empty(doc.GetParagraphTexts());
    }

    [Fact]
    public void GetParagraphTexts_SingleParagraph_ReturnsOneItem()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Hello");
        Assert.Single(doc.GetParagraphTexts());
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetParagraphTexts_TextMatchesAppendParagraphText()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Unique text");
        Assert.Equal("Unique text", doc.GetParagraphTexts()[0]);
    }

    [Fact]
    public void GetParagraphTexts_MultipleParagraphs_ReturnedInOrder()
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
    public void GetParagraphTexts_HeadingTextIncluded()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("Chapter 1", 1);
        var texts = doc.GetParagraphTexts();
        Assert.Contains("Chapter 1", texts);
    }

    [Fact]
    public void GetParagraphTexts_MixedContent_BothIncluded()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("Title", 1);
        doc.AppendParagraph("Body");
        var texts = doc.GetParagraphTexts();
        Assert.Equal(2, texts.Count);
        Assert.Equal("Title", texts[0]);
        Assert.Equal("Body", texts[1]);
    }

    [Fact]
    public void GetParagraphTexts_Count_MatchesParagraphCount()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("A");
        doc.AppendParagraph("B");
        doc.AppendHeading("C", 2);
        Assert.Equal(doc.ParagraphCount, doc.GetParagraphTexts().Count);
    }

    [Fact]
    public void GetParagraphTexts_ReturnsIReadOnlyList()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("X");
        Assert.IsAssignableFrom<System.Collections.Generic.IReadOnlyList<string>>(doc.GetParagraphTexts());
    }

    // -------------------------------------------------------------------------
    // Dogfood pipelines
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_AppendParagraph_GetParagraphTexts()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Intro");
        doc.AppendParagraph("Body");
        doc.AppendParagraph("Conclusion");
        var texts = doc.GetParagraphTexts();
        Assert.Contains("Intro", texts);
        Assert.Contains("Body", texts);
        Assert.Contains("Conclusion", texts);
    }

    [Fact]
    public void DogfoodPipeline_MultipleAppends_PreservedInInsertionOrder()
    {
        var doc = FodtDocument.CreateEmpty();
        for (int i = 0; i < 5; i++)
            doc.AppendParagraph($"Para {i}");
        var texts = doc.GetParagraphTexts();
        Assert.Equal(5, texts.Count);
        for (int i = 0; i < 5; i++)
            Assert.Equal($"Para {i}", texts[i]);
    }
}
