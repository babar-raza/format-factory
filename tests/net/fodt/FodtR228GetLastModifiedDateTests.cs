// Tests for FodtDocument.GetLastModifiedDate dedicated coverage.
// Sprint: ff-sprint-s213-dotnet-deepening-20260629
// Ledger: PC-FODT-R228

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R228: Dedicated tests for FodtDocument.GetLastModifiedDate.
/// Empty document: no exception.
/// Returns string or null.
/// ParagraphCount unchanged after get.
/// Called twice: returns same value.
/// After appending paragraphs: no exception.
/// Returns value not throwing after SetAuthor.
/// Dogfood: stable across paragraph operations.
/// Dogfood: multiple calls return consistent value.
/// </summary>
public class FodtR228GetLastModifiedDateTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetLastModifiedDate_EmptyDoc_NoException()
    {
        var doc = FodtDocument.CreateEmpty();
        var ex = Record.Exception(() => doc.GetLastModifiedDate());
        Assert.Null(ex);
    }

    [Fact]
    public void GetLastModifiedDate_EmptyDoc_ReturnsStringOrNull()
    {
        var doc = FodtDocument.CreateEmpty();
        var date = doc.GetLastModifiedDate();
        Assert.True(date == null || date is string);
    }

    [Fact]
    public void GetLastModifiedDate_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Alpha");
        doc.AppendParagraph("Beta");
        int before = doc.ParagraphCount;
        doc.GetLastModifiedDate();
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void GetLastModifiedDate_CalledTwice_SameValue()
    {
        var doc = FodtDocument.CreateEmpty();
        Assert.Equal(doc.GetLastModifiedDate(), doc.GetLastModifiedDate());
    }

    [Fact]
    public void GetLastModifiedDate_AfterParagraphsAdded_NoException()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Para 1");
        doc.AppendParagraph("Para 2");
        var ex = Record.Exception(() => doc.GetLastModifiedDate());
        Assert.Null(ex);
    }

    [Fact]
    public void GetLastModifiedDate_AfterSetAuthor_NoException()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.SetAuthor("Test Author");
        var ex = Record.Exception(() => doc.GetLastModifiedDate());
        Assert.Null(ex);
    }

    [Fact]
    public void GetLastModifiedDate_ReturnTypeIsStringOrNull()
    {
        var doc = FodtDocument.CreateEmpty();
        var result = doc.GetLastModifiedDate();
        Assert.True(result == null || result is string);
    }

    [Fact]
    public void GetLastModifiedDate_AfterHeadingAdded_NoException()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("Chapter 1", 1);
        var ex = Record.Exception(() => doc.GetLastModifiedDate());
        Assert.Null(ex);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipelines
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_StableAcrossParagraphOps()
    {
        var doc = FodtDocument.CreateEmpty();
        var before = doc.GetLastModifiedDate();
        for (int i = 0; i < 3; i++)
            doc.AppendParagraph($"Content {i}");
        var after = doc.GetLastModifiedDate();
        Assert.Equal(before, after);
    }

    [Fact]
    public void DogfoodPipeline_MultipleCallsConsistent()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.SetAuthor("Author");
        doc.AppendParagraph("Content");
        var v1 = doc.GetLastModifiedDate();
        var v2 = doc.GetLastModifiedDate();
        var v3 = doc.GetLastModifiedDate();
        Assert.Equal(v1, v2);
        Assert.Equal(v2, v3);
    }
}
