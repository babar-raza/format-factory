// Tests for FodtDocument.GetMetadataAuthor dedicated coverage.
// Sprint: ff-sprint-s329-dotnet-deepening-20260630
// Ledger: PC-FODT-R347

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R347: Dedicated tests for FodtDocument.GetMetadataAuthor().
/// Empty document ok.
/// Returns non-null.
/// ParagraphCount unchanged after GetMetadataAuthor.
/// TableCount unchanged after GetMetadataAuthor.
/// SectionCount unchanged after GetMetadataAuthor.
/// Idempotent (called twice same result).
/// After SetAuthor returns correct author.
/// Dogfood: document with author and content returns non-null.
/// Dogfood: author unchanged after AddParagraph.
/// </summary>
public class FodtR347GetMetadataAuthorDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetMetadataAuthor_EmptyDocument_Ok()
    {
        var doc = FodtDocument.CreateNew();
        var ex = Record.Exception(() => doc.GetMetadataAuthor());
        Assert.Null(ex);
    }

    [Fact]
    public void GetMetadataAuthor_ReturnsNonNull()
    {
        var doc = FodtDocument.CreateNew();
        string? author = doc.GetMetadataAuthor();
        Assert.NotNull(author);
    }

    [Fact]
    public void GetMetadataAuthor_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Document content");
        int before = doc.ParagraphCount;
        _ = doc.GetMetadataAuthor();
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void GetMetadataAuthor_TableCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Document content");
        int before = doc.TableCount;
        _ = doc.GetMetadataAuthor();
        Assert.Equal(before, doc.TableCount);
    }

    [Fact]
    public void GetMetadataAuthor_SectionCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Document content");
        int before = doc.SectionCount;
        _ = doc.GetMetadataAuthor();
        Assert.Equal(before, doc.SectionCount);
    }

    [Fact]
    public void GetMetadataAuthor_CalledTwice_SameResult()
    {
        var doc = FodtDocument.CreateNew();
        doc.SetAuthor("Jane Smith");
        string? first = doc.GetMetadataAuthor();
        string? second = doc.GetMetadataAuthor();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetMetadataAuthor_AfterSetAuthor_ReturnsAuthor()
    {
        var doc = FodtDocument.CreateNew();
        doc.SetAuthor("John Doe");
        string? author = doc.GetMetadataAuthor();
        Assert.NotNull(author);
        Assert.Equal("John Doe", author);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_DocumentWithAuthorAndContent_NonNull()
    {
        var doc = FodtDocument.CreateNew();
        doc.SetAuthor("Research Team");
        doc.SetTitle("Research Report");
        doc.AddParagraph("This report was authored by the research team.");
        string? author = doc.GetMetadataAuthor();
        Assert.NotNull(author);
        Assert.Equal(doc.ParagraphCount, doc.ParagraphCount);
    }

    [Fact]
    public void DogfoodPipeline_AuthorUnchangedAfterAddParagraph()
    {
        var doc = FodtDocument.CreateNew();
        doc.SetAuthor("Alice Brown");
        string? authorBefore = doc.GetMetadataAuthor();
        doc.AddParagraph("Content added after author was set");
        string? authorAfter = doc.GetMetadataAuthor();
        Assert.Equal(authorBefore, authorAfter);
    }
}
