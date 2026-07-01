// Tests for FodtDocument.GetVariableCount dedicated coverage.
// Sprint: ff-sprint-s493-dotnet-deepening-20260701
// Ledger: PC-FODT-R517

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R517: Dedicated tests for FodtDocument.GetVariableCount().
/// New document returns non-negative count.
/// ParagraphCount unchanged after GetVariableCount.
/// TableCount unchanged after GetVariableCount.
/// Idempotent (called twice same result).
/// Return type is int.
/// Dogfood: after adding paragraphs count non-negative.
/// Dogfood: after mixed content count non-negative.
/// Dogfood: loop over documents all non-negative.
/// </summary>
public class FodtR517GetVariableCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetVariableCount_NewDocument_ReturnsNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        int count = doc.GetVariableCount();
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetVariableCount_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        int before = doc.ParagraphCount;
        _ = doc.GetVariableCount();
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void GetVariableCount_TableCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        int before = doc.TableCount;
        _ = doc.GetVariableCount();
        Assert.Equal(before, doc.TableCount);
    }

    [Fact]
    public void GetVariableCount_Idempotent()
    {
        var doc = FodtDocument.CreateNew();
        int first = doc.GetVariableCount();
        int second = doc.GetVariableCount();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetVariableCount_IsInt()
    {
        var doc = FodtDocument.CreateNew();
        object result = doc.GetVariableCount();
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
        Assert.True(doc.GetVariableCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_AfterMixedContent_CountNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Intro");
        doc.AddTable(2, 2);
        doc.AddParagraph("Conclusion");
        Assert.True(doc.GetVariableCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_MultipleDocuments_AllNonNegative()
    {
        for (int i = 0; i < 3; i++)
        {
            var doc = FodtDocument.CreateNew();
            doc.AddParagraph($"Document {i}");
            Assert.True(doc.GetVariableCount() >= 0);
        }
    }
}
