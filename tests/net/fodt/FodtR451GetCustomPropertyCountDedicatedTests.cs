// Tests for FodtDocument.GetCustomPropertyCount dedicated coverage.
// Sprint: ff-sprint-s427-dotnet-deepening-20260701
// Ledger: PC-FODT-R451

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R451: Dedicated tests for FodtDocument.GetCustomPropertyCount().
/// New document returns non-negative count.
/// ParagraphCount unchanged after GetCustomPropertyCount.
/// TableCount unchanged after GetCustomPropertyCount.
/// Idempotent (called twice same result).
/// Return type is int.
/// Dogfood: after adding paragraphs count non-negative.
/// Dogfood: after mixed content count non-negative.
/// Dogfood: loop over documents all non-negative.
/// </summary>
public class FodtR451GetCustomPropertyCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCustomPropertyCount_NewDocument_ReturnsNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        int count = doc.GetCustomPropertyCount();
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetCustomPropertyCount_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        int before = doc.ParagraphCount;
        _ = doc.GetCustomPropertyCount();
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void GetCustomPropertyCount_TableCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        int before = doc.TableCount;
        _ = doc.GetCustomPropertyCount();
        Assert.Equal(before, doc.TableCount);
    }

    [Fact]
    public void GetCustomPropertyCount_Idempotent()
    {
        var doc = FodtDocument.CreateNew();
        int first = doc.GetCustomPropertyCount();
        int second = doc.GetCustomPropertyCount();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetCustomPropertyCount_IsInt()
    {
        var doc = FodtDocument.CreateNew();
        object result = doc.GetCustomPropertyCount();
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
        Assert.True(doc.GetCustomPropertyCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_AfterMixedContent_CountNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Intro");
        doc.AddTable(2, 2);
        doc.AddParagraph("Conclusion");
        Assert.True(doc.GetCustomPropertyCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_MultipleDocuments_AllNonNegative()
    {
        for (int i = 0; i < 3; i++)
        {
            var doc = FodtDocument.CreateNew();
            doc.AddParagraph($"Document {i}");
            Assert.True(doc.GetCustomPropertyCount() >= 0);
        }
    }
}
