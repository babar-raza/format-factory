// Tests for FodtDocument.GetNumberingRuleCount dedicated coverage.
// Sprint: ff-sprint-s411-dotnet-deepening-20260701
// Ledger: PC-FODT-R435

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R435: Dedicated tests for FodtDocument.GetNumberingRuleCount().
/// New document returns non-negative count.
/// ParagraphCount unchanged after GetNumberingRuleCount.
/// TableCount unchanged after GetNumberingRuleCount.
/// Idempotent (called twice same result).
/// Return type is int.
/// Dogfood: after adding paragraphs count non-negative.
/// Dogfood: after mixed content count non-negative.
/// Dogfood: loop over documents all non-negative.
/// </summary>
public class FodtR435GetNumberingRuleCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetNumberingRuleCount_NewDocument_ReturnsNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        int count = doc.GetNumberingRuleCount();
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetNumberingRuleCount_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        int before = doc.ParagraphCount;
        _ = doc.GetNumberingRuleCount();
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void GetNumberingRuleCount_TableCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        int before = doc.TableCount;
        _ = doc.GetNumberingRuleCount();
        Assert.Equal(before, doc.TableCount);
    }

    [Fact]
    public void GetNumberingRuleCount_Idempotent()
    {
        var doc = FodtDocument.CreateNew();
        int first = doc.GetNumberingRuleCount();
        int second = doc.GetNumberingRuleCount();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetNumberingRuleCount_IsInt()
    {
        var doc = FodtDocument.CreateNew();
        object result = doc.GetNumberingRuleCount();
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
        Assert.True(doc.GetNumberingRuleCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_AfterMixedContent_CountNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Intro");
        doc.AddTable(2, 2);
        doc.AddParagraph("Conclusion");
        Assert.True(doc.GetNumberingRuleCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_MultipleDocuments_AllNonNegative()
    {
        for (int i = 0; i < 3; i++)
        {
            var doc = FodtDocument.CreateNew();
            doc.AddParagraph($"Document {i}");
            Assert.True(doc.GetNumberingRuleCount() >= 0);
        }
    }
}
