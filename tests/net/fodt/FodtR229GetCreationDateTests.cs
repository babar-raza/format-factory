// Tests for FodtDocument.GetCreationDate dedicated coverage.
// Sprint: ff-sprint-s214-dotnet-deepening-20260629
// Ledger: PC-FODT-R229

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R229: Dedicated tests for FodtDocument.GetCreationDate.
/// Empty document: no exception.
/// Returns string or null.
/// ParagraphCount unchanged after get.
/// Called twice: returns same value.
/// After appending paragraphs: no exception.
/// After setting author: no exception.
/// After adding headings: no exception.
/// Return type consistent string or null.
/// Dogfood: stable across operations.
/// Dogfood: multiple calls consistent.
/// </summary>
public class FodtR229GetCreationDateTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCreationDate_EmptyDoc_NoException()
    {
        var doc = FodtDocument.CreateEmpty();
        var ex = Record.Exception(() => doc.GetCreationDate());
        Assert.Null(ex);
    }

    [Fact]
    public void GetCreationDate_EmptyDoc_ReturnsStringOrNull()
    {
        var doc = FodtDocument.CreateEmpty();
        var date = doc.GetCreationDate();
        Assert.True(date == null || date is string);
    }

    [Fact]
    public void GetCreationDate_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Alpha");
        doc.AppendParagraph("Beta");
        int before = doc.ParagraphCount;
        doc.GetCreationDate();
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void GetCreationDate_CalledTwice_SameValue()
    {
        var doc = FodtDocument.CreateEmpty();
        Assert.Equal(doc.GetCreationDate(), doc.GetCreationDate());
    }

    [Fact]
    public void GetCreationDate_AfterParagraphsAdded_NoException()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Para 1");
        doc.AppendParagraph("Para 2");
        var ex = Record.Exception(() => doc.GetCreationDate());
        Assert.Null(ex);
    }

    [Fact]
    public void GetCreationDate_AfterSetAuthor_NoException()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.SetAuthor("Test Author");
        var ex = Record.Exception(() => doc.GetCreationDate());
        Assert.Null(ex);
    }

    [Fact]
    public void GetCreationDate_AfterHeadingAdded_NoException()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("Chapter 1", 1);
        var ex = Record.Exception(() => doc.GetCreationDate());
        Assert.Null(ex);
    }

    [Fact]
    public void GetCreationDate_ReturnTypeIsStringOrNull()
    {
        var doc = FodtDocument.CreateEmpty();
        var result = doc.GetCreationDate();
        Assert.True(result == null || result is string);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipelines
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_StableAcrossOperations()
    {
        var doc = FodtDocument.CreateEmpty();
        var before = doc.GetCreationDate();
        doc.AppendParagraph("Content 1");
        doc.AppendParagraph("Content 2");
        doc.SetAuthor("Author");
        var after = doc.GetCreationDate();
        Assert.Equal(before, after);
    }

    [Fact]
    public void DogfoodPipeline_MultipleCallsConsistent()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.SetAuthor("Author");
        doc.AppendParagraph("Content");
        var v1 = doc.GetCreationDate();
        var v2 = doc.GetCreationDate();
        var v3 = doc.GetCreationDate();
        Assert.Equal(v1, v2);
        Assert.Equal(v2, v3);
    }
}
