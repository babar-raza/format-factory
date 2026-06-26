// Tests for FodtDocument.DeleteParagraphAt dedicated coverage.
// Sprint: ff-sprint-s226-dotnet-deepening-20260629
// Ledger: PC-FODT-R241

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R241: Dedicated tests for FodtDocument.DeleteParagraphAt(index).
/// Negative index → throws exception.
/// OOB index → throws exception.
/// Valid delete → no exception.
/// ParagraphCount decreases after delete.
/// Delete first: subsequent text shifts down.
/// Delete last: no exception.
/// Delete middle: others preserved.
/// Called on single paragraph: count becomes 0.
/// Dogfood: add then delete multiple, count correct.
/// Dogfood: delete-append round-trip works.
/// </summary>
public class FodtR241DeleteParagraphAtTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void DeleteParagraphAt_NegativeIndex_ThrowsException()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Text");
        Assert.ThrowsAny<Exception>(() => doc.DeleteParagraphAt(-1));
    }

    [Fact]
    public void DeleteParagraphAt_OobIndex_ThrowsException()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Text");
        Assert.ThrowsAny<Exception>(() => doc.DeleteParagraphAt(10));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void DeleteParagraphAt_ValidDelete_NoException()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("To Delete");
        var ex = Record.Exception(() => doc.DeleteParagraphAt(0));
        Assert.Null(ex);
    }

    [Fact]
    public void DeleteParagraphAt_ParagraphCountDecreases()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("One");
        doc.AppendParagraph("Two");
        int before = doc.ParagraphCount;
        doc.DeleteParagraphAt(0);
        Assert.Equal(before - 1, doc.ParagraphCount);
    }

    [Fact]
    public void DeleteParagraphAt_DeleteFirst_ShiftsDown()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("First");
        doc.AppendParagraph("Second");
        doc.DeleteParagraphAt(0);
        Assert.Contains("Second", doc.GetParagraphText(0));
    }

    [Fact]
    public void DeleteParagraphAt_DeleteLast_NoException()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Only");
        doc.AppendParagraph("Last");
        var ex = Record.Exception(() => doc.DeleteParagraphAt(1));
        Assert.Null(ex);
    }

    [Fact]
    public void DeleteParagraphAt_DeleteMiddle_OthersPreserved()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("First");
        doc.AppendParagraph("Middle");
        doc.AppendParagraph("Last");
        doc.DeleteParagraphAt(1);
        Assert.Contains("First", doc.GetParagraphText(0));
        Assert.Contains("Last", doc.GetParagraphText(1));
    }

    [Fact]
    public void DeleteParagraphAt_SingleParagraph_CountBecomesZero()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Only One");
        doc.DeleteParagraphAt(0);
        Assert.Equal(0, doc.ParagraphCount);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipelines
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_AddThenDeleteMultiple_CountCorrect()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("A");
        doc.AppendParagraph("B");
        doc.AppendParagraph("C");
        doc.AppendParagraph("D");
        doc.DeleteParagraphAt(0);
        doc.DeleteParagraphAt(0);
        Assert.Equal(2, doc.ParagraphCount);
    }

    [Fact]
    public void DogfoodPipeline_DeleteAndAppend_WorksCorrectly()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Old");
        doc.DeleteParagraphAt(0);
        doc.AppendParagraph("New");
        Assert.Equal(1, doc.ParagraphCount);
        Assert.Contains("New", doc.GetParagraphText(0));
    }
}
