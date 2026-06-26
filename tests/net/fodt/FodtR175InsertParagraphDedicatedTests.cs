// Tests for FodtDocument.InsertParagraph dedicated coverage.
// Sprint: ff-sprint-s166-dotnet-deepening-20260628
// Ledger: PC-FODT-R175

using System;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R175: Dedicated tests for FodtDocument.InsertParagraph(int index, string text).
/// InsertParagraph inserts a paragraph at the given position (before element at index).
/// Index must be in range [0, ParagraphCount] — equal to count inserts at end.
/// Throws ArgumentOutOfRangeException for negative index or index > ParagraphCount.
/// Returns the created FodtParagraph.
/// Covers: negative index throws ArgumentOutOfRangeException; index beyond count throws;
/// valid insert at 0 no-throw; valid insert at count (append) no-throw;
/// count increases after insert; inserted paragraph text accessible;
/// insert at 0 shifts existing to index 1; insert at end appends;
/// dogfood AppendParagraph->InsertParagraph pipeline; dogfood insert-at-0 places before first.
/// </summary>
public class FodtR175InsertParagraphDedicatedTests
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
    public void InsertParagraph_IndexBeyondCount_ThrowsArgumentOutOfRangeException()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Existing");
        Assert.Throws<ArgumentOutOfRangeException>(() => doc.InsertParagraph(5, "Text"));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void InsertParagraph_AtIndexZero_DoesNotThrow()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertParagraph(0, "First"); // Insert into empty doc at 0
        Assert.Equal(1, doc.ParagraphCount);
    }

    [Fact]
    public void InsertParagraph_AtIndexEqualsCount_AppendsNoThrow()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Existing");
        doc.InsertParagraph(1, "AppendedViInsert"); // 1 == count
        Assert.Equal(2, doc.ParagraphCount);
    }

    [Fact]
    public void InsertParagraph_CountIncreasesAfterInsert()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Original");
        var before = doc.ParagraphCount;
        doc.InsertParagraph(0, "New First");
        Assert.Equal(before + 1, doc.ParagraphCount);
    }

    [Fact]
    public void InsertParagraph_InsertedTextAccessible()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertParagraph(0, "Inserted");
        Assert.Equal("Inserted", doc.GetParagraphText(0));
    }

    [Fact]
    public void InsertParagraph_InsertAtZero_ShiftsExistingToIndexOne()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Was First");
        doc.InsertParagraph(0, "New First");
        Assert.Equal("New First", doc.GetParagraphText(0));
        Assert.Equal("Was First", doc.GetParagraphText(1));
    }

    [Fact]
    public void InsertParagraph_InsertAtEnd_AppendsCorrectly()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("First");
        doc.InsertParagraph(doc.ParagraphCount, "Last");
        Assert.Equal("Last", doc.GetParagraphText(1));
    }

    // -------------------------------------------------------------------------
    // Dogfood pipelines
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_AppendParagraph_InsertAtZero()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Body");
        doc.InsertParagraph(0, "Title");
        Assert.Equal(2, doc.ParagraphCount);
        Assert.Equal("Title", doc.GetParagraphText(0));
        Assert.Equal("Body", doc.GetParagraphText(1));
    }

    [Fact]
    public void DogfoodPipeline_InsertAtZero_PlacesBeforeFirst()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Para 1");
        doc.AppendParagraph("Para 2");
        doc.InsertParagraph(0, "Para 0");
        Assert.Equal("Para 0", doc.GetParagraphText(0));
        Assert.Equal("Para 1", doc.GetParagraphText(1));
        Assert.Equal("Para 2", doc.GetParagraphText(2));
    }
}
