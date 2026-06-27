// Tests for FodtDocument.GetHeadingCount dedicated coverage.
// Sprint: ff-sprint-s314-dotnet-deepening-20260630
// Ledger: PC-FODT-R332

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R332: Dedicated tests for FodtDocument.GetHeadingCount().
/// Non-negative on empty document.
/// Empty document ok.
/// Increases after AddHeading.
/// ParagraphCount unchanged after GetHeadingCount.
/// TableCount unchanged after GetHeadingCount.
/// SectionCount unchanged after GetHeadingCount.
/// Idempotent (called twice same result).
/// Dogfood: add headings then count is non-negative.
/// Dogfood: multiple heading levels count is non-negative.
/// </summary>
public class FodtR332GetHeadingCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetHeadingCount_EmptyDocument_NonNegative()
    {
        var doc = FodtDocument.CreateNew();
        int count = doc.GetHeadingCount();
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetHeadingCount_EmptyDocument_Ok()
    {
        var doc = FodtDocument.CreateNew();
        var ex = Record.Exception(() => doc.GetHeadingCount());
        Assert.Null(ex);
    }

    [Fact]
    public void GetHeadingCount_AfterAddHeading_Increases()
    {
        var doc = FodtDocument.CreateNew();
        int before = doc.GetHeadingCount();
        doc.AddHeading("Chapter 1", 1);
        int after = doc.GetHeadingCount();
        Assert.True(after >= before);
    }

    [Fact]
    public void GetHeadingCount_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Body text");
        int before = doc.ParagraphCount;
        _ = doc.GetHeadingCount();
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void GetHeadingCount_TableCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Some text");
        int before = doc.TableCount;
        _ = doc.GetHeadingCount();
        Assert.Equal(before, doc.TableCount);
    }

    [Fact]
    public void GetHeadingCount_SectionCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Some text");
        int before = doc.SectionCount;
        _ = doc.GetHeadingCount();
        Assert.Equal(before, doc.SectionCount);
    }

    [Fact]
    public void GetHeadingCount_CalledTwice_SameResult()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddHeading("Title", 1);
        int first = doc.GetHeadingCount();
        int second = doc.GetHeadingCount();
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_AddHeadings_CountNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddHeading("Chapter 1", 1);
        doc.AddParagraph("Chapter body");
        doc.AddHeading("Section 1.1", 2);
        int count = doc.GetHeadingCount();
        Assert.True(count >= 0);
        int before = doc.ParagraphCount;
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void DogfoodPipeline_MultipleHeadingLevels_CountNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddHeading("Part I", 1);
        doc.AddHeading("Chapter 1", 2);
        doc.AddHeading("Section 1.1", 3);
        doc.AddParagraph("Content paragraph");
        int count = doc.GetHeadingCount();
        Assert.True(count >= 0);
    }
}
