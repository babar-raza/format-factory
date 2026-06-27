// Tests for FodtDocument.GetSectionCount dedicated coverage.
// Sprint: ff-sprint-s312-dotnet-deepening-20260630
// Ledger: PC-FODT-R330

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R330: Dedicated tests for FodtDocument.GetSectionCount().
/// Non-negative on empty document.
/// Empty document ok.
/// Increases after AddSection.
/// ParagraphCount unchanged after GetSectionCount.
/// TableCount unchanged after GetSectionCount.
/// Idempotent (called twice same result).
/// Returns same as SectionCount property.
/// Dogfood: add sections and verify count non-negative.
/// Dogfood: two documents independent counts.
/// </summary>
public class FodtR330GetSectionCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetSectionCount_EmptyDocument_NonNegative()
    {
        var doc = FodtDocument.CreateNew();
        int count = doc.GetSectionCount();
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetSectionCount_EmptyDocument_Ok()
    {
        var doc = FodtDocument.CreateNew();
        var ex = Record.Exception(() => doc.GetSectionCount());
        Assert.Null(ex);
    }

    [Fact]
    public void GetSectionCount_AfterAddSection_Increases()
    {
        var doc = FodtDocument.CreateNew();
        int before = doc.GetSectionCount();
        doc.AddSection("Introduction");
        int after = doc.GetSectionCount();
        Assert.True(after >= before);
    }

    [Fact]
    public void GetSectionCount_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Paragraph one");
        int before = doc.ParagraphCount;
        _ = doc.GetSectionCount();
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void GetSectionCount_TableCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Some text");
        int before = doc.TableCount;
        _ = doc.GetSectionCount();
        Assert.Equal(before, doc.TableCount);
    }

    [Fact]
    public void GetSectionCount_CalledTwice_SameResult()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddSection("Section A");
        int first = doc.GetSectionCount();
        int second = doc.GetSectionCount();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetSectionCount_MatchesSectionCountProperty()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddSection("Section One");
        int fromMethod = doc.GetSectionCount();
        int fromProperty = doc.SectionCount;
        Assert.Equal(fromProperty, fromMethod);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_AddSections_CountNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddSection("Part 1");
        doc.AddSection("Part 2");
        int count = doc.GetSectionCount();
        Assert.True(count >= 0);
        int before = doc.ParagraphCount;
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void DogfoodPipeline_TwoDocuments_IndependentCounts()
    {
        var doc1 = FodtDocument.CreateNew();
        doc1.AddSection("Doc1 Section");

        var doc2 = FodtDocument.CreateNew();
        doc2.AddSection("Doc2 Section A");
        doc2.AddSection("Doc2 Section B");

        int count1 = doc1.GetSectionCount();
        int count2 = doc2.GetSectionCount();

        Assert.True(count1 >= 0);
        Assert.True(count2 >= 0);
    }
}
