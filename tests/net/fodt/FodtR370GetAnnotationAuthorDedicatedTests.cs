// Tests for FodtDocument.GetAnnotationAuthor dedicated coverage.
// Sprint: ff-sprint-s352-dotnet-deepening-20260630
// Ledger: PC-FODT-R370

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R370: Dedicated tests for FodtDocument.GetAnnotationAuthor().
/// Negative annotation index throws.
/// Out-of-range annotation index throws.
/// Empty document (no annotations) throws.
/// Valid annotation returns non-null.
/// AnnotationCount unchanged after GetAnnotationAuthor.
/// ParagraphCount unchanged after GetAnnotationAuthor.
/// Idempotent (called twice same result).
/// Dogfood: AddAnnotation with author then Get returns expected author.
/// Dogfood: multiple annotations each returns non-null author.
/// </summary>
public class FodtR370GetAnnotationAuthorDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetAnnotationAuthor_NegativeIndex_Throws()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddAnnotation("Review note", "Alice");
        Assert.ThrowsAny<Exception>(() => doc.GetAnnotationAuthor(-1));
    }

    [Fact]
    public void GetAnnotationAuthor_OutOfRangeIndex_Throws()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddAnnotation("Review note", "Alice");
        Assert.ThrowsAny<Exception>(() => doc.GetAnnotationAuthor(99));
    }

    [Fact]
    public void GetAnnotationAuthor_EmptyDocument_Throws()
    {
        var doc = FodtDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetAnnotationAuthor(0));
    }

    [Fact]
    public void GetAnnotationAuthor_ValidAnnotation_ReturnsNonNull()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddAnnotation("Check this section", "Bob");
        string? author = doc.GetAnnotationAuthor(0);
        Assert.NotNull(author);
    }

    [Fact]
    public void GetAnnotationAuthor_AnnotationCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddAnnotation("Note", "Carol");
        int before = doc.AnnotationCount;
        _ = doc.GetAnnotationAuthor(0);
        Assert.Equal(before, doc.AnnotationCount);
    }

    [Fact]
    public void GetAnnotationAuthor_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Document body");
        doc.AddAnnotation("Side note", "Dave");
        int before = doc.ParagraphCount;
        _ = doc.GetAnnotationAuthor(0);
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void GetAnnotationAuthor_CalledTwice_SameResult()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddAnnotation("Stable note", "Eve");
        string? first = doc.GetAnnotationAuthor(0);
        string? second = doc.GetAnnotationAuthor(0);
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_AddAnnotationWithAuthor_ReturnsExpectedAuthor()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddAnnotation("Please verify the calculations", "John Smith");
        string? author = doc.GetAnnotationAuthor(0);
        Assert.NotNull(author);
        Assert.Equal("John Smith", author);
    }

    [Fact]
    public void DogfoodPipeline_MultipleAnnotations_EachReturnsNonNull()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddAnnotation("First review comment", "Alice");
        doc.AddAnnotation("Second review comment", "Bob");
        doc.AddAnnotation("Third review comment", "Carol");
        Assert.NotNull(doc.GetAnnotationAuthor(0));
        Assert.NotNull(doc.GetAnnotationAuthor(1));
        Assert.NotNull(doc.GetAnnotationAuthor(2));
    }
}
