// Tests for FodtDocument.GetAnnotationText dedicated coverage.
// Sprint: ff-sprint-s341-dotnet-deepening-20260630
// Ledger: PC-FODT-R359

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R359: Dedicated tests for FodtDocument.GetAnnotationText().
/// Negative index throws.
/// Out-of-range index throws.
/// Empty document with no annotations: index 0 throws.
/// Returns non-null for valid index.
/// AnnotationCount unchanged after GetAnnotationText.
/// ParagraphCount unchanged after GetAnnotationText.
/// Idempotent (called twice same result).
/// After AddAnnotation returns correct text.
/// Dogfood: multiple annotations each returns correct text.
/// </summary>
public class FodtR359GetAnnotationTextDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetAnnotationText_NegativeIndex_Throws()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddAnnotation("First note");
        Assert.ThrowsAny<Exception>(() => doc.GetAnnotationText(-1));
    }

    [Fact]
    public void GetAnnotationText_OutOfRangeIndex_Throws()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddAnnotation("First note");
        Assert.ThrowsAny<Exception>(() => doc.GetAnnotationText(10));
    }

    [Fact]
    public void GetAnnotationText_EmptyDocument_Throws()
    {
        var doc = FodtDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetAnnotationText(0));
    }

    [Fact]
    public void GetAnnotationText_ValidIndex_ReturnsNonNull()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddAnnotation("Review this section carefully");
        string? text = doc.GetAnnotationText(0);
        Assert.NotNull(text);
    }

    [Fact]
    public void GetAnnotationText_AnnotationCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddAnnotation("Note for reviewer");
        int before = doc.GetAnnotationCount();
        _ = doc.GetAnnotationText(0);
        Assert.Equal(before, doc.GetAnnotationCount());
    }

    [Fact]
    public void GetAnnotationText_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Body text");
        doc.AddAnnotation("Inline annotation");
        int before = doc.ParagraphCount;
        _ = doc.GetAnnotationText(0);
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void GetAnnotationText_CalledTwice_SameResult()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddAnnotation("Stable annotation text");
        string? first = doc.GetAnnotationText(0);
        string? second = doc.GetAnnotationText(0);
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetAnnotationText_AfterAddAnnotation_ReturnsCorrectText()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddAnnotation("Please verify the data source here");
        string? text = doc.GetAnnotationText(0);
        Assert.NotNull(text);
        Assert.Equal("Please verify the data source here", text);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_MultipleAnnotations_EachReturnsCorrectText()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddAnnotation("First annotation comment");
        doc.AddAnnotation("Second annotation comment");
        doc.AddAnnotation("Third annotation comment");
        Assert.Equal("First annotation comment", doc.GetAnnotationText(0));
        Assert.Equal("Second annotation comment", doc.GetAnnotationText(1));
        Assert.Equal("Third annotation comment", doc.GetAnnotationText(2));
    }
}
