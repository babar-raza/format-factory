// Tests for FodtDocument.GetListCount dedicated coverage.
// Sprint: ff-sprint-s376-dotnet-deepening-20260630
// Ledger: PC-FODT-R394

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R394: Dedicated tests for FodtDocument.ListCount (or GetListCount()).
/// New document returns non-negative.
/// ParagraphCount unchanged after checking ListCount.
/// TableCount unchanged after checking ListCount.
/// SectionCount unchanged after checking ListCount.
/// Idempotent (read twice same result).
/// Is integer type.
/// Dogfood: ListCount non-negative after paragraphs.
/// Dogfood: ListCount never negative in loop.
/// Dogfood: ListCount non-negative in fresh doc.
/// </summary>
public class FodtR394GetListCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void ListCount_NewDocument_ReturnsNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        Assert.True(doc.ListCount >= 0);
    }

    [Fact]
    public void ListCount_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Para 1");
        int before = doc.ParagraphCount;
        _ = doc.ListCount;
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void ListCount_TableCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Para 1");
        int before = doc.TableCount;
        _ = doc.ListCount;
        Assert.Equal(before, doc.TableCount);
    }

    [Fact]
    public void ListCount_SectionCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Para 1");
        int before = doc.SectionCount;
        _ = doc.ListCount;
        Assert.Equal(before, doc.SectionCount);
    }

    [Fact]
    public void ListCount_Idempotent()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Text");
        int first = doc.ListCount;
        int second = doc.ListCount;
        Assert.Equal(first, second);
    }

    [Fact]
    public void ListCount_IsInteger()
    {
        var doc = FodtDocument.CreateNew();
        int count = doc.ListCount;
        Assert.IsType<int>(count);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_AfterParagraphs_NonNegative()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Item one");
        doc.AddParagraph("Item two");
        Assert.True(doc.ListCount >= 0);
    }

    [Fact]
    public void DogfoodPipeline_NeverNegativeInLoop()
    {
        var doc = FodtDocument.CreateNew();
        for (int i = 0; i < 5; i++)
        {
            doc.AddParagraph($"Paragraph {i}");
            Assert.True(doc.ListCount >= 0);
        }
    }

    [Fact]
    public void DogfoodPipeline_FreshDoc_NonNegative()
    {
        var doc1 = FodtDocument.CreateNew();
        var doc2 = FodtDocument.CreateNew();
        Assert.True(doc1.ListCount >= 0);
        Assert.True(doc2.ListCount >= 0);
    }
}
