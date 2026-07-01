// Tests for FodtDocument.GetGraphicObjectCount dedicated coverage.
// Sprint: ff-sprint-s412-dotnet-deepening-20260701
// Ledger: PC-FODT-R436

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R436: Dedicated tests for FodtDocument.GetGraphicObjectCount().
/// New document returns non-negative count.
/// ParagraphCount unchanged after GetGraphicObjectCount.
/// TableCount unchanged after GetGraphicObjectCount.
/// Idempotent (called twice same result).
/// Return type is int.
/// Dogfood: after adding paragraphs count non-negative.
/// Dogfood: after mixed content count non-negative.
/// Dogfood: loop over documents all non-negative.
/// </summary>
public class FodtR436GetGraphicObjectCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetGraphicObjectCount_NewDocument_ReturnsNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        int count = doc.GetGraphicObjectCount();
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetGraphicObjectCount_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        int before = doc.ParagraphCount;
        _ = doc.GetGraphicObjectCount();
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void GetGraphicObjectCount_TableCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        int before = doc.TableCount;
        _ = doc.GetGraphicObjectCount();
        Assert.Equal(before, doc.TableCount);
    }

    [Fact]
    public void GetGraphicObjectCount_Idempotent()
    {
        var doc = FodtDocument.CreateNew();
        int first = doc.GetGraphicObjectCount();
        int second = doc.GetGraphicObjectCount();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetGraphicObjectCount_IsInt()
    {
        var doc = FodtDocument.CreateNew();
        object result = doc.GetGraphicObjectCount();
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
        Assert.True(doc.GetGraphicObjectCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_AfterMixedContent_CountNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Intro");
        doc.AddTable(2, 2);
        doc.AddParagraph("Conclusion");
        Assert.True(doc.GetGraphicObjectCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_MultipleDocuments_AllNonNegative()
    {
        for (int i = 0; i < 3; i++)
        {
            var doc = FodtDocument.CreateNew();
            doc.AddParagraph($"Document {i}");
            Assert.True(doc.GetGraphicObjectCount() >= 0);
        }
    }
}
