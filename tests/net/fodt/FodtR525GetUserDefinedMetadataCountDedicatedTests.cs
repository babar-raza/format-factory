// Tests for FodtDocument.GetUserDefinedMetadataCount dedicated coverage.
// Sprint: ff-sprint-s501-dotnet-deepening-20260701
// Ledger: PC-FODT-R525

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R525: Dedicated tests for FodtDocument.GetUserDefinedMetadataCount().
/// New document returns non-negative count.
/// ParagraphCount unchanged after GetUserDefinedMetadataCount.
/// TableCount unchanged after GetUserDefinedMetadataCount.
/// Idempotent (called twice same result).
/// Return type is int.
/// Dogfood: after adding paragraphs count non-negative.
/// Dogfood: after mixed content count non-negative.
/// Dogfood: loop over documents all non-negative.
/// </summary>
public class FodtR525GetUserDefinedMetadataCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetUserDefinedMetadataCount_NewDocument_ReturnsNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        int count = doc.GetUserDefinedMetadataCount();
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetUserDefinedMetadataCount_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        int before = doc.ParagraphCount;
        _ = doc.GetUserDefinedMetadataCount();
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void GetUserDefinedMetadataCount_TableCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        int before = doc.TableCount;
        _ = doc.GetUserDefinedMetadataCount();
        Assert.Equal(before, doc.TableCount);
    }

    [Fact]
    public void GetUserDefinedMetadataCount_Idempotent()
    {
        var doc = FodtDocument.CreateNew();
        int first = doc.GetUserDefinedMetadataCount();
        int second = doc.GetUserDefinedMetadataCount();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetUserDefinedMetadataCount_IsInt()
    {
        var doc = FodtDocument.CreateNew();
        object result = doc.GetUserDefinedMetadataCount();
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
        Assert.True(doc.GetUserDefinedMetadataCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_AfterMixedContent_CountNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Intro");
        doc.AddTable(2, 2);
        doc.AddParagraph("Conclusion");
        Assert.True(doc.GetUserDefinedMetadataCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_MultipleDocuments_AllNonNegative()
    {
        for (int i = 0; i < 3; i++)
        {
            var doc = FodtDocument.CreateNew();
            doc.AddParagraph($"Document {i}");
            Assert.True(doc.GetUserDefinedMetadataCount() >= 0);
        }
    }
}
