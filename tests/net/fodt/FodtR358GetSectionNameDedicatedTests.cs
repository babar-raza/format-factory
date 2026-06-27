// Tests for FodtDocument.GetSectionName dedicated coverage.
// Sprint: ff-sprint-s340-dotnet-deepening-20260630
// Ledger: PC-FODT-R358

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R358: Dedicated tests for FodtDocument.GetSectionName().
/// Negative index throws.
/// Out-of-range index throws.
/// Empty document with no sections: index 0 throws.
/// Returns non-null for valid index.
/// ParagraphCount unchanged after GetSectionName.
/// SectionCount unchanged after GetSectionName.
/// Idempotent (called twice same result).
/// After AddSection returns correct name.
/// Dogfood: multiple sections each returns correct name.
/// </summary>
public class FodtR358GetSectionNameDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetSectionName_NegativeIndex_Throws()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddSection("Introduction");
        Assert.ThrowsAny<Exception>(() => doc.GetSectionName(-1));
    }

    [Fact]
    public void GetSectionName_OutOfRangeIndex_Throws()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddSection("Introduction");
        Assert.ThrowsAny<Exception>(() => doc.GetSectionName(10));
    }

    [Fact]
    public void GetSectionName_EmptyDocument_Throws()
    {
        var doc = FodtDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetSectionName(0));
    }

    [Fact]
    public void GetSectionName_ValidIndex_ReturnsNonNull()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddSection("Executive Summary");
        string? name = doc.GetSectionName(0);
        Assert.NotNull(name);
    }

    [Fact]
    public void GetSectionName_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddSection("Overview");
        doc.AddParagraph("Section content");
        int before = doc.ParagraphCount;
        _ = doc.GetSectionName(0);
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void GetSectionName_SectionCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddSection("Overview");
        int before = doc.SectionCount;
        _ = doc.GetSectionName(0);
        Assert.Equal(before, doc.SectionCount);
    }

    [Fact]
    public void GetSectionName_CalledTwice_SameResult()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddSection("Stable Section");
        string? first = doc.GetSectionName(0);
        string? second = doc.GetSectionName(0);
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetSectionName_AfterAddSection_ReturnsCorrectName()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddSection("Financial Analysis");
        string? name = doc.GetSectionName(0);
        Assert.NotNull(name);
        Assert.Equal("Financial Analysis", name);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_MultipleSections_EachReturnsCorrectName()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddSection("Part One");
        doc.AddSection("Part Two");
        doc.AddSection("Part Three");
        Assert.Equal("Part One", doc.GetSectionName(0));
        Assert.Equal("Part Two", doc.GetSectionName(1));
        Assert.Equal("Part Three", doc.GetSectionName(2));
    }
}
