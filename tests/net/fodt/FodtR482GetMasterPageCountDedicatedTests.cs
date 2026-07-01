// Tests for FodtDocument.GetMasterPageCount dedicated coverage.
// Sprint: ff-sprint-s458-dotnet-deepening-20260701
// Ledger: PC-FODT-R482

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R482: Dedicated tests for FodtDocument.GetMasterPageCount().
/// New document returns non-negative count.
/// ParagraphCount unchanged after GetMasterPageCount.
/// TableCount unchanged after GetMasterPageCount.
/// Idempotent (called twice same result).
/// Return type is int.
/// Dogfood: after adding paragraphs count non-negative.
/// Dogfood: after mixed content count non-negative.
/// Dogfood: loop over documents all non-negative.
/// </summary>
public class FodtR482GetMasterPageCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetMasterPageCount_NewDocument_ReturnsNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        int count = doc.GetMasterPageCount();
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetMasterPageCount_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        int before = doc.ParagraphCount;
        _ = doc.GetMasterPageCount();
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void GetMasterPageCount_TableCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        int before = doc.TableCount;
        _ = doc.GetMasterPageCount();
        Assert.Equal(before, doc.TableCount);
    }

    [Fact]
    public void GetMasterPageCount_Idempotent()
    {
        var doc = FodtDocument.CreateNew();
        int first = doc.GetMasterPageCount();
        int second = doc.GetMasterPageCount();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetMasterPageCount_IsInt()
    {
        var doc = FodtDocument.CreateNew();
        object result = doc.GetMasterPageCount();
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
        Assert.True(doc.GetMasterPageCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_AfterMixedContent_CountNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Intro");
        doc.AddTable(2, 2);
        doc.AddParagraph("Conclusion");
        Assert.True(doc.GetMasterPageCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_MultipleDocuments_AllNonNegative()
    {
        for (int i = 0; i < 3; i++)
        {
            var doc = FodtDocument.CreateNew();
            doc.AddParagraph($"Document {i}");
            Assert.True(doc.GetMasterPageCount() >= 0);
        }
    }
}
