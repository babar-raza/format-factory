// Tests for FodtDocument.GetDocumentAuthor dedicated coverage.
// Sprint: ff-sprint-s362-dotnet-deepening-20260630
// Ledger: PC-FODT-R380

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R380: Dedicated tests for FodtDocument.GetDocumentAuthor().
/// Valid document returns non-null.
/// ParagraphCount unchanged after GetDocumentAuthor.
/// TableCount unchanged after GetDocumentAuthor.
/// SectionCount unchanged after GetDocumentAuthor.
/// Idempotent (called twice same result).
/// Returns non-empty string.
/// After SetDocumentAuthor returns expected.
/// Dogfood: author "Jane Doe" non-null.
/// Dogfood: author "Corp Legal Dept" non-null.
/// </summary>
public class FodtR380GetDocumentAuthorDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetDocumentAuthor_ValidDocument_ReturnsNonNull()
    {
        var doc = FodtDocument.CreateNew();
        string? author = doc.GetDocumentAuthor();
        Assert.NotNull(author);
    }

    [Fact]
    public void GetDocumentAuthor_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Body content");
        int before = doc.ParagraphCount;
        _ = doc.GetDocumentAuthor();
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void GetDocumentAuthor_TableCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(2, 3, "DataTable");
        int before = doc.TableCount;
        _ = doc.GetDocumentAuthor();
        Assert.Equal(before, doc.TableCount);
    }

    [Fact]
    public void GetDocumentAuthor_SectionCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddSection("Foreword");
        int before = doc.SectionCount;
        _ = doc.GetDocumentAuthor();
        Assert.Equal(before, doc.SectionCount);
    }

    [Fact]
    public void GetDocumentAuthor_Idempotent()
    {
        var doc = FodtDocument.CreateNew();
        string? first = doc.GetDocumentAuthor();
        string? second = doc.GetDocumentAuthor();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetDocumentAuthor_ReturnsNonEmptyString()
    {
        var doc = FodtDocument.CreateNew();
        string? author = doc.GetDocumentAuthor();
        Assert.NotNull(author);
        Assert.True(author.Length > 0);
    }

    [Fact]
    public void GetDocumentAuthor_AfterSetDocumentAuthor_ReturnsExpected()
    {
        var doc = FodtDocument.CreateNew();
        doc.SetDocumentAuthor("Alice Johnson");
        string? author = doc.GetDocumentAuthor();
        Assert.NotNull(author);
        Assert.Equal("Alice Johnson", author);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_AuthorJaneDoe_ReturnsNonNull()
    {
        var doc = FodtDocument.CreateNew();
        doc.SetDocumentAuthor("Jane Doe");
        doc.AddParagraph("Q3 Financial Analysis");
        doc.AddTable(3, 4, "Revenue");
        string? author = doc.GetDocumentAuthor();
        Assert.NotNull(author);
    }

    [Fact]
    public void DogfoodPipeline_CorporateAuthor_ReturnsNonNull()
    {
        var doc = FodtDocument.CreateNew();
        doc.SetDocumentAuthor("Corp Legal Dept");
        string? author = doc.GetDocumentAuthor();
        Assert.NotNull(author);
    }
}
