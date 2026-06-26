// Tests for FodtDocument.AddParagraph dedicated coverage.
// Sprint: ff-sprint-s268-dotnet-deepening-20260630
// Ledger: PC-FODT-R283

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R283: Dedicated tests for FodtDocument.AddParagraph(text).
/// Valid text no exception.
/// Empty string no exception.
/// ParagraphCount increases after AddParagraph.
/// GetParagraphText returns added text.
/// TableCount unchanged after AddParagraph.
/// Called twice ParagraphCount increases by 2.
/// Dogfood: add paragraph, retrieve text matches.
/// Dogfood: add multiple paragraphs, each retrievable.
/// </summary>
public class FodtR283AddParagraphDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard / functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void AddParagraph_ValidText_NoException()
    {
        var doc = FodtDocument.CreateNew();
        var ex = Record.Exception(() => doc.AddParagraph("Hello World"));
        Assert.Null(ex);
    }

    [Fact]
    public void AddParagraph_EmptyString_NoException()
    {
        var doc = FodtDocument.CreateNew();
        var ex = Record.Exception(() => doc.AddParagraph(""));
        Assert.Null(ex);
    }

    [Fact]
    public void AddParagraph_ParagraphCountIncreases()
    {
        var doc = FodtDocument.CreateNew();
        int before = doc.ParagraphCount;
        doc.AddParagraph("New paragraph");
        Assert.True(doc.ParagraphCount > before);
    }

    [Fact]
    public void AddParagraph_GetParagraphTextReturnsAddedText()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Test content");
        int idx = doc.ParagraphCount - 1;
        string text = doc.GetParagraphText(idx);
        Assert.Equal("Test content", text);
    }

    [Fact]
    public void AddParagraph_TableCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        int tablesBefore = doc.TableCount;
        doc.AddParagraph("Some text");
        Assert.Equal(tablesBefore, doc.TableCount);
    }

    [Fact]
    public void AddParagraph_CalledTwice_CountIncreasesByTwo()
    {
        var doc = FodtDocument.CreateNew();
        int before = doc.ParagraphCount;
        doc.AddParagraph("Para 1");
        doc.AddParagraph("Para 2");
        Assert.Equal(before + 2, doc.ParagraphCount);
    }

    [Fact]
    public void AddParagraph_LongText_NoException()
    {
        var doc = FodtDocument.CreateNew();
        string longText = new string('A', 1000);
        var ex = Record.Exception(() => doc.AddParagraph(longText));
        Assert.Null(ex);
    }

    [Fact]
    public void AddParagraph_SpecialCharacters_NoException()
    {
        var doc = FodtDocument.CreateNew();
        var ex = Record.Exception(() => doc.AddParagraph("Hello & <World> \"test\""));
        Assert.Null(ex);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_AddParagraph_RetrievedTextMatches()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("The quick brown fox");
        int idx = doc.ParagraphCount - 1;
        string retrieved = doc.GetParagraphText(idx);
        Assert.Equal("The quick brown fox", retrieved);
    }

    [Fact]
    public void DogfoodPipeline_AddMultipleParagraphs_EachRetrievable()
    {
        var doc = FodtDocument.CreateNew();
        int start = doc.ParagraphCount;
        doc.AddParagraph("First");
        doc.AddParagraph("Second");
        doc.AddParagraph("Third");
        Assert.Equal("First", doc.GetParagraphText(start));
        Assert.Equal("Second", doc.GetParagraphText(start + 1));
        Assert.Equal("Third", doc.GetParagraphText(start + 2));
    }
}
