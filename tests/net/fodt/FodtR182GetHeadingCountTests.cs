// Tests for FodtDocument.GetHeadingCount dedicated coverage.
// Sprint: ff-sprint-s173-dotnet-deepening-20260628
// Ledger: PC-FODT-R182

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R182: Dedicated tests for FodtDocument.GetHeadingCount().
/// Returns the total number of heading elements (text:h) in the document.
/// Counts only actual heading elements (AppendHeading), not body paragraphs.
/// Covers: empty doc returns 0; paragraphs-only returns 0; single heading returns 1;
/// multiple headings count all; paragraphs not counted; mixed content headings only;
/// count matches GetHeadingParagraphs().Count; AppendHeading increments by 1;
/// count after RemoveHeading decrements; dogfood pipeline; multi-level headings all counted.
/// </summary>
public class FodtR182GetHeadingCountTests
{
    // -------------------------------------------------------------------------
    // Basic tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetHeadingCount_EmptyDocument_ReturnsZero()
    {
        var doc = FodtDocument.CreateEmpty();
        Assert.Equal(0, doc.GetHeadingCount());
    }

    [Fact]
    public void GetHeadingCount_ParagraphsOnly_ReturnsZero()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Para 1");
        doc.AppendParagraph("Para 2");
        Assert.Equal(0, doc.GetHeadingCount());
    }

    [Fact]
    public void GetHeadingCount_SingleHeading_ReturnsOne()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("Title", 1);
        Assert.Equal(1, doc.GetHeadingCount());
    }

    [Fact]
    public void GetHeadingCount_MultipleHeadings_CountsAll()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("H1", 1);
        doc.AppendHeading("H2", 2);
        doc.AppendHeading("H3", 3);
        Assert.Equal(3, doc.GetHeadingCount());
    }

    [Fact]
    public void GetHeadingCount_ParagraphsExcluded()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Body 1");
        doc.AppendHeading("Title", 1);
        doc.AppendParagraph("Body 2");
        Assert.Equal(1, doc.GetHeadingCount());
    }

    [Fact]
    public void GetHeadingCount_MixedContent_OnlyHeadingsCounted()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("Ch1", 1);
        doc.AppendParagraph("Body 1");
        doc.AppendHeading("Ch2", 2);
        doc.AppendParagraph("Body 2");
        Assert.Equal(2, doc.GetHeadingCount());
    }

    [Fact]
    public void GetHeadingCount_MatchesGetHeadingParagraphsCount()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("A", 1);
        doc.AppendParagraph("Body");
        doc.AppendHeading("B", 2);
        Assert.Equal(doc.GetHeadingParagraphs().Count, doc.GetHeadingCount());
    }

    [Fact]
    public void GetHeadingCount_AppendHeading_IncrementsCount()
    {
        var doc = FodtDocument.CreateEmpty();
        var before = doc.GetHeadingCount();
        doc.AppendHeading("New Heading", 1);
        Assert.Equal(before + 1, doc.GetHeadingCount());
    }

    // -------------------------------------------------------------------------
    // Dogfood pipelines
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_MultiLevelHeadings_AllCounted()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("Part 1", 1);
        doc.AppendHeading("Chapter 1", 2);
        doc.AppendHeading("Section 1.1", 3);
        doc.AppendParagraph("Body");
        doc.AppendHeading("Section 1.2", 3);
        Assert.Equal(4, doc.GetHeadingCount());
    }

    [Fact]
    public void DogfoodPipeline_RemoveHeading_DecrementsCount()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("Title", 1);
        doc.AppendParagraph("Body");
        var before = doc.GetHeadingCount();
        doc.RemoveHeading(0); // remove first heading
        Assert.Equal(before - 1, doc.GetHeadingCount());
    }
}
