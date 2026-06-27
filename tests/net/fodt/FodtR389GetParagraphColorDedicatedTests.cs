// Tests for FodtDocument.GetParagraphColor dedicated coverage.
// Sprint: ff-sprint-s371-dotnet-deepening-20260630
// Ledger: PC-FODT-R389

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R389: Dedicated tests for FodtDocument.GetParagraphColor().
/// Negative index throws.
/// Out-of-range index throws.
/// Empty document throws.
/// Valid paragraph returns non-null.
/// ParagraphCount unchanged after GetParagraphColor.
/// TableCount unchanged after GetParagraphColor.
/// Idempotent (called twice same result).
/// Dogfood: SetParagraphColor "#0000FF" then GetParagraphColor returns "#0000FF".
/// Dogfood: multiple paragraphs each returns non-null color.
/// </summary>
public class FodtR389GetParagraphColorDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetParagraphColor_NegativeIndex_Throws()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Body text");
        Assert.ThrowsAny<Exception>(() => doc.GetParagraphColor(-1));
    }

    [Fact]
    public void GetParagraphColor_OutOfRangeIndex_Throws()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Body text");
        Assert.ThrowsAny<Exception>(() => doc.GetParagraphColor(99));
    }

    [Fact]
    public void GetParagraphColor_EmptyDocument_Throws()
    {
        var doc = FodtDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetParagraphColor(0));
    }

    [Fact]
    public void GetParagraphColor_ValidParagraph_ReturnsNonNull()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Colored paragraph");
        string? color = doc.GetParagraphColor(0);
        Assert.NotNull(color);
    }

    [Fact]
    public void GetParagraphColor_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Content");
        int before = doc.ParagraphCount;
        _ = doc.GetParagraphColor(0);
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void GetParagraphColor_TableCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Text");
        doc.AddTable(2, 3, "DataTable");
        int before = doc.TableCount;
        _ = doc.GetParagraphColor(0);
        Assert.Equal(before, doc.TableCount);
    }

    [Fact]
    public void GetParagraphColor_Idempotent()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Stable paragraph");
        string? first = doc.GetParagraphColor(0);
        string? second = doc.GetParagraphColor(0);
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_SetColorBlue_ReturnsBlue()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Blue heading");
        doc.SetParagraphColor(0, "#0000FF");
        string? color = doc.GetParagraphColor(0);
        Assert.NotNull(color);
        Assert.Equal("#0000FF", color);
    }

    [Fact]
    public void DogfoodPipeline_MultipleParagraphs_EachNonNull()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("First");
        doc.AddParagraph("Second");
        doc.AddParagraph("Third");
        Assert.NotNull(doc.GetParagraphColor(0));
        Assert.NotNull(doc.GetParagraphColor(1));
        Assert.NotNull(doc.GetParagraphColor(2));
    }
}
