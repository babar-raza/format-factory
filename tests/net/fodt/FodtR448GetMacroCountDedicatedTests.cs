// Tests for FodtDocument.GetMacroCount dedicated coverage.
// Sprint: ff-sprint-s424-dotnet-deepening-20260701
// Ledger: PC-FODT-R448

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R448: Dedicated tests for FodtDocument.GetMacroCount().
/// New document returns non-negative count.
/// ParagraphCount unchanged after GetMacroCount.
/// TableCount unchanged after GetMacroCount.
/// Idempotent (called twice same result).
/// Return type is int.
/// Dogfood: after adding paragraphs count non-negative.
/// Dogfood: after mixed content count non-negative.
/// Dogfood: loop over documents all non-negative.
/// </summary>
public class FodtR448GetMacroCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetMacroCount_NewDocument_ReturnsNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        int count = doc.GetMacroCount();
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetMacroCount_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        int before = doc.ParagraphCount;
        _ = doc.GetMacroCount();
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void GetMacroCount_TableCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        int before = doc.TableCount;
        _ = doc.GetMacroCount();
        Assert.Equal(before, doc.TableCount);
    }

    [Fact]
    public void GetMacroCount_Idempotent()
    {
        var doc = FodtDocument.CreateNew();
        int first = doc.GetMacroCount();
        int second = doc.GetMacroCount();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetMacroCount_IsInt()
    {
        var doc = FodtDocument.CreateNew();
        object result = doc.GetMacroCount();
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
        Assert.True(doc.GetMacroCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_AfterMixedContent_CountNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Intro");
        doc.AddTable(2, 2);
        doc.AddParagraph("Conclusion");
        Assert.True(doc.GetMacroCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_MultipleDocuments_AllNonNegative()
    {
        for (int i = 0; i < 3; i++)
        {
            var doc = FodtDocument.CreateNew();
            doc.AddParagraph($"Document {i}");
            Assert.True(doc.GetMacroCount() >= 0);
        }
    }
}
