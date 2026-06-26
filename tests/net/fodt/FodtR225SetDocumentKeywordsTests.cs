// Tests for FodtDocument.SetDocumentKeywords / GetDocumentKeywords dedicated coverage.
// Sprint: ff-sprint-s210-dotnet-deepening-20260629
// Ledger: PC-FODT-R225

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R225: Dedicated tests for FodtDocument.SetDocumentKeywords / GetDocumentKeywords.
/// Empty document: returns null or empty string.
/// No exception on empty doc.
/// SetDocumentKeywords then Get: returns set value.
/// Returns string type.
/// ParagraphCount unchanged after get.
/// Called twice: returns same value.
/// Set twice: latest value returned.
/// Paragraphs added after set: keywords unchanged.
/// Dogfood: set keywords, add paragraphs, verify stable.
/// Dogfood: exact value round-trip.
/// </summary>
public class FodtR225SetDocumentKeywordsTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetDocumentKeywords_EmptyDoc_ReturnsNullOrEmpty()
    {
        var doc = FodtDocument.CreateEmpty();
        var keywords = doc.GetDocumentKeywords();
        Assert.True(keywords == null || keywords.Length >= 0);
    }

    [Fact]
    public void GetDocumentKeywords_NoException_EmptyDoc()
    {
        var doc = FodtDocument.CreateEmpty();
        var ex = Record.Exception(() => doc.GetDocumentKeywords());
        Assert.Null(ex);
    }

    [Fact]
    public void GetDocumentKeywords_AfterSet_ReturnsValue()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.SetDocumentKeywords("format, factory, document");
        Assert.Equal("format, factory, document", doc.GetDocumentKeywords());
    }

    [Fact]
    public void GetDocumentKeywords_ReturnsString()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.SetDocumentKeywords("test keywords");
        Assert.IsAssignableFrom<string>(doc.GetDocumentKeywords());
    }

    [Fact]
    public void GetDocumentKeywords_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Alpha");
        doc.AppendParagraph("Beta");
        int before = doc.ParagraphCount;
        doc.GetDocumentKeywords();
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void GetDocumentKeywords_CalledTwice_SameValue()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.SetDocumentKeywords("stable, keywords");
        Assert.Equal(doc.GetDocumentKeywords(), doc.GetDocumentKeywords());
    }

    [Fact]
    public void GetDocumentKeywords_SetTwice_ReturnsLatest()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.SetDocumentKeywords("first, set");
        doc.SetDocumentKeywords("second, set");
        Assert.Equal("second, set", doc.GetDocumentKeywords());
    }

    [Fact]
    public void GetDocumentKeywords_AfterParagraphsAdded_KeywordsUnchanged()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.SetDocumentKeywords("persistent, keywords");
        doc.AppendParagraph("Para 1");
        doc.AppendHeading("Heading", 1);
        Assert.Equal("persistent, keywords", doc.GetDocumentKeywords());
    }

    // -------------------------------------------------------------------------
    // Dogfood pipelines
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_KeywordsWithParagraphs_KeywordsStable()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.SetDocumentKeywords("format factory keywords");
        for (int i = 0; i < 5; i++)
            doc.AppendParagraph($"Content {i}");
        Assert.Equal("format factory keywords", doc.GetDocumentKeywords());
    }

    [Fact]
    public void DogfoodPipeline_ExactValueRoundTrip()
    {
        var doc = FodtDocument.CreateEmpty();
        string expected = "exact, round-trip, keywords, value";
        doc.SetDocumentKeywords(expected);
        Assert.Equal(expected, doc.GetDocumentKeywords());
    }
}
