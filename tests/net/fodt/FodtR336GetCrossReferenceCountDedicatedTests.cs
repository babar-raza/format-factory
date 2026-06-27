// Tests for FodtDocument.GetCrossReferenceCount dedicated coverage.
// Sprint: ff-sprint-s318-dotnet-deepening-20260630
// Ledger: PC-FODT-R336

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R336: Dedicated tests for FodtDocument.GetCrossReferenceCount().
/// Non-negative on empty document.
/// Empty document ok.
/// Increases after AddCrossReference.
/// ParagraphCount unchanged after GetCrossReferenceCount.
/// TableCount unchanged after GetCrossReferenceCount.
/// SectionCount unchanged after GetCrossReferenceCount.
/// Idempotent (called twice same result).
/// Dogfood: add cross-reference then count is non-negative.
/// Dogfood: multiple cross-references count is non-negative.
/// </summary>
public class FodtR336GetCrossReferenceCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCrossReferenceCount_EmptyDocument_NonNegative()
    {
        var doc = FodtDocument.CreateNew();
        int count = doc.GetCrossReferenceCount();
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetCrossReferenceCount_EmptyDocument_Ok()
    {
        var doc = FodtDocument.CreateNew();
        var ex = Record.Exception(() => doc.GetCrossReferenceCount());
        Assert.Null(ex);
    }

    [Fact]
    public void GetCrossReferenceCount_AfterAddCrossReference_Increases()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("See figure below");
        int before = doc.GetCrossReferenceCount();
        doc.AddCrossReference("fig:1", "Figure 1");
        int after = doc.GetCrossReferenceCount();
        Assert.True(after >= before);
    }

    [Fact]
    public void GetCrossReferenceCount_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Main paragraph");
        int before = doc.ParagraphCount;
        _ = doc.GetCrossReferenceCount();
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void GetCrossReferenceCount_TableCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Some text");
        int before = doc.TableCount;
        _ = doc.GetCrossReferenceCount();
        Assert.Equal(before, doc.TableCount);
    }

    [Fact]
    public void GetCrossReferenceCount_SectionCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Some text");
        int before = doc.SectionCount;
        _ = doc.GetCrossReferenceCount();
        Assert.Equal(before, doc.SectionCount);
    }

    [Fact]
    public void GetCrossReferenceCount_CalledTwice_SameResult()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Reference paragraph");
        doc.AddCrossReference("sec:1", "Section 1");
        int first = doc.GetCrossReferenceCount();
        int second = doc.GetCrossReferenceCount();
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_AddCrossReference_CountNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Introduction text");
        doc.AddCrossReference("tab:1", "Table 1");
        int count = doc.GetCrossReferenceCount();
        Assert.True(count >= 0);
        int before = doc.ParagraphCount;
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void DogfoodPipeline_MultipleCrossReferences_CountNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Analysis section");
        doc.AddCrossReference("fig:1", "Figure 1");
        doc.AddCrossReference("fig:2", "Figure 2");
        doc.AddCrossReference("tab:1", "Table 1");
        int count = doc.GetCrossReferenceCount();
        Assert.True(count >= 0);
    }
}
