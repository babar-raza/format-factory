// Tests for FodtDocument.InsertParagraphAt dedicated coverage.
// Sprint: ff-sprint-s225-dotnet-deepening-20260629
// Ledger: PC-FODT-R240

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R240: Dedicated tests for FodtDocument.InsertParagraphAt(index, text).
/// Negative index → throws exception.
/// OOB index → throws exception.
/// Valid insert → no exception.
/// ParagraphCount increases after insert.
/// Inserted text retrievable at correct index.
/// Insert at zero shifts others.
/// Insert at end: no exception.
/// Text at other indices preserved.
/// Dogfood: insert at multiple positions, verify order.
/// Dogfood: insert and replace round-trip.
/// </summary>
public class FodtR240InsertParagraphAtTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void InsertParagraphAt_NegativeIndex_ThrowsException()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Existing");
        Assert.ThrowsAny<Exception>(() => doc.InsertParagraphAt(-1, "New"));
    }

    [Fact]
    public void InsertParagraphAt_OobIndex_ThrowsException()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Existing");
        Assert.ThrowsAny<Exception>(() => doc.InsertParagraphAt(10, "New"));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void InsertParagraphAt_ValidInsert_NoException()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Existing");
        var ex = Record.Exception(() => doc.InsertParagraphAt(0, "Inserted"));
        Assert.Null(ex);
    }

    [Fact]
    public void InsertParagraphAt_ParagraphCountIncreases()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("One");
        doc.AppendParagraph("Two");
        int before = doc.ParagraphCount;
        doc.InsertParagraphAt(0, "Inserted");
        Assert.Equal(before + 1, doc.ParagraphCount);
    }

    [Fact]
    public void InsertParagraphAt_InsertedTextRetrievable()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Original");
        doc.InsertParagraphAt(0, "Inserted First");
        var text = doc.GetParagraphText(0);
        Assert.Contains("Inserted First", text);
    }

    [Fact]
    public void InsertParagraphAt_InsertAtEnd_NoException()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Only Paragraph");
        var ex = Record.Exception(() => doc.InsertParagraphAt(1, "At End"));
        Assert.Null(ex);
    }

    [Fact]
    public void InsertParagraphAt_OtherIndicesPreserved()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Keep This");
        doc.InsertParagraphAt(0, "New First");
        // "Keep This" should now be at index 1
        var t1 = doc.GetParagraphText(1);
        Assert.Contains("Keep This", t1);
    }

    [Fact]
    public void InsertParagraphAt_InsertAtZeroShiftsOthers()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Was First");
        doc.InsertParagraphAt(0, "Now First");
        Assert.Contains("Now First", doc.GetParagraphText(0));
        Assert.Contains("Was First", doc.GetParagraphText(1));
    }

    // -------------------------------------------------------------------------
    // Dogfood pipelines
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_InsertMultiple_VerifyOrder()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Base");
        doc.InsertParagraphAt(0, "First");
        doc.InsertParagraphAt(1, "Second");
        Assert.Equal(3, doc.ParagraphCount);
        Assert.Contains("First", doc.GetParagraphText(0));
    }

    [Fact]
    public void DogfoodPipeline_InsertAndReplace_RoundTrip()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Original");
        doc.InsertParagraphAt(0, "Inserted");
        doc.ReplaceParagraphText(0, "Replaced");
        Assert.Contains("Replaced", doc.GetParagraphText(0));
        Assert.Contains("Original", doc.GetParagraphText(1));
    }
}
