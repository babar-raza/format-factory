// Tests for FodtDocument.GetSectionType dedicated coverage.
// Sprint: ff-sprint-s348-dotnet-deepening-20260630
// Ledger: PC-FODT-R366

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R366: Dedicated tests for FodtDocument.GetSectionType().
/// Negative section index throws.
/// Out-of-range section index throws.
/// Empty document (no sections) throws.
/// Valid section returns non-null.
/// ParagraphCount unchanged after GetSectionType.
/// SectionCount unchanged after GetSectionType.
/// Idempotent (called twice same result).
/// After AddSection returns expected type string.
/// Dogfood: multiple sections each returns non-null type.
/// </summary>
public class FodtR366GetSectionTypesDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetSectionType_NegativeSectionIndex_Throws()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddSection("Intro");
        Assert.ThrowsAny<Exception>(() => doc.GetSectionType(-1));
    }

    [Fact]
    public void GetSectionType_OutOfRangeIndex_Throws()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddSection("Intro");
        Assert.ThrowsAny<Exception>(() => doc.GetSectionType(99));
    }

    [Fact]
    public void GetSectionType_EmptyDocument_Throws()
    {
        var doc = FodtDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetSectionType(0));
    }

    [Fact]
    public void GetSectionType_ValidSection_ReturnsNonNull()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddSection("Overview");
        string? type = doc.GetSectionType(0);
        Assert.NotNull(type);
    }

    [Fact]
    public void GetSectionType_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Introduction text");
        doc.AddSection("Body");
        int before = doc.ParagraphCount;
        _ = doc.GetSectionType(0);
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void GetSectionType_SectionCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddSection("Chapter 1");
        int before = doc.SectionCount;
        _ = doc.GetSectionType(0);
        Assert.Equal(before, doc.SectionCount);
    }

    [Fact]
    public void GetSectionType_CalledTwice_SameResult()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddSection("Stable");
        string? first = doc.GetSectionType(0);
        string? second = doc.GetSectionType(0);
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetSectionType_AfterAddSection_ReturnsNonNull()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddSection("Appendix");
        string? type = doc.GetSectionType(0);
        Assert.NotNull(type);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_MultipleSections_EachReturnsNonNull()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddSection("Executive Summary");
        doc.AddSection("Financial Analysis");
        doc.AddSection("Conclusions");
        Assert.NotNull(doc.GetSectionType(0));
        Assert.NotNull(doc.GetSectionType(1));
        Assert.NotNull(doc.GetSectionType(2));
    }
}
