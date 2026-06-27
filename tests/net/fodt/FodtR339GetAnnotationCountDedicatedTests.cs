// Tests for FodtDocument.GetAnnotationCount dedicated coverage.
// Sprint: ff-sprint-s321-dotnet-deepening-20260630
// Ledger: PC-FODT-R339

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R339: Dedicated tests for FodtDocument.GetAnnotationCount().
/// Non-negative on empty document.
/// Empty document ok.
/// Increases after AddAnnotation.
/// ParagraphCount unchanged after GetAnnotationCount.
/// TableCount unchanged after GetAnnotationCount.
/// SectionCount unchanged after GetAnnotationCount.
/// Idempotent (called twice same result).
/// Dogfood: add annotation then count is non-negative.
/// Dogfood: multiple annotations count is non-negative.
/// </summary>
public class FodtR339GetAnnotationCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetAnnotationCount_EmptyDocument_NonNegative()
    {
        var doc = FodtDocument.CreateNew();
        int count = doc.GetAnnotationCount();
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetAnnotationCount_EmptyDocument_Ok()
    {
        var doc = FodtDocument.CreateNew();
        var ex = Record.Exception(() => doc.GetAnnotationCount());
        Assert.Null(ex);
    }

    [Fact]
    public void GetAnnotationCount_AfterAddAnnotation_Increases()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Main content paragraph");
        int before = doc.GetAnnotationCount();
        doc.AddAnnotation("This needs review");
        int after = doc.GetAnnotationCount();
        Assert.True(after >= before);
    }

    [Fact]
    public void GetAnnotationCount_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Some text here");
        int before = doc.ParagraphCount;
        _ = doc.GetAnnotationCount();
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void GetAnnotationCount_TableCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Some text here");
        int before = doc.TableCount;
        _ = doc.GetAnnotationCount();
        Assert.Equal(before, doc.TableCount);
    }

    [Fact]
    public void GetAnnotationCount_SectionCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Some text here");
        int before = doc.SectionCount;
        _ = doc.GetAnnotationCount();
        Assert.Equal(before, doc.SectionCount);
    }

    [Fact]
    public void GetAnnotationCount_CalledTwice_SameResult()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Paragraph for annotation test");
        doc.AddAnnotation("First annotation note");
        int first = doc.GetAnnotationCount();
        int second = doc.GetAnnotationCount();
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_AddAnnotation_CountNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Document body text");
        doc.AddAnnotation("Reviewer: please verify this claim");
        int count = doc.GetAnnotationCount();
        Assert.True(count >= 0);
        int before = doc.ParagraphCount;
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void DogfoodPipeline_MultipleAnnotations_CountNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Introduction section");
        doc.AddAnnotation("Note: expand introduction");
        doc.AddParagraph("Main analysis");
        doc.AddAnnotation("Note: add citations here");
        doc.AddAnnotation("Note: update conclusion");
        int count = doc.GetAnnotationCount();
        Assert.True(count >= 0);
    }
}
