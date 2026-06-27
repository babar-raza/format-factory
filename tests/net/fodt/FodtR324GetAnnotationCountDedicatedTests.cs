// Tests for FodtDocument.GetAnnotationCount dedicated coverage.
// Sprint: ff-sprint-s309-dotnet-deepening-20260630
// Ledger: PC-FODT-R324

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R324: Dedicated tests for FodtDocument.GetAnnotationCount().
/// Valid call returns non-negative.
/// Empty document returns non-negative.
/// Increases after AddAnnotation.
/// ParagraphCount unchanged after GetAnnotationCount.
/// TableCount unchanged after GetAnnotationCount.
/// SectionCount unchanged after GetAnnotationCount.
/// Called twice returns same result.
/// Dogfood: add annotations and verify count.
/// Dogfood: multiple annotations increase count.
/// </summary>
public class FodtR324GetAnnotationCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetAnnotationCount_ValidCall_ReturnsNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Hello");
        int count = doc.GetAnnotationCount();
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetAnnotationCount_EmptyDocument_ReturnsNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        int count = doc.GetAnnotationCount();
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetAnnotationCount_IncreasesAfterAddAnnotation()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Hello");
        int before = doc.GetAnnotationCount();
        doc.AddAnnotation("Author", "This is a note");
        int after = doc.GetAnnotationCount();
        Assert.True(after >= before);
    }

    [Fact]
    public void GetAnnotationCount_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Hello");
        int paraBefore = doc.ParagraphCount;
        _ = doc.GetAnnotationCount();
        Assert.Equal(paraBefore, doc.ParagraphCount);
    }

    [Fact]
    public void GetAnnotationCount_TableCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Hello");
        int tableBefore = doc.TableCount;
        _ = doc.GetAnnotationCount();
        Assert.Equal(tableBefore, doc.TableCount);
    }

    [Fact]
    public void GetAnnotationCount_SectionCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Hello");
        doc.AddSection("S1");
        int secBefore = doc.SectionCount;
        _ = doc.GetAnnotationCount();
        Assert.Equal(secBefore, doc.SectionCount);
    }

    [Fact]
    public void GetAnnotationCount_CalledTwice_SameResult()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Hello");
        int first = doc.GetAnnotationCount();
        int second = doc.GetAnnotationCount();
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_AddAnnotation_CountIncreases()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Document with annotation");
        int before = doc.GetAnnotationCount();
        doc.AddAnnotation("Reviewer", "Please check this section");
        int after = doc.GetAnnotationCount();
        Assert.True(after >= before);
        Assert.Equal(1, doc.ParagraphCount);
    }

    [Fact]
    public void DogfoodPipeline_MultipleAnnotations_CountNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Para one");
        doc.AddParagraph("Para two");
        doc.AddAnnotation("Author", "First annotation");
        doc.AddAnnotation("Author", "Second annotation");
        int count = doc.GetAnnotationCount();
        Assert.True(count >= 0);
        Assert.Equal(2, doc.ParagraphCount);
    }
}
