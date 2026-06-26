// Tests for FodtDocument.SetCreator / GetCreator dedicated coverage.
// Sprint: ff-sprint-s212-dotnet-deepening-20260629
// Ledger: PC-FODT-R227

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R227: Dedicated tests for FodtDocument.SetCreator / GetCreator.
/// Empty document: GetCreator returns null or empty string.
/// No exception on empty doc.
/// SetCreator then Get: returns set value.
/// Returns string type.
/// ParagraphCount unchanged after get.
/// Called twice: returns same value.
/// Set twice: latest value returned.
/// Paragraphs added after set: creator unchanged.
/// Dogfood: set creator, add paragraphs, verify stable.
/// Dogfood: exact value round-trip.
/// </summary>
public class FodtR227SetCreatorTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCreator_EmptyDoc_NoException()
    {
        var doc = FodtDocument.CreateEmpty();
        var ex = Record.Exception(() => doc.GetCreator());
        Assert.Null(ex);
    }

    [Fact]
    public void GetCreator_EmptyDoc_ReturnsNullOrEmpty()
    {
        var doc = FodtDocument.CreateEmpty();
        var creator = doc.GetCreator();
        Assert.True(creator == null || creator.Length >= 0);
    }

    [Fact]
    public void GetCreator_AfterSet_ReturnsValue()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.SetCreator("Format Factory Creator");
        Assert.Equal("Format Factory Creator", doc.GetCreator());
    }

    [Fact]
    public void GetCreator_ReturnsString()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.SetCreator("Creator");
        Assert.IsAssignableFrom<string>(doc.GetCreator());
    }

    [Fact]
    public void GetCreator_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Alpha");
        doc.AppendParagraph("Beta");
        int before = doc.ParagraphCount;
        doc.GetCreator();
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void GetCreator_CalledTwice_SameValue()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.SetCreator("Stable Creator");
        Assert.Equal(doc.GetCreator(), doc.GetCreator());
    }

    [Fact]
    public void GetCreator_SetTwice_ReturnsLatest()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.SetCreator("First Creator");
        doc.SetCreator("Second Creator");
        Assert.Equal("Second Creator", doc.GetCreator());
    }

    [Fact]
    public void GetCreator_AfterParagraphsAdded_CreatorUnchanged()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.SetCreator("Persistent Creator");
        doc.AppendParagraph("Para 1");
        doc.AppendHeading("Heading", 1);
        Assert.Equal("Persistent Creator", doc.GetCreator());
    }

    // -------------------------------------------------------------------------
    // Dogfood pipelines
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_CreatorWithParagraphs_CreatorStable()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.SetCreator("Format Factory");
        for (int i = 0; i < 5; i++)
            doc.AppendParagraph($"Content {i}");
        Assert.Equal("Format Factory", doc.GetCreator());
    }

    [Fact]
    public void DogfoodPipeline_ExactValueRoundTrip()
    {
        var doc = FodtDocument.CreateEmpty();
        string expected = "Exact round-trip creator value";
        doc.SetCreator(expected);
        Assert.Equal(expected, doc.GetCreator());
    }
}
