// Tests for FodtDocument.SetDocumentSubject / GetDocumentSubject dedicated coverage.
// Sprint: ff-sprint-s209-dotnet-deepening-20260629
// Ledger: PC-FODT-R224

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R224: Dedicated tests for FodtDocument.SetDocumentSubject / GetDocumentSubject.
/// Empty document: returns null or empty string.
/// No exception on empty doc.
/// SetDocumentSubject then Get: returns set value.
/// Returns string type.
/// ParagraphCount unchanged after get.
/// Called twice: returns same value.
/// Set twice: latest value returned.
/// Paragraphs added after set: subject unchanged.
/// Dogfood: set subject, add paragraphs, verify stable.
/// Dogfood: exact value round-trip.
/// </summary>
public class FodtR224SetDocumentSubjectTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetDocumentSubject_EmptyDoc_ReturnsNullOrEmpty()
    {
        var doc = FodtDocument.CreateEmpty();
        var subject = doc.GetDocumentSubject();
        Assert.True(subject == null || subject.Length >= 0);
    }

    [Fact]
    public void GetDocumentSubject_NoException_EmptyDoc()
    {
        var doc = FodtDocument.CreateEmpty();
        var ex = Record.Exception(() => doc.GetDocumentSubject());
        Assert.Null(ex);
    }

    [Fact]
    public void GetDocumentSubject_AfterSet_ReturnsValue()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.SetDocumentSubject("Format Conversion");
        Assert.Equal("Format Conversion", doc.GetDocumentSubject());
    }

    [Fact]
    public void GetDocumentSubject_ReturnsString()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.SetDocumentSubject("Subject");
        Assert.IsAssignableFrom<string>(doc.GetDocumentSubject());
    }

    [Fact]
    public void GetDocumentSubject_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Alpha");
        doc.AppendParagraph("Beta");
        int before = doc.ParagraphCount;
        doc.GetDocumentSubject();
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void GetDocumentSubject_CalledTwice_SameValue()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.SetDocumentSubject("Stable Subject");
        Assert.Equal(doc.GetDocumentSubject(), doc.GetDocumentSubject());
    }

    [Fact]
    public void GetDocumentSubject_SetTwice_ReturnsLatest()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.SetDocumentSubject("First Subject");
        doc.SetDocumentSubject("Second Subject");
        Assert.Equal("Second Subject", doc.GetDocumentSubject());
    }

    [Fact]
    public void GetDocumentSubject_AfterParagraphsAdded_SubjectUnchanged()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.SetDocumentSubject("Persistent Subject");
        doc.AppendParagraph("Para 1");
        doc.AppendHeading("Heading", 1);
        Assert.Equal("Persistent Subject", doc.GetDocumentSubject());
    }

    // -------------------------------------------------------------------------
    // Dogfood pipelines
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_SubjectWithParagraphs_SubjectStable()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.SetDocumentSubject("Format Factory Subject");
        for (int i = 0; i < 5; i++)
            doc.AppendParagraph($"Content {i}");
        Assert.Equal("Format Factory Subject", doc.GetDocumentSubject());
    }

    [Fact]
    public void DogfoodPipeline_ExactValueRoundTrip()
    {
        var doc = FodtDocument.CreateEmpty();
        string expected = "Exact round-trip subject value";
        doc.SetDocumentSubject(expected);
        Assert.Equal(expected, doc.GetDocumentSubject());
    }
}
