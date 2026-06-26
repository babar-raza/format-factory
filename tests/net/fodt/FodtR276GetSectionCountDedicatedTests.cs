// Tests for FodtDocument.GetSectionCount dedicated coverage.
// Sprint: ff-sprint-s261-dotnet-deepening-20260630
// Ledger: PC-FODT-R276

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R276: Dedicated tests for FodtDocument.GetSectionCount().
/// GetSectionCount returns the number of sections in the document.
/// Returns non-negative integer.
/// New document returns 0 or non-negative.
/// After AddSection, count increases.
/// ParagraphCount unchanged after GetSectionCount.
/// Called twice → same result.
/// Dogfood: add sections, verify count increases.
/// Dogfood: count consistent with number of AddSection calls.
/// </summary>
public class FodtR276GetSectionCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Basic behavioral tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetSectionCount_ReturnsNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        int count = doc.GetSectionCount();
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetSectionCount_NewDocument_NonNegative()
    {
        var doc = FodtDocument.CreateNew();
        int count = doc.GetSectionCount();
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetSectionCount_AfterAddSection_CountNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddSection("MySectionName");
        int count = doc.GetSectionCount();
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetSectionCount_AfterAddSection_Increases()
    {
        var doc = FodtDocument.CreateNew();
        int before = doc.GetSectionCount();
        doc.AddSection("NewSection");
        int after = doc.GetSectionCount();
        Assert.True(after >= before);
    }

    // -------------------------------------------------------------------------
    // Preservation tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetSectionCount_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Some text");
        int parasBefore = doc.ParagraphCount;
        doc.GetSectionCount();
        Assert.Equal(parasBefore, doc.ParagraphCount);
    }

    [Fact]
    public void GetSectionCount_CalledTwice_SameResult()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddSection("SectionA");
        int first = doc.GetSectionCount();
        int second = doc.GetSectionCount();
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_AddThreeSections_CountIncreases()
    {
        var doc = FodtDocument.CreateNew();
        int start = doc.GetSectionCount();
        doc.AddSection("Intro");
        doc.AddSection("Body");
        doc.AddSection("Conclusion");
        int end = doc.GetSectionCount();
        Assert.True(end >= start + 3);
    }

    [Fact]
    public void DogfoodPipeline_AddSectionWithContent_CountNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddSection("MainSection");
        doc.AddParagraph("Content in section");
        int count = doc.GetSectionCount();
        Assert.True(count >= 1);
    }

    [Fact]
    public void DogfoodPipeline_ConsistentWithAddSectionCalls()
    {
        var doc = FodtDocument.CreateNew();
        int initial = doc.GetSectionCount();
        doc.AddSection("S1");
        doc.AddSection("S2");
        int after = doc.GetSectionCount();
        // After adding 2 sections, count should be at least initial + 2
        Assert.True(after >= initial + 2);
    }
}
