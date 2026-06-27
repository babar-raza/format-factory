// Tests for FodtDocument.GetDocumentCreationDate dedicated coverage.
// Sprint: ff-sprint-s367-dotnet-deepening-20260630
// Ledger: PC-FODT-R385

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R385: Dedicated tests for FodtDocument.GetDocumentCreationDate().
/// Valid document returns non-null.
/// ParagraphCount unchanged after GetDocumentCreationDate.
/// TableCount unchanged after GetDocumentCreationDate.
/// SectionCount unchanged after GetDocumentCreationDate.
/// Idempotent (called twice same result).
/// Returns non-empty string.
/// After SetDocumentCreationDate returns expected.
/// Dogfood: date "2026-07-01" non-null.
/// Dogfood: date "2025-12-31" non-null.
/// </summary>
public class FodtR385GetDocumentCreationDateDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetDocumentCreationDate_ValidDocument_ReturnsNonNull()
    {
        var doc = FodtDocument.CreateNew();
        string? date = doc.GetDocumentCreationDate();
        Assert.NotNull(date);
    }

    [Fact]
    public void GetDocumentCreationDate_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Report paragraph");
        int before = doc.ParagraphCount;
        _ = doc.GetDocumentCreationDate();
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void GetDocumentCreationDate_TableCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(2, 3, "Timeline");
        int before = doc.TableCount;
        _ = doc.GetDocumentCreationDate();
        Assert.Equal(before, doc.TableCount);
    }

    [Fact]
    public void GetDocumentCreationDate_SectionCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddSection("Background");
        int before = doc.SectionCount;
        _ = doc.GetDocumentCreationDate();
        Assert.Equal(before, doc.SectionCount);
    }

    [Fact]
    public void GetDocumentCreationDate_Idempotent()
    {
        var doc = FodtDocument.CreateNew();
        string? first = doc.GetDocumentCreationDate();
        string? second = doc.GetDocumentCreationDate();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetDocumentCreationDate_ReturnsNonEmptyString()
    {
        var doc = FodtDocument.CreateNew();
        string? date = doc.GetDocumentCreationDate();
        Assert.NotNull(date);
        Assert.True(date.Length > 0);
    }

    [Fact]
    public void GetDocumentCreationDate_AfterSetDocumentCreationDate_ReturnsExpected()
    {
        var doc = FodtDocument.CreateNew();
        doc.SetDocumentCreationDate("2026-01-15");
        string? date = doc.GetDocumentCreationDate();
        Assert.NotNull(date);
        Assert.Equal("2026-01-15", date);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_Date20260701_ReturnsNonNull()
    {
        var doc = FodtDocument.CreateNew();
        doc.SetDocumentCreationDate("2026-07-01");
        doc.AddParagraph("Mid-year review");
        doc.AddTable(3, 4, "Milestones");
        string? date = doc.GetDocumentCreationDate();
        Assert.NotNull(date);
    }

    [Fact]
    public void DogfoodPipeline_Date20251231_ReturnsNonNull()
    {
        var doc = FodtDocument.CreateNew();
        doc.SetDocumentCreationDate("2025-12-31");
        string? date = doc.GetDocumentCreationDate();
        Assert.NotNull(date);
    }
}
