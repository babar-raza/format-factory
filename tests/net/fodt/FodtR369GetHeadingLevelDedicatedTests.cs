// Tests for FodtDocument.GetHeadingLevel dedicated coverage.
// Sprint: ff-sprint-s351-dotnet-deepening-20260630
// Ledger: PC-FODT-R369

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R369: Dedicated tests for FodtDocument.GetHeadingLevel().
/// Negative heading index throws.
/// Out-of-range heading index throws.
/// Empty document (no headings) throws.
/// Valid heading returns positive level.
/// ParagraphCount unchanged after GetHeadingLevel.
/// TableCount unchanged after GetHeadingLevel.
/// Idempotent (called twice same result).
/// Dogfood: AddHeading level 1 returns 1.
/// Dogfood: AddHeading level 3 returns 3.
/// </summary>
public class FodtR369GetHeadingLevelDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetHeadingLevel_NegativeIndex_Throws()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddHeading("Chapter 1", 1);
        Assert.ThrowsAny<Exception>(() => doc.GetHeadingLevel(-1));
    }

    [Fact]
    public void GetHeadingLevel_OutOfRangeIndex_Throws()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddHeading("Chapter 1", 1);
        Assert.ThrowsAny<Exception>(() => doc.GetHeadingLevel(99));
    }

    [Fact]
    public void GetHeadingLevel_EmptyDocument_Throws()
    {
        var doc = FodtDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetHeadingLevel(0));
    }

    [Fact]
    public void GetHeadingLevel_ValidHeading_ReturnsPositive()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddHeading("Main Title", 1);
        int level = doc.GetHeadingLevel(0);
        Assert.True(level > 0);
    }

    [Fact]
    public void GetHeadingLevel_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Intro");
        doc.AddHeading("Section", 2);
        int before = doc.ParagraphCount;
        _ = doc.GetHeadingLevel(0);
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void GetHeadingLevel_TableCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddHeading("Section", 1);
        int before = doc.TableCount;
        _ = doc.GetHeadingLevel(0);
        Assert.Equal(before, doc.TableCount);
    }

    [Fact]
    public void GetHeadingLevel_CalledTwice_SameResult()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddHeading("Stable Heading", 2);
        int first = doc.GetHeadingLevel(0);
        int second = doc.GetHeadingLevel(0);
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_AddHeadingLevel1_ReturnsOne()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddHeading("Annual Report", 1);
        int level = doc.GetHeadingLevel(0);
        Assert.Equal(1, level);
    }

    [Fact]
    public void DogfoodPipeline_AddHeadingLevel3_ReturnsThree()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddHeading("Sub-sub-section", 3);
        int level = doc.GetHeadingLevel(0);
        Assert.Equal(3, level);
    }
}
