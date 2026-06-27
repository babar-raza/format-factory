// Tests for FodtDocument.GetAnnotationDate dedicated coverage.
// Sprint: ff-sprint-s353-dotnet-deepening-20260630
// Ledger: PC-FODT-R371

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R371: Dedicated tests for FodtDocument.GetAnnotationDate().
/// Negative annotation index throws.
/// Out-of-range annotation index throws.
/// Empty document (no annotations) throws.
/// Valid annotation returns non-null.
/// AnnotationCount unchanged after GetAnnotationDate.
/// ParagraphCount unchanged after GetAnnotationDate.
/// Idempotent (called twice same result).
/// Dogfood: AddAnnotation with date then Get returns expected date.
/// Dogfood: multiple annotations each returns non-null date.
/// </summary>
public class FodtR371GetAnnotationDateDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetAnnotationDate_NegativeIndex_Throws()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddAnnotation("Note", "Author", "2026-01-15");
        Assert.ThrowsAny<Exception>(() => doc.GetAnnotationDate(-1));
    }

    [Fact]
    public void GetAnnotationDate_OutOfRangeIndex_Throws()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddAnnotation("Note", "Author", "2026-01-15");
        Assert.ThrowsAny<Exception>(() => doc.GetAnnotationDate(99));
    }

    [Fact]
    public void GetAnnotationDate_EmptyDocument_Throws()
    {
        var doc = FodtDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetAnnotationDate(0));
    }

    [Fact]
    public void GetAnnotationDate_ValidAnnotation_ReturnsNonNull()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddAnnotation("Check data", "Reviewer", "2026-06-01");
        string? date = doc.GetAnnotationDate(0);
        Assert.NotNull(date);
    }

    [Fact]
    public void GetAnnotationDate_AnnotationCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddAnnotation("Fix typo", "Editor", "2026-03-15");
        int before = doc.AnnotationCount;
        _ = doc.GetAnnotationDate(0);
        Assert.Equal(before, doc.AnnotationCount);
    }

    [Fact]
    public void GetAnnotationDate_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Body content");
        doc.AddAnnotation("Side note", "Author", "2026-04-20");
        int before = doc.ParagraphCount;
        _ = doc.GetAnnotationDate(0);
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void GetAnnotationDate_CalledTwice_SameResult()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddAnnotation("Stable note", "User", "2026-05-10");
        string? first = doc.GetAnnotationDate(0);
        string? second = doc.GetAnnotationDate(0);
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_AddAnnotationWithDate_ReturnsExpectedDate()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddAnnotation("Review comment", "Jane Doe", "2026-07-01");
        string? date = doc.GetAnnotationDate(0);
        Assert.NotNull(date);
        Assert.Equal("2026-07-01", date);
    }

    [Fact]
    public void DogfoodPipeline_MultipleAnnotations_EachNonNullDate()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddAnnotation("First note", "Alice", "2026-01-01");
        doc.AddAnnotation("Second note", "Bob", "2026-02-01");
        doc.AddAnnotation("Third note", "Carol", "2026-03-01");
        Assert.NotNull(doc.GetAnnotationDate(0));
        Assert.NotNull(doc.GetAnnotationDate(1));
        Assert.NotNull(doc.GetAnnotationDate(2));
    }
}
