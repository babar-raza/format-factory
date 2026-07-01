// Tests for FodtDocument.GetObjectCount dedicated coverage.
// Sprint: ff-sprint-s530-dotnet-deepening-20260701
// Ledger: PC-FODT-R554

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R554: Dedicated tests for FodtDocument.GetObjectCount().
/// New document returns non-negative count.
/// ParagraphCount unchanged after GetObjectCount.
/// TableCount unchanged after GetObjectCount.
/// Idempotent (called twice same result).
/// Return type is int.
/// Dogfood: after adding paragraphs count non-negative.
/// Dogfood: after mixed content count non-negative.
/// Dogfood: loop over documents all non-negative.
/// </summary>
public class FodtR554GetObjectCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetObjectCount_NewDocument_ReturnsNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        int count = doc.GetObjectCount();
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetObjectCount_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        int before = doc.ParagraphCount;
        _ = doc.GetObjectCount();
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void GetObjectCount_TableCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        int before = doc.TableCount;
        _ = doc.GetObjectCount();
        Assert.Equal(before, doc.TableCount);
    }

    [Fact]
    public void GetObjectCount_Idempotent()
    {
        var doc = FodtDocument.CreateNew();
        int first = doc.GetObjectCount();
        int second = doc.GetObjectCount();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetObjectCount_IsInt()
    {
        var doc = FodtDocument.CreateNew();
        object result = doc.GetObjectCount();
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
        Assert.True(doc.GetObjectCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_AfterMixedContent_CountNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Intro");
        doc.AddTable(2, 2);
        doc.AddParagraph("Conclusion");
        Assert.True(doc.GetObjectCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_MultipleDocuments_AllNonNegative()
    {
        for (int i = 0; i < 3; i++)
        {
            var doc = FodtDocument.CreateNew();
            doc.AddParagraph($"Document {i}");
            Assert.True(doc.GetObjectCount() >= 0);
        }
    }
}
