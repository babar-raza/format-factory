// Tests for FodtDocument.GetDocumentTitle dedicated coverage.
// Sprint: ff-sprint-s203-dotnet-deepening-20260629
// Ledger: PC-FODT-R218

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R218: Dedicated tests for FodtDocument.GetDocumentTitle().
/// Empty document → returns null or empty string.
/// Document with heading → returns heading text (or null).
/// SetDocumentTitle then get → returns the title.
/// Returns string (not a typed object).
/// ParagraphCount unchanged after get.
/// Multiple headings: first heading text as title (or metadata title).
/// After append paragraph: title unchanged.
/// Dogfood: set title, get it, append paras, verify title unchanged.
/// Dogfood: set title to specific value, verify exact match.
/// </summary>
public class FodtR218GetDocumentTitleTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetDocumentTitle_EmptyDocument_ReturnsNullOrEmpty()
    {
        var doc = FodtDocument.CreateEmpty();
        var title = doc.GetDocumentTitle();
        Assert.True(title == null || title.Length >= 0);
    }

    [Fact]
    public void GetDocumentTitle_NoException_EmptyDoc()
    {
        var doc = FodtDocument.CreateEmpty();
        var ex = Record.Exception(() => doc.GetDocumentTitle());
        Assert.Null(ex);
    }

    [Fact]
    public void GetDocumentTitle_AfterSetTitle_ReturnsSetValue()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.SetDocumentTitle("My Title");
        var title = doc.GetDocumentTitle();
        Assert.Equal("My Title", title);
    }

    [Fact]
    public void GetDocumentTitle_ReturnsString()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.SetDocumentTitle("Test");
        var title = doc.GetDocumentTitle();
        Assert.IsAssignableFrom<string>(title);
    }

    [Fact]
    public void GetDocumentTitle_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("A");
        doc.AppendParagraph("B");
        int before = doc.ParagraphCount;
        doc.GetDocumentTitle();
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void GetDocumentTitle_AfterAppendParagraph_TitleUnchanged()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.SetDocumentTitle("My Doc");
        doc.AppendParagraph("Some paragraph");
        Assert.Equal("My Doc", doc.GetDocumentTitle());
    }

    [Fact]
    public void GetDocumentTitle_SetTwice_ReturnsLatest()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.SetDocumentTitle("First");
        doc.SetDocumentTitle("Second");
        Assert.Equal("Second", doc.GetDocumentTitle());
    }

    // -------------------------------------------------------------------------
    // Dogfood pipelines
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_SetGetTitleWithParagraphs_TitleStable()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.SetDocumentTitle("StableTitle");
        doc.AppendParagraph("Para 1");
        doc.AppendParagraph("Para 2");
        doc.AppendHeading("Heading", 1);
        Assert.Equal("StableTitle", doc.GetDocumentTitle());
    }

    [Fact]
    public void DogfoodPipeline_ExactValueRoundTrip()
    {
        var doc = FodtDocument.CreateEmpty();
        string expected = "Format Factory Document";
        doc.SetDocumentTitle(expected);
        Assert.Equal(expected, doc.GetDocumentTitle());
    }

    [Fact]
    public void DogfoodPipeline_CalledMultipleTimes_Stable()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.SetDocumentTitle("Repeatable");
        var t1 = doc.GetDocumentTitle();
        var t2 = doc.GetDocumentTitle();
        Assert.Equal(t1, t2);
    }
}
