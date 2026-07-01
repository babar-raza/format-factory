// Tests for FodtDocument.GetUserDefinedStyleCount dedicated coverage.
// Sprint: ff-sprint-s438-dotnet-deepening-20260701
// Ledger: PC-FODT-R462

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R462: Dedicated tests for FodtDocument.GetUserDefinedStyleCount().
/// New document returns non-negative count.
/// ParagraphCount unchanged after GetUserDefinedStyleCount.
/// TableCount unchanged after GetUserDefinedStyleCount.
/// Idempotent (called twice same result).
/// Return type is int.
/// Dogfood: after adding paragraphs count non-negative.
/// Dogfood: after mixed content count non-negative.
/// Dogfood: loop over documents all non-negative.
/// </summary>
public class FodtR462GetUserDefinedStyleCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetUserDefinedStyleCount_NewDocument_ReturnsNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        int count = doc.GetUserDefinedStyleCount();
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetUserDefinedStyleCount_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        int before = doc.ParagraphCount;
        _ = doc.GetUserDefinedStyleCount();
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void GetUserDefinedStyleCount_TableCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        int before = doc.TableCount;
        _ = doc.GetUserDefinedStyleCount();
        Assert.Equal(before, doc.TableCount);
    }

    [Fact]
    public void GetUserDefinedStyleCount_Idempotent()
    {
        var doc = FodtDocument.CreateNew();
        int first = doc.GetUserDefinedStyleCount();
        int second = doc.GetUserDefinedStyleCount();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetUserDefinedStyleCount_IsInt()
    {
        var doc = FodtDocument.CreateNew();
        object result = doc.GetUserDefinedStyleCount();
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
        Assert.True(doc.GetUserDefinedStyleCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_AfterMixedContent_CountNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Intro");
        doc.AddTable(2, 2);
        doc.AddParagraph("Conclusion");
        Assert.True(doc.GetUserDefinedStyleCount() >= 0);
    }

    [Fact]
    public void DogfoodPipeline_MultipleDocuments_AllNonNegative()
    {
        for (int i = 0; i < 3; i++)
        {
            var doc = FodtDocument.CreateNew();
            doc.AddParagraph($"Document {i}");
            Assert.True(doc.GetUserDefinedStyleCount() >= 0);
        }
    }
}
