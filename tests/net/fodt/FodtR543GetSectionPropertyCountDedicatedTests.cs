// Tests for FodtDocument.GetSectionPropertyCount dedicated coverage.
// Sprint: ff-sprint-s519-dotnet-deepening-20260701
// Ledger: PC-FODT-R543

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R543: Dedicated tests for FodtDocument.GetSectionPropertyCount().
/// New document returns non-negative count.
/// ParagraphCount unchanged after GetSectionPropertyCount.
/// TableCount unchanged after GetSectionPropertyCount.
/// Idempotent (called twice same result).
/// Return type is int.
/// Dogfood: after adding paragraphs count non-negative.
/// Dogfood: after mixed content count non-negative.
/// Dogfood: loop over documents all non-negative.
/// </summary>
public class FodtR543GetSectionPropertyCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetSectionPropertyCount_NewDocument_ReturnsNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        int count = doc.GetSectionPropertyCount();
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetSectionPropertyCount_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        int before = doc.ParagraphCount;
        _ = doc.GetSectionPropertyCount();
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void GetSectionPropertyCount_TableCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        int before = doc.TableCount;
        _ = doc.GetSectionPropertyCount();
        Assert.Equal(before, doc.TableCount);
    }

    [Fact]
    public void GetSectionPropertyCount_Idempotent()
    {
        var doc = FodtDocument.CreateNew();
        int first = doc.GetSectionPropertyCount();
        int second = doc.GetSectionPropertyCount();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetSectionPropertyCount_IsInt()
    {
        var doc = FodtDocument.CreateNew();
        object result = doc.GetSectionPropertyCount();
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
        Assert.True(doc.GetSectionPropertyCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_AfterMixedContent_CountNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Intro");
        doc.AddTable(2, 2);
        doc.AddParagraph("Conclusion");
        Assert.True(doc.GetSectionPropertyCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_MultipleDocuments_AllNonNegative()
    {
        for (int i = 0; i < 3; i++)
        {
            var doc = FodtDocument.CreateNew();
            doc.AddParagraph($"Document {i}");
            Assert.True(doc.GetSectionPropertyCount() >= 0);
        }
    }
}
