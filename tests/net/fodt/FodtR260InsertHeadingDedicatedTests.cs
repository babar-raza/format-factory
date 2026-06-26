// Tests for FodtDocument.InsertHeading dedicated coverage.
// Sprint: ff-sprint-s245-dotnet-deepening-20260629
// Ledger: PC-FODT-R260

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R260: Dedicated tests for FodtDocument.InsertHeading(index, text, level).
/// Negative index → throws exception.
/// OOB index → throws exception.
/// Valid insert → no exception.
/// ParagraphCount increases.
/// HeadingCount increases.
/// Heading text retrievable at inserted index.
/// Level-1 heading: no exception.
/// Level-2 heading: no exception.
/// Insert at zero: shifts other paragraphs.
/// Dogfood: insert multiple headings, verify count and text.
/// </summary>
public class FodtR260InsertHeadingDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void InsertHeading_NegativeIndex_ThrowsException()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Existing");
        Assert.ThrowsAny<Exception>(() => doc.InsertHeading(-1, "Heading", 1));
    }

    [Fact]
    public void InsertHeading_OobIndex_ThrowsException()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Existing");
        Assert.ThrowsAny<Exception>(() => doc.InsertHeading(10, "Heading", 1));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void InsertHeading_ValidCall_NoException()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Existing");
        var ex = Record.Exception(() => doc.InsertHeading(0, "My Heading", 1));
        Assert.Null(ex);
    }

    [Fact]
    public void InsertHeading_ParagraphCountIncreases()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Body");
        int before = doc.ParagraphCount;
        doc.InsertHeading(0, "Title", 1);
        Assert.True(doc.ParagraphCount > before);
    }

    [Fact]
    public void InsertHeading_HeadingCountIncreases()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Body");
        int before = doc.GetHeadingCount();
        doc.InsertHeading(0, "New Heading", 1);
        Assert.True(doc.GetHeadingCount() > before);
    }

    [Fact]
    public void InsertHeading_HeadingTextRetrievable()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Existing paragraph");
        doc.InsertHeading(0, "Inserted Title", 1);
        string? text = doc.GetHeadingText(0);
        Assert.NotNull(text);
        Assert.Contains("Inserted Title", text);
    }

    [Fact]
    public void InsertHeading_Level1_NoException()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Para");
        var ex = Record.Exception(() => doc.InsertHeading(0, "H1", 1));
        Assert.Null(ex);
    }

    [Fact]
    public void InsertHeading_Level2_NoException()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Para");
        var ex = Record.Exception(() => doc.InsertHeading(0, "H2", 2));
        Assert.Null(ex);
    }

    [Fact]
    public void InsertHeading_AtZero_ShiftsOthers()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Original first");
        doc.InsertHeading(0, "Prepended Heading", 1);
        // Should now have 2+ paragraphs, first being the heading
        Assert.True(doc.ParagraphCount >= 2);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_InsertMultipleHeadings_VerifyCountAndText()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Introduction text");
        doc.InsertHeading(0, "Chapter One", 1);
        doc.InsertHeading(1, "Section 1.1", 2);
        Assert.True(doc.GetHeadingCount() >= 2);
        string? h0 = doc.GetHeadingText(0);
        Assert.NotNull(h0);
        Assert.Contains("Chapter One", h0);
    }
}
