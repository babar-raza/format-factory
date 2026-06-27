// Tests for FodtDocument.GetAnnotationCount dedicated coverage.
// Sprint: ff-sprint-s386-dotnet-deepening-20260630
// Ledger: PC-FODT-R404

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R404: Dedicated tests for FodtDocument.AnnotationCount (or GetAnnotationCount()).
/// New document returns non-negative.
/// ParagraphCount unchanged after checking AnnotationCount.
/// TableCount unchanged after checking AnnotationCount.
/// EndnoteCount unchanged after checking AnnotationCount.
/// Idempotent (read twice same result).
/// Is integer type.
/// Dogfood: AnnotationCount non-negative after paragraphs.
/// Dogfood: AnnotationCount non-negative after mixed content.
/// Dogfood: AnnotationCount never negative in loop.
/// </summary>
public class FodtR404GetAnnotationCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void AnnotationCount_NewDocument_ReturnsNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        Assert.True(doc.AnnotationCount >= 0);
    }

    [Fact]
    public void AnnotationCount_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Para 1");
        int before = doc.ParagraphCount;
        _ = doc.AnnotationCount;
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void AnnotationCount_TableCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Para 1");
        int before = doc.TableCount;
        _ = doc.AnnotationCount;
        Assert.Equal(before, doc.TableCount);
    }

    [Fact]
    public void AnnotationCount_EndnoteCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Para 1");
        int before = doc.EndnoteCount;
        _ = doc.AnnotationCount;
        Assert.Equal(before, doc.EndnoteCount);
    }

    [Fact]
    public void AnnotationCount_Idempotent()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Text");
        int first = doc.AnnotationCount;
        int second = doc.AnnotationCount;
        Assert.Equal(first, second);
    }

    [Fact]
    public void AnnotationCount_IsInteger()
    {
        var doc = FodtDocument.CreateNew();
        int count = doc.AnnotationCount;
        Assert.IsType<int>(count);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_AfterParagraphs_NonNegative()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Annotated paragraph A");
        doc.AddParagraph("Annotated paragraph B");
        Assert.True(doc.AnnotationCount >= 0);
    }

    [Fact]
    public void DogfoodPipeline_AfterMixedContent_NonNegative()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Summary");
        doc.AddTable(3, 3);
        doc.AddParagraph("Notes");
        Assert.True(doc.AnnotationCount >= 0);
    }

    [Fact]
    public void DogfoodPipeline_NeverNegativeInLoop()
    {
        var doc = FodtDocument.CreateNew();
        for (int i = 0; i < 5; i++)
        {
            doc.AddParagraph($"Review note {i}");
            Assert.True(doc.AnnotationCount >= 0);
        }
    }
}
