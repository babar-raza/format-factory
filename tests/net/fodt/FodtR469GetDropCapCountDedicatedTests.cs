// Tests for FodtDocument.GetDropCapCount dedicated coverage.
// Sprint: ff-sprint-s445-dotnet-deepening-20260701
// Ledger: PC-FODT-R469

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R469: Dedicated tests for FodtDocument.GetDropCapCount().
/// New document returns non-negative count.
/// ParagraphCount unchanged after GetDropCapCount.
/// TableCount unchanged after GetDropCapCount.
/// Idempotent (called twice same result).
/// Return type is int.
/// Dogfood: after adding paragraphs count non-negative.
/// Dogfood: after mixed content count non-negative.
/// Dogfood: loop over documents all non-negative.
/// </summary>
public class FodtR469GetDropCapCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetDropCapCount_NewDocument_ReturnsNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        int count = doc.GetDropCapCount();
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetDropCapCount_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        int before = doc.ParagraphCount;
        _ = doc.GetDropCapCount();
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void GetDropCapCount_TableCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        int before = doc.TableCount;
        _ = doc.GetDropCapCount();
        Assert.Equal(before, doc.TableCount);
    }

    [Fact]
    public void GetDropCapCount_Idempotent()
    {
        var doc = FodtDocument.CreateNew();
        int first = doc.GetDropCapCount();
        int second = doc.GetDropCapCount();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetDropCapCount_IsInt()
    {
        var doc = FodtDocument.CreateNew();
        object result = doc.GetDropCapCount();
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
        Assert.True(doc.GetDropCapCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_AfterMixedContent_CountNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Intro");
        doc.AddTable(2, 2);
        doc.AddParagraph("Conclusion");
        Assert.True(doc.GetDropCapCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_MultipleDocuments_AllNonNegative()
    {
        for (int i = 0; i < 3; i++)
        {
            var doc = FodtDocument.CreateNew();
            doc.AddParagraph($"Document {i}");
            Assert.True(doc.GetDropCapCount() >= 0);
        }
    }
}
