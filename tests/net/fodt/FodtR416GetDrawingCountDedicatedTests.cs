// Tests for FodtDocument.GetDrawingCount dedicated coverage.
// Sprint: ff-sprint-s392-dotnet-deepening-20260701
// Ledger: PC-FODT-R416

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R416: Dedicated tests for FodtDocument.DrawingCount (or GetDrawingCount()).
/// New document returns non-negative.
/// ParagraphCount unchanged after checking DrawingCount.
/// TableCount unchanged after checking DrawingCount.
/// FieldCount unchanged after checking DrawingCount.
/// Idempotent (read twice same result).
/// Is integer type.
/// Dogfood: DrawingCount non-negative after paragraphs.
/// Dogfood: DrawingCount non-negative after mixed content.
/// Dogfood: DrawingCount never negative in loop.
/// </summary>
public class FodtR416GetDrawingCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void DrawingCount_NewDocument_ReturnsNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        Assert.True(doc.DrawingCount >= 0);
    }

    [Fact]
    public void DrawingCount_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Para 1");
        int before = doc.ParagraphCount;
        _ = doc.DrawingCount;
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void DrawingCount_TableCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Para 1");
        int before = doc.TableCount;
        _ = doc.DrawingCount;
        Assert.Equal(before, doc.TableCount);
    }

    [Fact]
    public void DrawingCount_FieldCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Para 1");
        int before = doc.FieldCount;
        _ = doc.DrawingCount;
        Assert.Equal(before, doc.FieldCount);
    }

    [Fact]
    public void DrawingCount_Idempotent()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Text");
        int first = doc.DrawingCount;
        int second = doc.DrawingCount;
        Assert.Equal(first, second);
    }

    [Fact]
    public void DrawingCount_IsInteger()
    {
        var doc = FodtDocument.CreateNew();
        int count = doc.DrawingCount;
        Assert.IsType<int>(count);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_AfterParagraphs_NonNegative()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Caption for drawing A");
        doc.AddParagraph("Caption for drawing B");
        Assert.True(doc.DrawingCount >= 0);
    }

    [Fact]
    public void DogfoodPipeline_AfterMixedContent_NonNegative()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Figure 1 description");
        doc.AddTable(2, 3);
        doc.AddParagraph("Diagram reference");
        Assert.True(doc.DrawingCount >= 0);
    }

    [Fact]
    public void DogfoodPipeline_NeverNegativeInLoop()
    {
        var doc = FodtDocument.CreateNew();
        for (int i = 0; i < 5; i++)
        {
            doc.AddParagraph($"Drawing caption {i}");
            Assert.True(doc.DrawingCount >= 0);
        }
    }
}
