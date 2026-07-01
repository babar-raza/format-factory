// Tests for FodtDocument.GetColumnCount dedicated coverage.
// Sprint: ff-sprint-s510-dotnet-deepening-20260701
// Ledger: PC-FODT-R534

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R534: Dedicated tests for FodtDocument.GetColumnCount().
/// New document returns non-negative count.
/// ParagraphCount unchanged after GetColumnCount.
/// TableCount unchanged after GetColumnCount.
/// Idempotent (called twice same result).
/// Return type is int.
/// Dogfood: after adding paragraphs count non-negative.
/// Dogfood: after mixed content count non-negative.
/// Dogfood: loop over documents all non-negative.
/// </summary>
public class FodtR534GetColumnCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnCount_NewDocument_ReturnsNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        int count = doc.GetColumnCount();
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetColumnCount_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        int before = doc.ParagraphCount;
        _ = doc.GetColumnCount();
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void GetColumnCount_TableCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        int before = doc.TableCount;
        _ = doc.GetColumnCount();
        Assert.Equal(before, doc.TableCount);
    }

    [Fact]
    public void GetColumnCount_Idempotent()
    {
        var doc = FodtDocument.CreateNew();
        int first = doc.GetColumnCount();
        int second = doc.GetColumnCount();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetColumnCount_IsInt()
    {
        var doc = FodtDocument.CreateNew();
        object result = doc.GetColumnCount();
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
        Assert.True(doc.GetColumnCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_AfterMixedContent_CountNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Intro");
        doc.AddTable(2, 2);
        doc.AddParagraph("Conclusion");
        Assert.True(doc.GetColumnCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_MultipleDocuments_AllNonNegative()
    {
        for (int i = 0; i < 3; i++)
        {
            var doc = FodtDocument.CreateNew();
            doc.AddParagraph($"Document {i}");
            Assert.True(doc.GetColumnCount() >= 0);
        }
    }
}
