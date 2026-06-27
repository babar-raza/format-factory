// Tests for FodtDocument.GetParagraphFont dedicated coverage.
// Sprint: ff-sprint-s369-dotnet-deepening-20260630
// Ledger: PC-FODT-R387

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R387: Dedicated tests for FodtDocument.GetParagraphFont().
/// Negative index throws.
/// Out-of-range index throws.
/// Empty document throws.
/// Valid paragraph returns non-null.
/// ParagraphCount unchanged after GetParagraphFont.
/// TableCount unchanged after GetParagraphFont.
/// Idempotent (called twice same result).
/// Dogfood: SetParagraphFont "Arial" then GetParagraphFont returns "Arial".
/// Dogfood: multiple paragraphs each returns non-null font.
/// </summary>
public class FodtR387GetParagraphFontDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetParagraphFont_NegativeIndex_Throws()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Body text");
        Assert.ThrowsAny<Exception>(() => doc.GetParagraphFont(-1));
    }

    [Fact]
    public void GetParagraphFont_OutOfRangeIndex_Throws()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Body text");
        Assert.ThrowsAny<Exception>(() => doc.GetParagraphFont(99));
    }

    [Fact]
    public void GetParagraphFont_EmptyDocument_Throws()
    {
        var doc = FodtDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetParagraphFont(0));
    }

    [Fact]
    public void GetParagraphFont_ValidParagraph_ReturnsNonNull()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Introduction");
        string? font = doc.GetParagraphFont(0);
        Assert.NotNull(font);
    }

    [Fact]
    public void GetParagraphFont_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Content");
        int before = doc.ParagraphCount;
        _ = doc.GetParagraphFont(0);
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void GetParagraphFont_TableCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Text");
        doc.AddTable(2, 3, "DataTable");
        int before = doc.TableCount;
        _ = doc.GetParagraphFont(0);
        Assert.Equal(before, doc.TableCount);
    }

    [Fact]
    public void GetParagraphFont_Idempotent()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Stable paragraph");
        string? first = doc.GetParagraphFont(0);
        string? second = doc.GetParagraphFont(0);
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_SetFontArial_ReturnsArial()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Styled paragraph");
        doc.SetParagraphFont(0, "Arial");
        string? font = doc.GetParagraphFont(0);
        Assert.NotNull(font);
        Assert.Equal("Arial", font);
    }

    [Fact]
    public void DogfoodPipeline_MultipleParagraphs_EachNonNull()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("First paragraph");
        doc.AddParagraph("Second paragraph");
        doc.AddParagraph("Third paragraph");
        Assert.NotNull(doc.GetParagraphFont(0));
        Assert.NotNull(doc.GetParagraphFont(1));
        Assert.NotNull(doc.GetParagraphFont(2));
    }
}
