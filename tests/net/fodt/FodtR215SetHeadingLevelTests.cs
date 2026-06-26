// Tests for FodtDocument.SetHeadingLevel dedicated coverage.
// Sprint: ff-sprint-s200-dotnet-deepening-20260629
// Ledger: PC-FODT-R215

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R215: Dedicated tests for FodtDocument.SetHeadingLevel(int index, int level).
/// OOB index → ArgumentOutOfRangeException.
/// level &lt; 1 → ArgumentOutOfRangeException.
/// level &gt; 6 → ArgumentOutOfRangeException.
/// Valid: heading level set without exception.
/// Valid: ParagraphCount unchanged after set.
/// Valid: paragraph text unchanged after set level.
/// Valid: GetHeadingLevel returns new level.
/// Can change level on existing heading.
/// Dogfood: set multiple levels; verify each.
/// Dogfood: heading re-leveled twice, final level correct.
/// </summary>
public class FodtR215SetHeadingLevelTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void SetHeadingLevel_NegativeIndex_ThrowsArgumentOutOfRangeException()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("Title", 1);
        Assert.Throws<ArgumentOutOfRangeException>(() => doc.SetHeadingLevel(-1, 2));
    }

    [Fact]
    public void SetHeadingLevel_IndexAboveCount_ThrowsArgumentOutOfRangeException()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("Title", 1);
        Assert.Throws<ArgumentOutOfRangeException>(() => doc.SetHeadingLevel(5, 2));
    }

    [Fact]
    public void SetHeadingLevel_LevelZero_ThrowsArgumentOutOfRangeException()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("Title", 1);
        Assert.Throws<ArgumentOutOfRangeException>(() => doc.SetHeadingLevel(0, 0));
    }

    [Fact]
    public void SetHeadingLevel_LevelAboveSix_ThrowsArgumentOutOfRangeException()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("Title", 1);
        Assert.Throws<ArgumentOutOfRangeException>(() => doc.SetHeadingLevel(0, 7));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void SetHeadingLevel_ValidLevel_NoException()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("Title", 1);
        var ex = Record.Exception(() => doc.SetHeadingLevel(0, 2));
        Assert.Null(ex);
    }

    [Fact]
    public void SetHeadingLevel_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("Title", 1);
        doc.AppendParagraph("Body");
        int before = doc.ParagraphCount;
        doc.SetHeadingLevel(0, 2);
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void SetHeadingLevel_TextUnchanged()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("My Heading", 1);
        doc.SetHeadingLevel(0, 3);
        Assert.Equal("My Heading", doc.GetParagraphText(0));
    }

    [Fact]
    public void SetHeadingLevel_LevelReturned()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("Title", 1);
        doc.SetHeadingLevel(0, 4);
        Assert.Equal(4, doc.GetHeadingLevel(0));
    }

    // -------------------------------------------------------------------------
    // Dogfood pipelines
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_SetMultipleLevels_EachCorrect()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("H1", 1);
        doc.AppendHeading("H2", 1);
        doc.AppendHeading("H3", 1);
        doc.SetHeadingLevel(0, 1);
        doc.SetHeadingLevel(1, 2);
        doc.SetHeadingLevel(2, 3);
        Assert.Equal(1, doc.GetHeadingLevel(0));
        Assert.Equal(2, doc.GetHeadingLevel(1));
        Assert.Equal(3, doc.GetHeadingLevel(2));
    }

    [Fact]
    public void DogfoodPipeline_RelevelTwice_FinalLevelCorrect()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("Title", 1);
        doc.SetHeadingLevel(0, 3);
        doc.SetHeadingLevel(0, 5);
        Assert.Equal(5, doc.GetHeadingLevel(0));
        Assert.Equal("Title", doc.GetParagraphText(0));
    }
}
