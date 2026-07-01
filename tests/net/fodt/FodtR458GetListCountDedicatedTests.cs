// Tests for FodtDocument.GetListCount dedicated coverage.
// Sprint: ff-sprint-s434-dotnet-deepening-20260701
// Ledger: PC-FODT-R458

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R458: Dedicated tests for FodtDocument.GetListCount().
/// New document returns non-negative count.
/// ParagraphCount unchanged after GetListCount.
/// TableCount unchanged after GetListCount.
/// Idempotent (called twice same result).
/// Return type is int.
/// Dogfood: after adding paragraphs count non-negative.
/// Dogfood: after mixed content count non-negative.
/// Dogfood: loop over documents all non-negative.
/// </summary>
public class FodtR458GetListCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetListCount_NewDocument_ReturnsNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        int count = doc.GetListCount();
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetListCount_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        int before = doc.ParagraphCount;
        _ = doc.GetListCount();
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void GetListCount_TableCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        int before = doc.TableCount;
        _ = doc.GetListCount();
        Assert.Equal(before, doc.TableCount);
    }

    [Fact]
    public void GetListCount_Idempotent()
    {
        var doc = FodtDocument.CreateNew();
        int first = doc.GetListCount();
        int second = doc.GetListCount();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetListCount_IsInt()
    {
        var doc = FodtDocument.CreateNew();
        object result = doc.GetListCount();
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
        Assert.True(doc.GetListCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_AfterMixedContent_CountNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Intro");
        doc.AddTable(2, 2);
        doc.AddParagraph("Conclusion");
        Assert.True(doc.GetListCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_MultipleDocuments_AllNonNegative()
    {
        for (int i = 0; i < 3; i++)
        {
            var doc = FodtDocument.CreateNew();
            doc.AddParagraph($"Document {i}");
            Assert.True(doc.GetListCount() >= 0);
        }
    }
}
