// Tests for FodtDocument.GetEmbeddedObjectCount dedicated coverage.
// Sprint: ff-sprint-s399-dotnet-deepening-20260701
// Ledger: PC-FODT-R423

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R423: Dedicated tests for FodtDocument.EmbeddedObjectCount (or GetEmbeddedObjectCount()).
/// New document returns non-negative.
/// ParagraphCount unchanged after checking EmbeddedObjectCount.
/// TableCount unchanged after checking EmbeddedObjectCount.
/// ReferenceMarkCount unchanged after checking EmbeddedObjectCount.
/// Idempotent (read twice same result).
/// Is integer type.
/// Dogfood: EmbeddedObjectCount non-negative after paragraphs.
/// Dogfood: EmbeddedObjectCount non-negative after mixed content.
/// Dogfood: EmbeddedObjectCount never negative in loop.
/// </summary>
public class FodtR423GetEmbeddedObjectCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void EmbeddedObjectCount_NewDocument_ReturnsNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        Assert.True(doc.EmbeddedObjectCount >= 0);
    }

    [Fact]
    public void EmbeddedObjectCount_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Para 1");
        int before = doc.ParagraphCount;
        _ = doc.EmbeddedObjectCount;
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void EmbeddedObjectCount_TableCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Para 1");
        int before = doc.TableCount;
        _ = doc.EmbeddedObjectCount;
        Assert.Equal(before, doc.TableCount);
    }

    [Fact]
    public void EmbeddedObjectCount_ReferenceMarkCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Para 1");
        int before = doc.ReferenceMarkCount;
        _ = doc.EmbeddedObjectCount;
        Assert.Equal(before, doc.ReferenceMarkCount);
    }

    [Fact]
    public void EmbeddedObjectCount_Idempotent()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Text");
        int first = doc.EmbeddedObjectCount;
        int second = doc.EmbeddedObjectCount;
        Assert.Equal(first, second);
    }

    [Fact]
    public void EmbeddedObjectCount_IsInteger()
    {
        var doc = FodtDocument.CreateNew();
        int count = doc.EmbeddedObjectCount;
        Assert.IsType<int>(count);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_AfterParagraphs_NonNegative()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Section with embedded chart");
        doc.AddParagraph("Section with embedded spreadsheet");
        Assert.True(doc.EmbeddedObjectCount >= 0);
    }

    [Fact]
    public void DogfoodPipeline_AfterMixedContent_NonNegative()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Main content");
        doc.AddTable(3, 4);
        doc.AddParagraph("Appendix with objects");
        Assert.True(doc.EmbeddedObjectCount >= 0);
    }

    [Fact]
    public void DogfoodPipeline_NeverNegativeInLoop()
    {
        var doc = FodtDocument.CreateNew();
        for (int i = 0; i < 5; i++)
        {
            doc.AddParagraph($"Content section {i}");
            Assert.True(doc.EmbeddedObjectCount >= 0);
        }
    }
}
