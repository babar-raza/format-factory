// Tests for FodtDocument.GetSoftHyphenCount dedicated coverage.
// Sprint: ff-sprint-s507-dotnet-deepening-20260701
// Ledger: PC-FODT-R531

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R531: Dedicated tests for FodtDocument.GetSoftHyphenCount().
/// New document returns non-negative count.
/// ParagraphCount unchanged after GetSoftHyphenCount.
/// TableCount unchanged after GetSoftHyphenCount.
/// Idempotent (called twice same result).
/// Return type is int.
/// Dogfood: after adding paragraphs count non-negative.
/// Dogfood: after mixed content count non-negative.
/// Dogfood: loop over documents all non-negative.
/// </summary>
public class FodtR531GetSoftHyphenCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetSoftHyphenCount_NewDocument_ReturnsNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        int count = doc.GetSoftHyphenCount();
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetSoftHyphenCount_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        int before = doc.ParagraphCount;
        _ = doc.GetSoftHyphenCount();
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void GetSoftHyphenCount_TableCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        int before = doc.TableCount;
        _ = doc.GetSoftHyphenCount();
        Assert.Equal(before, doc.TableCount);
    }

    [Fact]
    public void GetSoftHyphenCount_Idempotent()
    {
        var doc = FodtDocument.CreateNew();
        int first = doc.GetSoftHyphenCount();
        int second = doc.GetSoftHyphenCount();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetSoftHyphenCount_IsInt()
    {
        var doc = FodtDocument.CreateNew();
        object result = doc.GetSoftHyphenCount();
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
        Assert.True(doc.GetSoftHyphenCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_AfterMixedContent_CountNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Intro");
        doc.AddTable(2, 2);
        doc.AddParagraph("Conclusion");
        Assert.True(doc.GetSoftHyphenCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_MultipleDocuments_AllNonNegative()
    {
        for (int i = 0; i < 3; i++)
        {
            var doc = FodtDocument.CreateNew();
            doc.AddParagraph($"Document {i}");
            Assert.True(doc.GetSoftHyphenCount() >= 0);
        }
    }
}
