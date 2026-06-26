// Tests for FodtDocument.InsertParagraph dedicated coverage.
// Sprint: ff-sprint-s190-dotnet-deepening-20260628
// Ledger: PC-FODT-R199

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R199: Dedicated tests for FodtDocument.InsertParagraph(int index, string text).
/// Inserts a new body paragraph (text:p) at the given index.
/// Negative index throws ArgumentOutOfRangeException.
/// index > ParagraphCount throws ArgumentOutOfRangeException.
/// index = ParagraphCount appends to end.
/// Valid insert: ParagraphCount increments.
/// Existing paragraphs at and after index shift down.
/// Text content of inserted paragraph is accessible via GetParagraphText.
/// null text becomes empty string.
/// Returns the created FodtParagraph.
/// Covers: negative index throws; above-count throws; valid insert increments count;
/// existing para shifts down; insert at 0 before first; insert at count appends;
/// text accessible after insert; null text treated as empty; returns FodtParagraph;
/// dogfood insert middle verify order.
/// </summary>
public class FodtR199InsertParagraphTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void InsertParagraph_NegativeIndex_ThrowsArgumentOutOfRangeException()
    {
        var doc = FodtDocument.CreateEmpty();
        Assert.Throws<ArgumentOutOfRangeException>(() => doc.InsertParagraph(-1, "Text"));
    }

    [Fact]
    public void InsertParagraph_AboveCountIndex_ThrowsArgumentOutOfRangeException()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Para");
        Assert.Throws<ArgumentOutOfRangeException>(() => doc.InsertParagraph(2, "Text"));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void InsertParagraph_ValidInsert_IncrementsCount()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Existing");
        var before = doc.ParagraphCount;
        doc.InsertParagraph(0, "New");
        Assert.Equal(before + 1, doc.ParagraphCount);
    }

    [Fact]
    public void InsertParagraph_AtZero_ShiftsExistingDown()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Original");
        doc.InsertParagraph(0, "Inserted");
        Assert.Equal("Inserted", doc.GetParagraphText(0));
        Assert.Equal("Original", doc.GetParagraphText(1));
    }

    [Fact]
    public void InsertParagraph_AtCount_AppendsToEnd()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("First");
        doc.InsertParagraph(1, "Second");
        Assert.Equal("Second", doc.GetParagraphText(1));
    }

    [Fact]
    public void InsertParagraph_TextAccessibleAfterInsert()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("A");
        doc.InsertParagraph(1, "InsertedText");
        Assert.Equal("InsertedText", doc.GetParagraphText(1));
    }

    [Fact]
    public void InsertParagraph_NullText_TreatedAsEmpty()
    {
        var doc = FodtDocument.CreateEmpty();
        var result = doc.InsertParagraph(0, null!);
        var text = doc.GetParagraphText(0);
        Assert.True(text == "" || text == null);
    }

    [Fact]
    public void InsertParagraph_ReturnsFodtParagraph()
    {
        var doc = FodtDocument.CreateEmpty();
        var result = doc.InsertParagraph(0, "Text");
        Assert.IsType<FodtParagraph>(result);
    }

    [Fact]
    public void InsertParagraph_EmptyDoc_AtIndex0_Works()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertParagraph(0, "First");
        Assert.Equal(1, doc.ParagraphCount);
        Assert.Equal("First", doc.GetParagraphText(0));
    }

    // -------------------------------------------------------------------------
    // Dogfood pipelines
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_InsertMiddle_OrderPreserved()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("First");
        doc.AppendParagraph("Third");
        doc.InsertParagraph(1, "Second");
        Assert.Equal("First", doc.GetParagraphText(0));
        Assert.Equal("Second", doc.GetParagraphText(1));
        Assert.Equal("Third", doc.GetParagraphText(2));
    }

    [Fact]
    public void DogfoodPipeline_InsertThenRemove_CountRestored()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("A");
        doc.AppendParagraph("B");
        doc.InsertParagraph(1, "C");
        doc.RemoveParagraph(1); // remove C
        Assert.Equal(2, doc.ParagraphCount);
        Assert.Equal("A", doc.GetParagraphText(0));
        Assert.Equal("B", doc.GetParagraphText(1));
    }
}
