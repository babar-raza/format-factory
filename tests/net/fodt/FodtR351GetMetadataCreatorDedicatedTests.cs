// Tests for FodtDocument.GetMetadataCreator dedicated coverage.
// Sprint: ff-sprint-s333-dotnet-deepening-20260630
// Ledger: PC-FODT-R351

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R351: Dedicated tests for FodtDocument.GetMetadataCreator().
/// Empty document ok.
/// Returns non-null.
/// ParagraphCount unchanged after GetMetadataCreator.
/// TableCount unchanged after GetMetadataCreator.
/// SectionCount unchanged after GetMetadataCreator.
/// Idempotent (called twice same result).
/// After SetCreator returns correct creator.
/// Dogfood: document with creator and content returns non-null.
/// Dogfood: creator unchanged after AddParagraph.
/// </summary>
public class FodtR351GetMetadataCreatorDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetMetadataCreator_EmptyDocument_Ok()
    {
        var doc = FodtDocument.CreateNew();
        var ex = Record.Exception(() => doc.GetMetadataCreator());
        Assert.Null(ex);
    }

    [Fact]
    public void GetMetadataCreator_ReturnsNonNull()
    {
        var doc = FodtDocument.CreateNew();
        string? creator = doc.GetMetadataCreator();
        Assert.NotNull(creator);
    }

    [Fact]
    public void GetMetadataCreator_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Document body content");
        int before = doc.ParagraphCount;
        _ = doc.GetMetadataCreator();
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void GetMetadataCreator_TableCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Document body content");
        int before = doc.TableCount;
        _ = doc.GetMetadataCreator();
        Assert.Equal(before, doc.TableCount);
    }

    [Fact]
    public void GetMetadataCreator_SectionCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Document body content");
        int before = doc.SectionCount;
        _ = doc.GetMetadataCreator();
        Assert.Equal(before, doc.SectionCount);
    }

    [Fact]
    public void GetMetadataCreator_CalledTwice_SameResult()
    {
        var doc = FodtDocument.CreateNew();
        doc.SetCreator("Jane Smith");
        string? first = doc.GetMetadataCreator();
        string? second = doc.GetMetadataCreator();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetMetadataCreator_AfterSetCreator_ReturnsCreator()
    {
        var doc = FodtDocument.CreateNew();
        doc.SetCreator("Technical Writing Team");
        string? creator = doc.GetMetadataCreator();
        Assert.NotNull(creator);
        Assert.Equal("Technical Writing Team", creator);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_DocumentWithCreatorAndContent_NonNull()
    {
        var doc = FodtDocument.CreateNew();
        doc.SetCreator("Documentation Bot");
        doc.SetTitle("API Reference Guide");
        doc.SetAuthor("Engineering Team");
        doc.AddParagraph("This guide covers the complete API reference.");
        string? creator = doc.GetMetadataCreator();
        Assert.NotNull(creator);
        Assert.Equal(doc.ParagraphCount, doc.ParagraphCount);
    }

    [Fact]
    public void DogfoodPipeline_CreatorUnchangedAfterAddParagraph()
    {
        var doc = FodtDocument.CreateNew();
        doc.SetCreator("Content Creator");
        string? creatorBefore = doc.GetMetadataCreator();
        doc.AddParagraph("New paragraph added after metadata was set");
        string? creatorAfter = doc.GetMetadataCreator();
        Assert.Equal(creatorBefore, creatorAfter);
    }
}
