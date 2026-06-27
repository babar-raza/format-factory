// Tests for FodtDocument.GetDocumentModifiedDate dedicated coverage.
// Sprint: ff-sprint-s368-dotnet-deepening-20260630
// Ledger: PC-FODT-R386

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R386: Dedicated tests for FodtDocument.GetDocumentModifiedDate().
/// Valid document returns non-null.
/// ParagraphCount unchanged after GetDocumentModifiedDate.
/// TableCount unchanged after GetDocumentModifiedDate.
/// SectionCount unchanged after GetDocumentModifiedDate.
/// Idempotent (called twice same result).
/// Returns non-empty string.
/// After SetDocumentModifiedDate returns expected.
/// Dogfood: modified date "2026-07-02" non-null.
/// Dogfood: modified date "2026-01-01" non-null.
/// </summary>
public class FodtR386GetDocumentModifiedDateDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetDocumentModifiedDate_ValidDocument_ReturnsNonNull()
    {
        var doc = FodtDocument.CreateNew();
        string? date = doc.GetDocumentModifiedDate();
        Assert.NotNull(date);
    }

    [Fact]
    public void GetDocumentModifiedDate_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Change log entry");
        int before = doc.ParagraphCount;
        _ = doc.GetDocumentModifiedDate();
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void GetDocumentModifiedDate_TableCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(2, 3, "RevisionHistory");
        int before = doc.TableCount;
        _ = doc.GetDocumentModifiedDate();
        Assert.Equal(before, doc.TableCount);
    }

    [Fact]
    public void GetDocumentModifiedDate_SectionCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddSection("Changelog");
        int before = doc.SectionCount;
        _ = doc.GetDocumentModifiedDate();
        Assert.Equal(before, doc.SectionCount);
    }

    [Fact]
    public void GetDocumentModifiedDate_Idempotent()
    {
        var doc = FodtDocument.CreateNew();
        string? first = doc.GetDocumentModifiedDate();
        string? second = doc.GetDocumentModifiedDate();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetDocumentModifiedDate_ReturnsNonEmptyString()
    {
        var doc = FodtDocument.CreateNew();
        string? date = doc.GetDocumentModifiedDate();
        Assert.NotNull(date);
        Assert.True(date.Length > 0);
    }

    [Fact]
    public void GetDocumentModifiedDate_AfterSetDocumentModifiedDate_ReturnsExpected()
    {
        var doc = FodtDocument.CreateNew();
        doc.SetDocumentModifiedDate("2026-06-30");
        string? date = doc.GetDocumentModifiedDate();
        Assert.NotNull(date);
        Assert.Equal("2026-06-30", date);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_ModifiedDate20260702_ReturnsNonNull()
    {
        var doc = FodtDocument.CreateNew();
        doc.SetDocumentModifiedDate("2026-07-02");
        doc.AddParagraph("Latest revision notes");
        doc.AddTable(3, 3, "RevisionTable");
        string? date = doc.GetDocumentModifiedDate();
        Assert.NotNull(date);
    }

    [Fact]
    public void DogfoodPipeline_ModifiedDate20260101_ReturnsNonNull()
    {
        var doc = FodtDocument.CreateNew();
        doc.SetDocumentModifiedDate("2026-01-01");
        string? date = doc.GetDocumentModifiedDate();
        Assert.NotNull(date);
    }
}
