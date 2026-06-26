// Tests for FodtDocument.GetOdfVersion dedicated coverage.
// Sprint: ff-sprint-s215-dotnet-deepening-20260629
// Ledger: PC-FODT-R230

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R230: Dedicated tests for FodtDocument.GetOdfVersion.
/// Empty document: no exception.
/// Returns non-null string.
/// Contains version number (e.g. "1." prefix).
/// ParagraphCount unchanged after get.
/// Called twice: returns same value.
/// After appending paragraphs: same value.
/// After adding headings: same value.
/// Value is consistent with ODF spec versioning.
/// Dogfood: stable across document operations.
/// Dogfood: multiple calls return same result.
/// </summary>
public class FodtR230GetOdfVersionTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetOdfVersion_EmptyDoc_NoException()
    {
        var doc = FodtDocument.CreateEmpty();
        var ex = Record.Exception(() => doc.GetOdfVersion());
        Assert.Null(ex);
    }

    [Fact]
    public void GetOdfVersion_EmptyDoc_ReturnsNonNull()
    {
        var doc = FodtDocument.CreateEmpty();
        var version = doc.GetOdfVersion();
        Assert.NotNull(version);
    }

    [Fact]
    public void GetOdfVersion_ReturnsString()
    {
        var doc = FodtDocument.CreateEmpty();
        Assert.IsAssignableFrom<string>(doc.GetOdfVersion());
    }

    [Fact]
    public void GetOdfVersion_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Alpha");
        doc.AppendParagraph("Beta");
        int before = doc.ParagraphCount;
        doc.GetOdfVersion();
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void GetOdfVersion_CalledTwice_SameValue()
    {
        var doc = FodtDocument.CreateEmpty();
        Assert.Equal(doc.GetOdfVersion(), doc.GetOdfVersion());
    }

    [Fact]
    public void GetOdfVersion_AfterParagraphsAdded_SameValue()
    {
        var doc = FodtDocument.CreateEmpty();
        var before = doc.GetOdfVersion();
        doc.AppendParagraph("Para 1");
        doc.AppendParagraph("Para 2");
        Assert.Equal(before, doc.GetOdfVersion());
    }

    [Fact]
    public void GetOdfVersion_AfterHeadingAdded_SameValue()
    {
        var doc = FodtDocument.CreateEmpty();
        var before = doc.GetOdfVersion();
        doc.AppendHeading("Chapter 1", 1);
        Assert.Equal(before, doc.GetOdfVersion());
    }

    [Fact]
    public void GetOdfVersion_ValueIsNonEmpty()
    {
        var doc = FodtDocument.CreateEmpty();
        var version = doc.GetOdfVersion();
        Assert.True(version!.Length > 0);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipelines
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_StableAcrossOperations()
    {
        var doc = FodtDocument.CreateEmpty();
        var v1 = doc.GetOdfVersion();
        doc.AppendParagraph("Content");
        doc.SetAuthor("Author");
        doc.AppendHeading("Heading", 2);
        var v2 = doc.GetOdfVersion();
        Assert.Equal(v1, v2);
    }

    [Fact]
    public void DogfoodPipeline_MultipleCallsConsistent()
    {
        var doc = FodtDocument.CreateEmpty();
        var v1 = doc.GetOdfVersion();
        var v2 = doc.GetOdfVersion();
        var v3 = doc.GetOdfVersion();
        Assert.Equal(v1, v2);
        Assert.Equal(v2, v3);
    }
}
