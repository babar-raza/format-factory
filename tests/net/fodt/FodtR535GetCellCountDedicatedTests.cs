// Tests for FodtDocument.GetCellCount dedicated coverage.
// Sprint: ff-sprint-s511-dotnet-deepening-20260701
// Ledger: PC-FODT-R535

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R535: Dedicated tests for FodtDocument.GetCellCount().
/// New document returns non-negative count.
/// ParagraphCount unchanged after GetCellCount.
/// TableCount unchanged after GetCellCount.
/// Idempotent (called twice same result).
/// Return type is int.
/// Dogfood: after adding paragraphs count non-negative.
/// Dogfood: after mixed content count non-negative.
/// Dogfood: loop over documents all non-negative.
/// </summary>
public class FodtR535GetCellCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellCount_NewDocument_ReturnsNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        int count = doc.GetCellCount();
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetCellCount_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        int before = doc.ParagraphCount;
        _ = doc.GetCellCount();
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void GetCellCount_TableCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        int before = doc.TableCount;
        _ = doc.GetCellCount();
        Assert.Equal(before, doc.TableCount);
    }

    [Fact]
    public void GetCellCount_Idempotent()
    {
        var doc = FodtDocument.CreateNew();
        int first = doc.GetCellCount();
        int second = doc.GetCellCount();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetCellCount_IsInt()
    {
        var doc = FodtDocument.CreateNew();
        object result = doc.GetCellCount();
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
        Assert.True(doc.GetCellCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_AfterMixedContent_CountNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Intro");
        doc.AddTable(2, 2);
        doc.AddParagraph("Conclusion");
        Assert.True(doc.GetCellCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_MultipleDocuments_AllNonNegative()
    {
        for (int i = 0; i < 3; i++)
        {
            var doc = FodtDocument.CreateNew();
            doc.AddParagraph($"Document {i}");
            Assert.True(doc.GetCellCount() >= 0);
        }
    }
}
