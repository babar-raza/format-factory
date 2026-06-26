// Tests for FodtDocument.SetParagraphText dedicated coverage.
// Sprint: ff-sprint-s269-dotnet-deepening-20260630
// Ledger: PC-FODT-R284

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R284: Dedicated tests for FodtDocument.SetParagraphText(index, text).
/// Negative index throws exception.
/// Out-of-bounds index throws exception.
/// Valid call no exception.
/// GetParagraphText returns updated text.
/// Set twice second wins.
/// ParagraphCount unchanged after set.
/// TableCount unchanged after set.
/// Dogfood: add paragraph, set new text, retrieve matches.
/// Dogfood: multiple paragraphs, set each, all independent.
/// </summary>
public class FodtR284SetParagraphTextDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void SetParagraphText_NegativeIndex_ThrowsException()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Hello");
        Assert.ThrowsAny<Exception>(() => doc.SetParagraphText(-1, "New text"));
    }

    [Fact]
    public void SetParagraphText_OutOfBoundsIndex_ThrowsException()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Hello");
        int count = doc.ParagraphCount;
        Assert.ThrowsAny<Exception>(() => doc.SetParagraphText(count, "New text"));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void SetParagraphText_ValidIndex_NoException()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Original");
        var ex = Record.Exception(() => doc.SetParagraphText(doc.ParagraphCount - 1, "Updated"));
        Assert.Null(ex);
    }

    [Fact]
    public void SetParagraphText_GetParagraphTextReturnsUpdated()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Original");
        int idx = doc.ParagraphCount - 1;
        doc.SetParagraphText(idx, "Updated text");
        Assert.Equal("Updated text", doc.GetParagraphText(idx));
    }

    [Fact]
    public void SetParagraphText_SetTwice_SecondWins()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Original");
        int idx = doc.ParagraphCount - 1;
        doc.SetParagraphText(idx, "First update");
        doc.SetParagraphText(idx, "Second update");
        Assert.Equal("Second update", doc.GetParagraphText(idx));
    }

    [Fact]
    public void SetParagraphText_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Hello");
        int before = doc.ParagraphCount;
        doc.SetParagraphText(before - 1, "World");
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void SetParagraphText_TableCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Hello");
        int tablesBefore = doc.TableCount;
        doc.SetParagraphText(doc.ParagraphCount - 1, "World");
        Assert.Equal(tablesBefore, doc.TableCount);
    }

    [Fact]
    public void SetParagraphText_EmptyText_NoException()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Hello");
        int idx = doc.ParagraphCount - 1;
        var ex = Record.Exception(() => doc.SetParagraphText(idx, ""));
        Assert.Null(ex);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_AddThenSetText_RetrievesNew()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Draft");
        int idx = doc.ParagraphCount - 1;
        doc.SetParagraphText(idx, "Final");
        Assert.Equal("Final", doc.GetParagraphText(idx));
    }

    [Fact]
    public void DogfoodPipeline_MultipleParagraphs_SetEach_AllIndependent()
    {
        var doc = FodtDocument.CreateNew();
        int start = doc.ParagraphCount;
        doc.AddParagraph("A");
        doc.AddParagraph("B");
        doc.AddParagraph("C");
        doc.SetParagraphText(start, "Alpha");
        doc.SetParagraphText(start + 1, "Beta");
        doc.SetParagraphText(start + 2, "Gamma");
        Assert.Equal("Alpha", doc.GetParagraphText(start));
        Assert.Equal("Beta", doc.GetParagraphText(start + 1));
        Assert.Equal("Gamma", doc.GetParagraphText(start + 2));
    }
}
