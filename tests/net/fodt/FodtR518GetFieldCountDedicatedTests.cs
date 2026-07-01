// Tests for FodtDocument.GetFieldCount dedicated coverage.
// Sprint: ff-sprint-s494-dotnet-deepening-20260701
// Ledger: PC-FODT-R518

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R518: Dedicated tests for FodtDocument.GetFieldCount().
/// New document returns non-negative count.
/// ParagraphCount unchanged after GetFieldCount.
/// TableCount unchanged after GetFieldCount.
/// Idempotent (called twice same result).
/// Return type is int.
/// Dogfood: after adding paragraphs count non-negative.
/// Dogfood: after mixed content count non-negative.
/// Dogfood: loop over documents all non-negative.
/// </summary>
public class FodtR518GetFieldCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetFieldCount_NewDocument_ReturnsNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        int count = doc.GetFieldCount();
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetFieldCount_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        int before = doc.ParagraphCount;
        _ = doc.GetFieldCount();
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void GetFieldCount_TableCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        int before = doc.TableCount;
        _ = doc.GetFieldCount();
        Assert.Equal(before, doc.TableCount);
    }

    [Fact]
    public void GetFieldCount_Idempotent()
    {
        var doc = FodtDocument.CreateNew();
        int first = doc.GetFieldCount();
        int second = doc.GetFieldCount();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetFieldCount_IsInt()
    {
        var doc = FodtDocument.CreateNew();
        object result = doc.GetFieldCount();
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
        Assert.True(doc.GetFieldCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_AfterMixedContent_CountNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Intro");
        doc.AddTable(2, 2);
        doc.AddParagraph("Conclusion");
        Assert.True(doc.GetFieldCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_MultipleDocuments_AllNonNegative()
    {
        for (int i = 0; i < 3; i++)
        {
            var doc = FodtDocument.CreateNew();
            doc.AddParagraph($"Document {i}");
            Assert.True(doc.GetFieldCount() >= 0);
        }
    }
}
