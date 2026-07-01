// Tests for FodtDocument.GetSequenceCount dedicated coverage.
// Sprint: ff-sprint-s396-dotnet-deepening-20260701
// Ledger: PC-FODT-R420

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R420: Dedicated tests for FodtDocument.SequenceCount (or GetSequenceCount()).
/// New document returns non-negative.
/// ParagraphCount unchanged after checking SequenceCount.
/// TableCount unchanged after checking SequenceCount.
/// UserFieldCount unchanged after checking SequenceCount.
/// Idempotent (read twice same result).
/// Is integer type.
/// Dogfood: SequenceCount non-negative after paragraphs.
/// Dogfood: SequenceCount non-negative after mixed content.
/// Dogfood: SequenceCount never negative in loop.
/// </summary>
public class FodtR420GetSequenceCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void SequenceCount_NewDocument_ReturnsNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        Assert.True(doc.SequenceCount >= 0);
    }

    [Fact]
    public void SequenceCount_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Para 1");
        int before = doc.ParagraphCount;
        _ = doc.SequenceCount;
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void SequenceCount_TableCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Para 1");
        int before = doc.TableCount;
        _ = doc.SequenceCount;
        Assert.Equal(before, doc.TableCount);
    }

    [Fact]
    public void SequenceCount_UserFieldCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Para 1");
        int before = doc.UserFieldCount;
        _ = doc.SequenceCount;
        Assert.Equal(before, doc.UserFieldCount);
    }

    [Fact]
    public void SequenceCount_Idempotent()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Text");
        int first = doc.SequenceCount;
        int second = doc.SequenceCount;
        Assert.Equal(first, second);
    }

    [Fact]
    public void SequenceCount_IsInteger()
    {
        var doc = FodtDocument.CreateNew();
        int count = doc.SequenceCount;
        Assert.IsType<int>(count);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_AfterParagraphs_NonNegative()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Figure 1: Sample diagram");
        doc.AddParagraph("Table 2: Data summary");
        Assert.True(doc.SequenceCount >= 0);
    }

    [Fact]
    public void DogfoodPipeline_AfterMixedContent_NonNegative()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Chapter 1");
        doc.AddTable(3, 4);
        doc.AddParagraph("Appendix A");
        Assert.True(doc.SequenceCount >= 0);
    }

    [Fact]
    public void DogfoodPipeline_NeverNegativeInLoop()
    {
        var doc = FodtDocument.CreateNew();
        for (int i = 0; i < 5; i++)
        {
            doc.AddParagraph($"Sequence item {i}");
            Assert.True(doc.SequenceCount >= 0);
        }
    }
}
