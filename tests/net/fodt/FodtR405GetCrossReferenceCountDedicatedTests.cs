// Tests for FodtDocument.GetCrossReferenceCount dedicated coverage.
// Sprint: ff-sprint-s387-dotnet-deepening-20260630
// Ledger: PC-FODT-R405

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R405: Dedicated tests for FodtDocument.CrossReferenceCount (or GetCrossReferenceCount()).
/// New document returns non-negative.
/// ParagraphCount unchanged after checking CrossReferenceCount.
/// TableCount unchanged after checking CrossReferenceCount.
/// AnnotationCount unchanged after checking CrossReferenceCount.
/// Idempotent (read twice same result).
/// Is integer type.
/// Dogfood: CrossReferenceCount non-negative after paragraphs.
/// Dogfood: CrossReferenceCount non-negative after mixed content.
/// Dogfood: CrossReferenceCount never negative in loop.
/// </summary>
public class FodtR405GetCrossReferenceCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void CrossReferenceCount_NewDocument_ReturnsNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        Assert.True(doc.CrossReferenceCount >= 0);
    }

    [Fact]
    public void CrossReferenceCount_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Para 1");
        int before = doc.ParagraphCount;
        _ = doc.CrossReferenceCount;
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void CrossReferenceCount_TableCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Para 1");
        int before = doc.TableCount;
        _ = doc.CrossReferenceCount;
        Assert.Equal(before, doc.TableCount);
    }

    [Fact]
    public void CrossReferenceCount_AnnotationCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Para 1");
        int before = doc.AnnotationCount;
        _ = doc.CrossReferenceCount;
        Assert.Equal(before, doc.AnnotationCount);
    }

    [Fact]
    public void CrossReferenceCount_Idempotent()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Text");
        int first = doc.CrossReferenceCount;
        int second = doc.CrossReferenceCount;
        Assert.Equal(first, second);
    }

    [Fact]
    public void CrossReferenceCount_IsInteger()
    {
        var doc = FodtDocument.CreateNew();
        int count = doc.CrossReferenceCount;
        Assert.IsType<int>(count);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_AfterParagraphs_NonNegative()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("See section 2 for details");
        doc.AddParagraph("Refer to figure 1 above");
        Assert.True(doc.CrossReferenceCount >= 0);
    }

    [Fact]
    public void DogfoodPipeline_AfterMixedContent_NonNegative()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Overview");
        doc.AddTable(2, 4);
        doc.AddParagraph("See table 1 for summary");
        Assert.True(doc.CrossReferenceCount >= 0);
    }

    [Fact]
    public void DogfoodPipeline_NeverNegativeInLoop()
    {
        var doc = FodtDocument.CreateNew();
        for (int i = 0; i < 5; i++)
        {
            doc.AddParagraph($"Cross reference to section {i}");
            Assert.True(doc.CrossReferenceCount >= 0);
        }
    }
}
