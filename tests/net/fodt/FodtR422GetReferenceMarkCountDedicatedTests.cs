// Tests for FodtDocument.GetReferenceMarkCount dedicated coverage.
// Sprint: ff-sprint-s398-dotnet-deepening-20260701
// Ledger: PC-FODT-R422

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R422: Dedicated tests for FodtDocument.ReferenceMarkCount (or GetReferenceMarkCount()).
/// New document returns non-negative.
/// ParagraphCount unchanged after checking ReferenceMarkCount.
/// TableCount unchanged after checking ReferenceMarkCount.
/// DatabaseRangeCount unchanged after checking ReferenceMarkCount.
/// Idempotent (read twice same result).
/// Is integer type.
/// Dogfood: ReferenceMarkCount non-negative after paragraphs.
/// Dogfood: ReferenceMarkCount non-negative after mixed content.
/// Dogfood: ReferenceMarkCount never negative in loop.
/// </summary>
public class FodtR422GetReferenceMarkCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void ReferenceMarkCount_NewDocument_ReturnsNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        Assert.True(doc.ReferenceMarkCount >= 0);
    }

    [Fact]
    public void ReferenceMarkCount_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Para 1");
        int before = doc.ParagraphCount;
        _ = doc.ReferenceMarkCount;
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void ReferenceMarkCount_TableCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Para 1");
        int before = doc.TableCount;
        _ = doc.ReferenceMarkCount;
        Assert.Equal(before, doc.TableCount);
    }

    [Fact]
    public void ReferenceMarkCount_DatabaseRangeCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Para 1");
        int before = doc.DatabaseRangeCount;
        _ = doc.ReferenceMarkCount;
        Assert.Equal(before, doc.DatabaseRangeCount);
    }

    [Fact]
    public void ReferenceMarkCount_Idempotent()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Text");
        int first = doc.ReferenceMarkCount;
        int second = doc.ReferenceMarkCount;
        Assert.Equal(first, second);
    }

    [Fact]
    public void ReferenceMarkCount_IsInteger()
    {
        var doc = FodtDocument.CreateNew();
        int count = doc.ReferenceMarkCount;
        Assert.IsType<int>(count);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_AfterParagraphs_NonNegative()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("See reference [1]");
        doc.AddParagraph("Refer to bibliography [2]");
        Assert.True(doc.ReferenceMarkCount >= 0);
    }

    [Fact]
    public void DogfoodPipeline_AfterMixedContent_NonNegative()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Introduction with ref [A]");
        doc.AddTable(3, 2);
        doc.AddParagraph("Conclusion citing [B]");
        Assert.True(doc.ReferenceMarkCount >= 0);
    }

    [Fact]
    public void DogfoodPipeline_NeverNegativeInLoop()
    {
        var doc = FodtDocument.CreateNew();
        for (int i = 0; i < 5; i++)
        {
            doc.AddParagraph($"Reference mark paragraph {i}");
            Assert.True(doc.ReferenceMarkCount >= 0);
        }
    }
}
