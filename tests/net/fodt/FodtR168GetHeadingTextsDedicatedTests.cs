// Tests for FodtDocument.GetHeadingTexts dedicated coverage.
// Sprint: ff-sprint-s159-dotnet-deepening-20260628
// Ledger: PC-FODT-R168

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R168: Dedicated tests for FodtDocument.GetHeadingTexts().
/// GetHeadingTexts returns the text content of all heading paragraphs in document order.
/// Returns empty list for empty document or document with no headings.
/// Covers: empty document returns empty; paragraphs-only returns empty;
/// single heading returns one text; heading text matches AppendHeading text;
/// multiple headings returned in order; paragraphs excluded from result;
/// heading and paragraph mixed — only heading returned; result is IReadOnlyList;
/// dogfood AppendHeading->GetHeadingTexts pipeline;
/// dogfood multi-level headings all included in order.
/// </summary>
public class FodtR168GetHeadingTextsDedicatedTests
{
    // -------------------------------------------------------------------------
    // Zero / empty tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetHeadingTexts_EmptyDocument_ReturnsEmpty()
    {
        var doc = FodtDocument.CreateEmpty();
        Assert.Empty(doc.GetHeadingTexts());
    }

    [Fact]
    public void GetHeadingTexts_ParagraphsOnly_ReturnsEmpty()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Not a heading");
        doc.AppendParagraph("Also not a heading");
        Assert.Empty(doc.GetHeadingTexts());
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetHeadingTexts_SingleHeading_ReturnsOneText()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("Introduction", 1);
        var texts = doc.GetHeadingTexts();
        Assert.Single(texts);
    }

    [Fact]
    public void GetHeadingTexts_HeadingText_MatchesAppendHeadingText()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("Chapter One", 1);
        var texts = doc.GetHeadingTexts();
        Assert.Equal("Chapter One", texts[0]);
    }

    [Fact]
    public void GetHeadingTexts_MultipleHeadings_ReturnedInOrder()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("First", 1);
        doc.AppendHeading("Second", 1);
        doc.AppendHeading("Third", 2);
        var texts = doc.GetHeadingTexts();
        Assert.Equal(3, texts.Count);
        Assert.Equal("First", texts[0]);
        Assert.Equal("Third", texts[2]);
    }

    [Fact]
    public void GetHeadingTexts_ParagraphsExcluded()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("Heading", 1);
        doc.AppendParagraph("Body text excluded");
        var texts = doc.GetHeadingTexts();
        Assert.Single(texts);
        Assert.DoesNotContain("Body text excluded", texts);
    }

    [Fact]
    public void GetHeadingTexts_MixedContent_OnlyHeadingsReturned()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Intro para");
        doc.AppendHeading("Section 1", 1);
        doc.AppendParagraph("Section content");
        doc.AppendHeading("Section 2", 1);
        var texts = doc.GetHeadingTexts();
        Assert.Equal(2, texts.Count);
        Assert.Equal("Section 1", texts[0]);
        Assert.Equal("Section 2", texts[1]);
    }

    [Fact]
    public void GetHeadingTexts_ReturnsIReadOnlyList()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("H", 1);
        Assert.IsAssignableFrom<System.Collections.Generic.IReadOnlyList<string>>(doc.GetHeadingTexts());
    }

    // -------------------------------------------------------------------------
    // Dogfood pipelines
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_AppendHeading_GetHeadingTexts()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("Chapter 1", 1);
        doc.AppendHeading("Chapter 2", 1);
        var texts = doc.GetHeadingTexts();
        Assert.Equal(2, texts.Count);
        Assert.Contains("Chapter 1", texts);
        Assert.Contains("Chapter 2", texts);
    }

    [Fact]
    public void DogfoodPipeline_MultiLevelHeadings_AllIncludedInOrder()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("Title", 1);
        doc.AppendHeading("Subtitle", 2);
        doc.AppendHeading("Sub-subtitle", 3);
        var texts = doc.GetHeadingTexts();
        Assert.Equal(3, texts.Count);
        Assert.Equal("Title", texts[0]);
        Assert.Equal("Subtitle", texts[1]);
        Assert.Equal("Sub-subtitle", texts[2]);
    }
}
