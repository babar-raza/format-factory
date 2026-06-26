// Tests for FodtDocument.GetHeadingParagraphs dedicated coverage.
// Sprint: ff-sprint-s163-dotnet-deepening-20260628
// Ledger: PC-FODT-R172

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R172: Dedicated tests for FodtDocument.GetHeadingParagraphs().
/// GetHeadingParagraphs returns all heading elements (text:h) in document order.
/// Returns empty list for empty document or document with no headings.
/// Each returned FodtParagraph has IsHeading == true.
/// Covers: empty document returns empty; paragraphs-only returns empty;
/// single heading returns one; each result has IsHeading=true; multiple headings in order;
/// paragraphs excluded from result; count matches GetHeadingTexts count;
/// returns IReadOnlyList; dogfood AppendHeading->GetHeadingParagraphs;
/// dogfood multi-level all returned.
/// </summary>
public class FodtR172GetHeadingParagraphsDedicatedTests
{
    // -------------------------------------------------------------------------
    // Zero / empty tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetHeadingParagraphs_EmptyDocument_ReturnsEmpty()
    {
        var doc = FodtDocument.CreateEmpty();
        Assert.Empty(doc.GetHeadingParagraphs());
    }

    [Fact]
    public void GetHeadingParagraphs_ParagraphsOnly_ReturnsEmpty()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Body");
        doc.AppendParagraph("More body");
        Assert.Empty(doc.GetHeadingParagraphs());
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetHeadingParagraphs_SingleHeading_ReturnsOne()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("Title", 1);
        Assert.Single(doc.GetHeadingParagraphs());
    }

    [Fact]
    public void GetHeadingParagraphs_EachResult_IsHeadingTrue()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("H1", 1);
        doc.AppendHeading("H2", 2);
        foreach (var h in doc.GetHeadingParagraphs())
            Assert.True(h.IsHeading);
    }

    [Fact]
    public void GetHeadingParagraphs_MultipleHeadings_ReturnedInOrder()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("First", 1);
        doc.AppendHeading("Second", 2);
        doc.AppendHeading("Third", 3);
        var headings = doc.GetHeadingParagraphs();
        Assert.Equal(3, headings.Count);
        Assert.Equal("First", headings[0].Text);
        Assert.Equal("Third", headings[2].Text);
    }

    [Fact]
    public void GetHeadingParagraphs_ParagraphsExcluded()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Intro");
        doc.AppendHeading("Section", 1);
        doc.AppendParagraph("Body");
        var headings = doc.GetHeadingParagraphs();
        Assert.Single(headings);
        Assert.Equal("Section", headings[0].Text);
    }

    [Fact]
    public void GetHeadingParagraphs_Count_MatchesGetHeadingTextsCount()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("A", 1);
        doc.AppendParagraph("Para");
        doc.AppendHeading("B", 2);
        Assert.Equal(doc.GetHeadingTexts().Count, doc.GetHeadingParagraphs().Count);
    }

    [Fact]
    public void GetHeadingParagraphs_ReturnsIReadOnlyList()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("H", 1);
        Assert.IsAssignableFrom<System.Collections.Generic.IReadOnlyList<FodtParagraph>>(doc.GetHeadingParagraphs());
    }

    // -------------------------------------------------------------------------
    // Dogfood pipelines
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_AppendHeading_GetHeadingParagraphs()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("Chapter 1", 1);
        doc.AppendHeading("Chapter 2", 1);
        var headings = doc.GetHeadingParagraphs();
        Assert.Equal(2, headings.Count);
        Assert.All(headings, h => Assert.True(h.IsHeading));
    }

    [Fact]
    public void DogfoodPipeline_MultiLevelHeadings_AllReturned()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("Title", 1);
        doc.AppendHeading("Subtitle", 2);
        doc.AppendHeading("Sub-subtitle", 3);
        var headings = doc.GetHeadingParagraphs();
        Assert.Equal(3, headings.Count);
        Assert.Equal("Title", headings[0].Text);
        Assert.Equal("Subtitle", headings[1].Text);
        Assert.Equal("Sub-subtitle", headings[2].Text);
    }
}
