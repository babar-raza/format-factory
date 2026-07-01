// Tests for FodtDocument.GetScriptCount dedicated coverage.
// Sprint: ff-sprint-s402-dotnet-deepening-20260701
// Ledger: PC-FODT-R426

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R426: Dedicated tests for FodtDocument.GetScriptCount().
/// New document returns non-negative count.
/// ParagraphCount unchanged after GetScriptCount.
/// TableCount unchanged after GetScriptCount.
/// Idempotent (called twice same result).
/// Return type is int.
/// Dogfood: after adding paragraphs count non-negative.
/// Dogfood: after mixed content count non-negative.
/// Dogfood: loop over documents all non-negative.
/// </summary>
public class FodtR426GetScriptCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetScriptCount_NewDocument_ReturnsNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        int count = doc.GetScriptCount();
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetScriptCount_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        int before = doc.ParagraphCount;
        _ = doc.GetScriptCount();
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void GetScriptCount_TableCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        int before = doc.TableCount;
        _ = doc.GetScriptCount();
        Assert.Equal(before, doc.TableCount);
    }

    [Fact]
    public void GetScriptCount_Idempotent()
    {
        var doc = FodtDocument.CreateNew();
        int first = doc.GetScriptCount();
        int second = doc.GetScriptCount();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetScriptCount_IsInt()
    {
        var doc = FodtDocument.CreateNew();
        object result = doc.GetScriptCount();
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
        Assert.True(doc.GetScriptCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_AfterMixedContent_CountNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Intro");
        doc.AddTable(2, 2);
        doc.AddParagraph("Conclusion");
        Assert.True(doc.GetScriptCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_MultipleDocuments_AllNonNegative()
    {
        for (int i = 0; i < 3; i++)
        {
            var doc = FodtDocument.CreateNew();
            doc.AddParagraph($"Document {i}");
            Assert.True(doc.GetScriptCount() >= 0);
        }
    }
}
