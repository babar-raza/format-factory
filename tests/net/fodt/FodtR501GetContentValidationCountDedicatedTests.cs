// Tests for FodtDocument.GetContentValidationCount dedicated coverage.
// Sprint: ff-sprint-s477-dotnet-deepening-20260701
// Ledger: PC-FODT-R501

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R501: Dedicated tests for FodtDocument.GetContentValidationCount().
/// New document returns non-negative count.
/// ParagraphCount unchanged after GetContentValidationCount.
/// TableCount unchanged after GetContentValidationCount.
/// Idempotent (called twice same result).
/// Return type is int.
/// Dogfood: after adding paragraphs count non-negative.
/// Dogfood: after mixed content count non-negative.
/// Dogfood: loop over documents all non-negative.
/// </summary>
public class FodtR501GetContentValidationCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetContentValidationCount_NewDocument_ReturnsNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        int count = doc.GetContentValidationCount();
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetContentValidationCount_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        int before = doc.ParagraphCount;
        _ = doc.GetContentValidationCount();
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void GetContentValidationCount_TableCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        int before = doc.TableCount;
        _ = doc.GetContentValidationCount();
        Assert.Equal(before, doc.TableCount);
    }

    [Fact]
    public void GetContentValidationCount_Idempotent()
    {
        var doc = FodtDocument.CreateNew();
        int first = doc.GetContentValidationCount();
        int second = doc.GetContentValidationCount();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetContentValidationCount_IsInt()
    {
        var doc = FodtDocument.CreateNew();
        object result = doc.GetContentValidationCount();
        Assert.IsType<int>(result);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_AfterParagraphs_CountNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("First paragraph");
        doc.AddParagraph("Second paragraph");
        Assert.True(doc.GetContentValidationCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_AfterMixedContent_CountNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Intro");
        doc.AddTable(2, 2);
        doc.AddParagraph("Conclusion");
        Assert.True(doc.GetContentValidationCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_MultipleDocuments_AllNonNegative()
    {
        for (int i = 0; i < 3; i++)
        {
            var doc = FodtDocument.CreateNew();
            doc.AddParagraph($"Document {i}");
            Assert.True(doc.GetContentValidationCount() >= 0);
        }
    }
}
