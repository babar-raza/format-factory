// Tests for FodtDocument.GetHeadingParagraphs dedicated coverage.
// Sprint: ff-sprint-s187-dotnet-deepening-20260628
// Ledger: PC-FODT-R196

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R196: Dedicated tests for FodtDocument.GetHeadingParagraphs().
/// Returns an IReadOnlyList of FodtParagraph elements where IsHeading is true.
/// Empty document returns empty list.
/// Body paragraphs (text:p) are excluded.
/// Headings (text:h) are included.
/// Count matches number of headings in document.
/// All returned paragraphs have IsHeading = true.
/// Multiple heading levels all included.
/// Covers: empty doc returns empty; body paragraphs excluded; heading included;
/// returns IReadOnlyList; all IsHeading=true; count matches heading count;
/// multiple levels all included; mixed content selects only headings;
/// dogfood after append headings; dogfood heading count after remove.
/// </summary>
public class FodtR196GetHeadingParagraphsTests
{
    // -------------------------------------------------------------------------
    // Basic tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetHeadingParagraphs_EmptyDocument_ReturnsEmpty()
    {
        var doc = FodtDocument.CreateEmpty();
        var result = doc.GetHeadingParagraphs();
        Assert.Empty(result);
    }

    [Fact]
    public void GetHeadingParagraphs_OnlyBodyParagraphs_ReturnsEmpty()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Body 1");
        doc.AppendParagraph("Body 2");
        var result = doc.GetHeadingParagraphs();
        Assert.Empty(result);
    }

    [Fact]
    public void GetHeadingParagraphs_SingleHeading_ReturnsOne()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("Title", 1);
        var result = doc.GetHeadingParagraphs();
        Assert.Single(result);
    }

    [Fact]
    public void GetHeadingParagraphs_ReturnsIReadOnlyList()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("Title", 1);
        var result = doc.GetHeadingParagraphs();
        Assert.IsAssignableFrom<System.Collections.Generic.IReadOnlyList<FodtParagraph>>(result);
    }

    [Fact]
    public void GetHeadingParagraphs_AllReturnedAreHeadings()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("H1", 1);
        doc.AppendParagraph("Body");
        doc.AppendHeading("H2", 2);
        var result = doc.GetHeadingParagraphs();
        foreach (var p in result)
            Assert.True(p.IsHeading);
    }

    [Fact]
    public void GetHeadingParagraphs_CountMatchesHeadingCount()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("H1", 1);
        doc.AppendParagraph("Body");
        doc.AppendHeading("H2", 2);
        doc.AppendHeading("H3", 3);
        var result = doc.GetHeadingParagraphs();
        Assert.Equal(3, result.Count);
    }

    [Fact]
    public void GetHeadingParagraphs_MultipleHeadingLevels_AllIncluded()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("Level 1", 1);
        doc.AppendHeading("Level 2", 2);
        doc.AppendHeading("Level 3", 3);
        var result = doc.GetHeadingParagraphs();
        Assert.Equal(3, result.Count);
    }

    [Fact]
    public void GetHeadingParagraphs_MixedContent_OnlyHeadingsReturned()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Intro");
        doc.AppendHeading("Section", 1);
        doc.AppendParagraph("Body");
        doc.AppendHeading("Conclusion", 2);
        doc.AppendParagraph("End");
        var result = doc.GetHeadingParagraphs();
        Assert.Equal(2, result.Count);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipelines
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_AppendThreeHeadings_CountIsThree()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("Chapter 1", 1);
        doc.AppendHeading("Chapter 2", 1);
        doc.AppendHeading("Chapter 3", 1);
        var result = doc.GetHeadingParagraphs();
        Assert.Equal(3, result.Count);
        Assert.All(result, p => Assert.True(p.IsHeading));
    }

    [Fact]
    public void DogfoodPipeline_AfterRemoveParagraph_HeadingCountUpdated()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("Title", 1);
        doc.AppendHeading("Section", 2);
        doc.RemoveParagraph(0); // remove first heading
        var result = doc.GetHeadingParagraphs();
        Assert.Single(result);
    }
}
