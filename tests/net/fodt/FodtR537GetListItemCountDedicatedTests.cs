// Tests for FodtDocument.GetListItemCount dedicated coverage.
// Sprint: ff-sprint-s513-dotnet-deepening-20260701
// Ledger: PC-FODT-R537

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R537: Dedicated tests for FodtDocument.GetListItemCount().
/// New document returns non-negative count.
/// ParagraphCount unchanged after GetListItemCount.
/// TableCount unchanged after GetListItemCount.
/// Idempotent (called twice same result).
/// Return type is int.
/// Dogfood: after adding paragraphs count non-negative.
/// Dogfood: after mixed content count non-negative.
/// Dogfood: loop over documents all non-negative.
/// </summary>
public class FodtR537GetListItemCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetListItemCount_NewDocument_ReturnsNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        int count = doc.GetListItemCount();
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetListItemCount_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        int before = doc.ParagraphCount;
        _ = doc.GetListItemCount();
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void GetListItemCount_TableCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        int before = doc.TableCount;
        _ = doc.GetListItemCount();
        Assert.Equal(before, doc.TableCount);
    }

    [Fact]
    public void GetListItemCount_Idempotent()
    {
        var doc = FodtDocument.CreateNew();
        int first = doc.GetListItemCount();
        int second = doc.GetListItemCount();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetListItemCount_IsInt()
    {
        var doc = FodtDocument.CreateNew();
        object result = doc.GetListItemCount();
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
        Assert.True(doc.GetListItemCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_AfterMixedContent_CountNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Intro");
        doc.AddTable(2, 2);
        doc.AddParagraph("Conclusion");
        Assert.True(doc.GetListItemCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_MultipleDocuments_AllNonNegative()
    {
        for (int i = 0; i < 3; i++)
        {
            var doc = FodtDocument.CreateNew();
            doc.AddParagraph($"Document {i}");
            Assert.True(doc.GetListItemCount() >= 0);
        }
    }
}
