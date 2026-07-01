// Tests for FodtDocument.GetPageCount dedicated coverage.
// Sprint: ff-sprint-s451-dotnet-deepening-20260701
// Ledger: PC-FODT-R475

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R475: Dedicated tests for FodtDocument.GetPageCount().
/// New document returns positive count (at least 1 page).
/// ParagraphCount unchanged after GetPageCount.
/// TableCount unchanged after GetPageCount.
/// Idempotent (called twice same result).
/// Return type is int.
/// Dogfood: after adding paragraphs count at least 1.
/// Dogfood: after mixed content count at least 1.
/// Dogfood: loop over documents all at least 1.
/// </summary>
public class FodtR475GetPageCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetPageCount_NewDocument_ReturnsAtLeastOne()
    {
        var doc = FodtDocument.CreateNew();
        int count = doc.GetPageCount();
        Assert.True(count >= 1);
    }

    [Fact]
    public void GetPageCount_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        int before = doc.ParagraphCount;
        _ = doc.GetPageCount();
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void GetPageCount_TableCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        int before = doc.TableCount;
        _ = doc.GetPageCount();
        Assert.Equal(before, doc.TableCount);
    }

    [Fact]
    public void GetPageCount_Idempotent()
    {
        var doc = FodtDocument.CreateNew();
        int first = doc.GetPageCount();
        int second = doc.GetPageCount();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetPageCount_IsInt()
    {
        var doc = FodtDocument.CreateNew();
        object result = doc.GetPageCount();
        Assert.IsType<int>(result);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_AfterParagraphs_CountAtLeastOne()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("First paragraph");
        doc.AddParagraph("Second paragraph");
        Assert.True(doc.GetPageCount() >= 1);
    }

    [Fact]
    public void DogfoodPipeline_AfterMixedContent_CountAtLeastOne()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Intro");
        doc.AddTable(2, 2);
        doc.AddParagraph("Conclusion");
        Assert.True(doc.GetPageCount() >= 1);
    }

    [Fact]
    public void DogfoodPipeline_MultipleDocuments_AllAtLeastOne()
    {
        for (int i = 0; i < 3; i++)
        {
            var doc = FodtDocument.CreateNew();
            doc.AddParagraph($"Document {i}");
            Assert.True(doc.GetPageCount() >= 1);
        }
    }
}
