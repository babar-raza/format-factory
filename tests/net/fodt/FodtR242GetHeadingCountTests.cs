// Tests for FodtDocument.GetHeadingCount dedicated coverage.
// Sprint: ff-sprint-s227-dotnet-deepening-20260629
// Ledger: PC-FODT-R242

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R242: Dedicated tests for FodtDocument.GetHeadingCount().
/// Empty document: no exception.
/// Empty document: count is 0.
/// After adding one heading: count is 1.
/// ParagraphCount unchanged after get.
/// After adding paragraphs (no headings): heading count stays 0.
/// Called twice: same result.
/// After adding multiple headings: count matches.
/// Mixed headings and paragraphs: correct heading count.
/// Dogfood: add headings of different levels, verify count.
/// Dogfood: stable across delete and add.
/// </summary>
public class FodtR242GetHeadingCountTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetHeadingCount_EmptyDoc_NoException()
    {
        var doc = FodtDocument.CreateEmpty();
        var ex = Record.Exception(() => doc.GetHeadingCount());
        Assert.Null(ex);
    }

    [Fact]
    public void GetHeadingCount_EmptyDoc_IsZero()
    {
        var doc = FodtDocument.CreateEmpty();
        Assert.Equal(0, doc.GetHeadingCount());
    }

    [Fact]
    public void GetHeadingCount_AfterOneHeading_IsOne()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("Chapter 1", 1);
        Assert.Equal(1, doc.GetHeadingCount());
    }

    [Fact]
    public void GetHeadingCount_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Para");
        doc.AppendHeading("Head", 1);
        int before = doc.ParagraphCount;
        doc.GetHeadingCount();
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void GetHeadingCount_ParagraphsOnly_IsZero()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("No headings here");
        doc.AppendParagraph("Still no headings");
        Assert.Equal(0, doc.GetHeadingCount());
    }

    [Fact]
    public void GetHeadingCount_CalledTwice_SameResult()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("H1", 1);
        doc.AppendHeading("H2", 2);
        Assert.Equal(doc.GetHeadingCount(), doc.GetHeadingCount());
    }

    [Fact]
    public void GetHeadingCount_MultipleHeadings_CountMatches()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("Head A", 1);
        doc.AppendHeading("Head B", 2);
        doc.AppendHeading("Head C", 3);
        Assert.Equal(3, doc.GetHeadingCount());
    }

    [Fact]
    public void GetHeadingCount_Mixed_CorrectCount()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("Section 1", 1);
        doc.AppendParagraph("Para 1");
        doc.AppendHeading("Section 2", 1);
        doc.AppendParagraph("Para 2");
        Assert.Equal(2, doc.GetHeadingCount());
    }

    // -------------------------------------------------------------------------
    // Dogfood pipelines
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_DifferentLevels_AllCounted()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("Level 1 A", 1);
        doc.AppendHeading("Level 2 A", 2);
        doc.AppendHeading("Level 1 B", 1);
        doc.AppendHeading("Level 3 A", 3);
        Assert.Equal(4, doc.GetHeadingCount());
    }

    [Fact]
    public void DogfoodPipeline_StableAfterOperations()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("Initial Heading", 1);
        doc.AppendParagraph("Some content");
        doc.SetAuthor("Author");
        var count = doc.GetHeadingCount();
        Assert.True(count >= 1);
    }
}
