// Tests for FodtDocument.GetInputFieldCount dedicated coverage.
// Sprint: ff-sprint-s401-dotnet-deepening-20260701
// Ledger: PC-FODT-R425

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R425: Dedicated tests for FodtDocument.GetInputFieldCount().
/// New document returns non-negative count.
/// ParagraphCount unchanged after GetInputFieldCount.
/// TableCount unchanged after GetInputFieldCount.
/// Idempotent (called twice same result).
/// Return type is int.
/// Dogfood: after adding paragraphs count non-negative.
/// Dogfood: after mixed content count non-negative.
/// Dogfood: loop over documents all non-negative.
/// </summary>
public class FodtR425GetInputFieldCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetInputFieldCount_NewDocument_ReturnsNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        int count = doc.GetInputFieldCount();
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetInputFieldCount_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        int before = doc.ParagraphCount;
        _ = doc.GetInputFieldCount();
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void GetInputFieldCount_TableCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        int before = doc.TableCount;
        _ = doc.GetInputFieldCount();
        Assert.Equal(before, doc.TableCount);
    }

    [Fact]
    public void GetInputFieldCount_Idempotent()
    {
        var doc = FodtDocument.CreateNew();
        int first = doc.GetInputFieldCount();
        int second = doc.GetInputFieldCount();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetInputFieldCount_IsInt()
    {
        var doc = FodtDocument.CreateNew();
        object result = doc.GetInputFieldCount();
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
        Assert.True(doc.GetInputFieldCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_AfterMixedContent_CountNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Intro");
        doc.AddTable(2, 2);
        doc.AddParagraph("Conclusion");
        Assert.True(doc.GetInputFieldCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_MultipleDocuments_AllNonNegative()
    {
        for (int i = 0; i < 3; i++)
        {
            var doc = FodtDocument.CreateNew();
            doc.AddParagraph($"Document {i}");
            Assert.True(doc.GetInputFieldCount() >= 0);
        }
    }
}
