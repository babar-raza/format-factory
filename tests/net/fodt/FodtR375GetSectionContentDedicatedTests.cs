// Tests for FodtDocument.GetSectionContent dedicated coverage.
// Sprint: ff-sprint-s357-dotnet-deepening-20260630
// Ledger: PC-FODT-R375

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R375: Dedicated tests for FodtDocument.GetSectionContent().
/// Negative section index throws.
/// Out-of-range section index throws.
/// Empty document (no sections) throws.
/// Valid section returns non-null.
/// SectionCount unchanged after GetSectionContent.
/// ParagraphCount unchanged after GetSectionContent.
/// Idempotent (called twice same result).
/// Dogfood: AddSection with content then Get returns expected.
/// Dogfood: multiple sections each returns non-null content.
/// </summary>
public class FodtR375GetSectionContentDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetSectionContent_NegativeIndex_Throws()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddSection("Summary");
        Assert.ThrowsAny<Exception>(() => doc.GetSectionContent(-1));
    }

    [Fact]
    public void GetSectionContent_OutOfRangeIndex_Throws()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddSection("Summary");
        Assert.ThrowsAny<Exception>(() => doc.GetSectionContent(99));
    }

    [Fact]
    public void GetSectionContent_EmptyDocument_Throws()
    {
        var doc = FodtDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetSectionContent(0));
    }

    [Fact]
    public void GetSectionContent_ValidSection_ReturnsNonNull()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddSection("Introduction");
        string? content = doc.GetSectionContent(0);
        Assert.NotNull(content);
    }

    [Fact]
    public void GetSectionContent_SectionCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddSection("Chapter 1");
        int before = doc.SectionCount;
        _ = doc.GetSectionContent(0);
        Assert.Equal(before, doc.SectionCount);
    }

    [Fact]
    public void GetSectionContent_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Header paragraph");
        doc.AddSection("Body");
        int before = doc.ParagraphCount;
        _ = doc.GetSectionContent(0);
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void GetSectionContent_CalledTwice_SameResult()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddSection("Stable");
        string? first = doc.GetSectionContent(0);
        string? second = doc.GetSectionContent(0);
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_AddSectionWithContent_ReturnsNonNull()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddSection("Financial Summary", "Revenue: $1.2M\nExpenses: $0.8M\nProfit: $0.4M");
        string? content = doc.GetSectionContent(0);
        Assert.NotNull(content);
    }

    [Fact]
    public void DogfoodPipeline_MultipleSections_EachNonNullContent()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddSection("Executive Summary", "High-level overview");
        doc.AddSection("Methodology", "Research approach details");
        doc.AddSection("Conclusions", "Key findings and next steps");
        Assert.NotNull(doc.GetSectionContent(0));
        Assert.NotNull(doc.GetSectionContent(1));
        Assert.NotNull(doc.GetSectionContent(2));
    }
}
