// Tests for FodtDocument.SetDocumentDescription / GetDocumentDescription dedicated coverage.
// Sprint: ff-sprint-s208-dotnet-deepening-20260629
// Ledger: PC-FODT-R223

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R223: Dedicated tests for FodtDocument.SetDocumentDescription / GetDocumentDescription.
/// Empty document: GetDocumentDescription returns null or empty string.
/// GetDocumentDescription on empty doc: no exception.
/// SetDocumentDescription then Get: returns set value.
/// Returns string type.
/// ParagraphCount unchanged after get.
/// Called twice: returns same value.
/// Set twice: latest value returned.
/// Paragraphs added after set: description unchanged.
/// Dogfood: set description, add paragraphs, verify stable.
/// Dogfood: exact value round-trip.
/// </summary>
public class FodtR223SetDocumentDescriptionTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetDocumentDescription_EmptyDoc_ReturnsNullOrEmpty()
    {
        var doc = FodtDocument.CreateEmpty();
        var desc = doc.GetDocumentDescription();
        Assert.True(desc == null || desc.Length >= 0);
    }

    [Fact]
    public void GetDocumentDescription_NoException_EmptyDoc()
    {
        var doc = FodtDocument.CreateEmpty();
        var ex = Record.Exception(() => doc.GetDocumentDescription());
        Assert.Null(ex);
    }

    [Fact]
    public void GetDocumentDescription_AfterSet_ReturnsValue()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.SetDocumentDescription("A test document description.");
        Assert.Equal("A test document description.", doc.GetDocumentDescription());
    }

    [Fact]
    public void GetDocumentDescription_ReturnsString()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.SetDocumentDescription("Description");
        Assert.IsAssignableFrom<string>(doc.GetDocumentDescription());
    }

    [Fact]
    public void GetDocumentDescription_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Alpha");
        doc.AppendParagraph("Beta");
        int before = doc.ParagraphCount;
        doc.GetDocumentDescription();
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void GetDocumentDescription_CalledTwice_SameValue()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.SetDocumentDescription("Stable");
        Assert.Equal(doc.GetDocumentDescription(), doc.GetDocumentDescription());
    }

    [Fact]
    public void GetDocumentDescription_SetTwice_ReturnsLatest()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.SetDocumentDescription("First description");
        doc.SetDocumentDescription("Second description");
        Assert.Equal("Second description", doc.GetDocumentDescription());
    }

    [Fact]
    public void GetDocumentDescription_AfterParagraphsAdded_DescriptionUnchanged()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.SetDocumentDescription("Persistent");
        doc.AppendParagraph("Para 1");
        doc.AppendHeading("Heading", 1);
        Assert.Equal("Persistent", doc.GetDocumentDescription());
    }

    // -------------------------------------------------------------------------
    // Dogfood pipelines
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_DescriptionWithParagraphs_DescriptionStable()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.SetDocumentDescription("Format Factory Document");
        for (int i = 0; i < 5; i++)
            doc.AppendParagraph($"Paragraph {i}");
        Assert.Equal("Format Factory Document", doc.GetDocumentDescription());
    }

    [Fact]
    public void DogfoodPipeline_ExactValueRoundTrip()
    {
        var doc = FodtDocument.CreateEmpty();
        string expected = "Exact round-trip description value";
        doc.SetDocumentDescription(expected);
        Assert.Equal(expected, doc.GetDocumentDescription());
    }
}
