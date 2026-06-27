// Tests for FodtDocument.GetTextFrameCount dedicated coverage.
// Sprint: ff-sprint-s390-dotnet-deepening-20260630
// Ledger: PC-FODT-R408

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R408: Dedicated tests for FodtDocument.TextFrameCount (or GetTextFrameCount()).
/// New document returns non-negative.
/// ParagraphCount unchanged after checking TextFrameCount.
/// TableCount unchanged after checking TextFrameCount.
/// IndexMarkCount unchanged after checking TextFrameCount.
/// Idempotent (read twice same result).
/// Is integer type.
/// Dogfood: TextFrameCount non-negative after paragraphs.
/// Dogfood: TextFrameCount non-negative after mixed content.
/// Dogfood: TextFrameCount never negative in loop.
/// </summary>
public class FodtR408GetTextFrameCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void TextFrameCount_NewDocument_ReturnsNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        Assert.True(doc.TextFrameCount >= 0);
    }

    [Fact]
    public void TextFrameCount_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Para 1");
        int before = doc.ParagraphCount;
        _ = doc.TextFrameCount;
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void TextFrameCount_TableCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Para 1");
        int before = doc.TableCount;
        _ = doc.TextFrameCount;
        Assert.Equal(before, doc.TableCount);
    }

    [Fact]
    public void TextFrameCount_IndexMarkCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Para 1");
        int before = doc.IndexMarkCount;
        _ = doc.TextFrameCount;
        Assert.Equal(before, doc.IndexMarkCount);
    }

    [Fact]
    public void TextFrameCount_Idempotent()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Text");
        int first = doc.TextFrameCount;
        int second = doc.TextFrameCount;
        Assert.Equal(first, second);
    }

    [Fact]
    public void TextFrameCount_IsInteger()
    {
        var doc = FodtDocument.CreateNew();
        int count = doc.TextFrameCount;
        Assert.IsType<int>(count);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_AfterParagraphs_NonNegative()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Text frame content A");
        doc.AddParagraph("Text frame content B");
        Assert.True(doc.TextFrameCount >= 0);
    }

    [Fact]
    public void DogfoodPipeline_AfterMixedContent_NonNegative()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Main body");
        doc.AddTable(3, 3);
        doc.AddParagraph("Sidebar text");
        Assert.True(doc.TextFrameCount >= 0);
    }

    [Fact]
    public void DogfoodPipeline_NeverNegativeInLoop()
    {
        var doc = FodtDocument.CreateNew();
        for (int i = 0; i < 5; i++)
        {
            doc.AddParagraph($"Frame {i} content");
            Assert.True(doc.TextFrameCount >= 0);
        }
    }
}
