// Tests for FodtDocument.GetSectionCount dedicated coverage.
// Sprint: ff-sprint-s281-dotnet-deepening-20260630
// Ledger: PC-FODT-R296

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R296: Dedicated tests for FodtDocument.GetSectionCount().
/// Returns non-negative int.
/// Increases after AddSection.
/// ParagraphCount unchanged after GetSectionCount.
/// TableCount unchanged after GetSectionCount.
/// Called twice returns same result.
/// Adding two sections increases count by at least 2.
/// GetSectionCount matches SectionCount-style tracking.
/// Dogfood: add named section, count increases.
/// Dogfood: multiple sections accumulated correctly.
/// </summary>
public class FodtR296GetSectionCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetSectionCount_ReturnsNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        int count = doc.GetSectionCount();
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetSectionCount_IncreasesAfterAddSection()
    {
        var doc = FodtDocument.CreateNew();
        int before = doc.GetSectionCount();
        doc.AddSection("NewSection");
        int after = doc.GetSectionCount();
        Assert.True(after > before);
    }

    [Fact]
    public void GetSectionCount_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        int paraBefore = doc.ParagraphCount;
        _ = doc.GetSectionCount();
        Assert.Equal(paraBefore, doc.ParagraphCount);
    }

    [Fact]
    public void GetSectionCount_TableCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        int tableBefore = doc.TableCount;
        _ = doc.GetSectionCount();
        Assert.Equal(tableBefore, doc.TableCount);
    }

    [Fact]
    public void GetSectionCount_CalledTwice_SameResult()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddSection("Sec");
        int first = doc.GetSectionCount();
        int second = doc.GetSectionCount();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetSectionCount_AddTwoSections_IncreasedByAtLeastTwo()
    {
        var doc = FodtDocument.CreateNew();
        int before = doc.GetSectionCount();
        doc.AddSection("Sec1");
        doc.AddSection("Sec2");
        int after = doc.GetSectionCount();
        Assert.True(after >= before + 2);
    }

    [Fact]
    public void GetSectionCount_NewDocument_CountAtLeastZero()
    {
        var doc = FodtDocument.CreateNew();
        Assert.True(doc.GetSectionCount() >= 0);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_AddNamedSection_CountIncreases()
    {
        var doc = FodtDocument.CreateNew();
        int before = doc.GetSectionCount();
        doc.AddSection("Introduction");
        int after = doc.GetSectionCount();
        Assert.True(after > before);
    }

    [Fact]
    public void DogfoodPipeline_MultipleSections_AccumulatedCorrectly()
    {
        var doc = FodtDocument.CreateNew();
        int before = doc.GetSectionCount();
        doc.AddSection("SectionA");
        doc.AddSection("SectionB");
        doc.AddSection("SectionC");
        int after = doc.GetSectionCount();
        Assert.True(after >= before + 3);
    }
}
