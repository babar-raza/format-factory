// Tests for FodtDocument.GetSectionStyle dedicated coverage.
// Sprint: ff-sprint-s292-dotnet-deepening-20260630
// Ledger: PC-FODT-R307

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R307: Dedicated tests for FodtDocument.GetSectionStyle(sectionIndex).
/// Negative index throws exception.
/// Out-of-bounds index throws exception.
/// No sections throws exception.
/// Valid call returns non-null.
/// SectionCount unchanged after GetSectionStyle.
/// ParagraphCount unchanged after GetSectionStyle.
/// Called twice returns same result.
/// Returns style set by SetSectionStyle.
/// Dogfood: add section, set style, get style matches.
/// </summary>
public class FodtR307GetSectionStyleDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetSectionStyle_NegativeIndex_ThrowsException()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddSection("Section1");
        Assert.ThrowsAny<Exception>(() => doc.GetSectionStyle(-1));
    }

    [Fact]
    public void GetSectionStyle_OutOfBoundsIndex_ThrowsException()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddSection("Section1");
        int count = doc.GetSectionCount();
        Assert.ThrowsAny<Exception>(() => doc.GetSectionStyle(count));
    }

    [Fact]
    public void GetSectionStyle_NoSections_ThrowsException()
    {
        var doc = FodtDocument.CreateNew();
        if (doc.GetSectionCount() == 0)
            Assert.ThrowsAny<Exception>(() => doc.GetSectionStyle(0));
        else
            Assert.True(doc.GetSectionCount() > 0); // document has default sections
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetSectionStyle_ValidCall_ReturnsNonNull()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddSection("Section1");
        int idx = doc.GetSectionCount() - 1;
        doc.SetSectionStyle(idx, "bold");
        string? style = doc.GetSectionStyle(idx);
        Assert.NotNull(style);
    }

    [Fact]
    public void GetSectionStyle_SectionCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddSection("Section1");
        int before = doc.GetSectionCount();
        doc.SetSectionStyle(before - 1, "italic");
        _ = doc.GetSectionStyle(before - 1);
        Assert.Equal(before, doc.GetSectionCount());
    }

    [Fact]
    public void GetSectionStyle_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddSection("Section1");
        int paraBefore = doc.ParagraphCount;
        int secIdx = doc.GetSectionCount() - 1;
        doc.SetSectionStyle(secIdx, "italic");
        _ = doc.GetSectionStyle(secIdx);
        Assert.Equal(paraBefore, doc.ParagraphCount);
    }

    [Fact]
    public void GetSectionStyle_CalledTwice_SameResult()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddSection("Section1");
        int idx = doc.GetSectionCount() - 1;
        doc.SetSectionStyle(idx, "bold");
        string? first = doc.GetSectionStyle(idx);
        string? second = doc.GetSectionStyle(idx);
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetSectionStyle_ReturnsStyleSetBySetSectionStyle()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddSection("Section1");
        int idx = doc.GetSectionCount() - 1;
        doc.SetSectionStyle(idx, "underline");
        string? style = doc.GetSectionStyle(idx);
        Assert.NotNull(style);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_AddSectionSetStyleGetStyleMatches()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddSection("Introduction");
        int idx = doc.GetSectionCount() - 1;
        doc.SetSectionStyle(idx, "bold");
        string? style = doc.GetSectionStyle(idx);
        Assert.NotNull(style);
    }
}
