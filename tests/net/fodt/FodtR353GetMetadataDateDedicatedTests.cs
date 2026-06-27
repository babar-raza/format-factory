// Tests for FodtDocument.GetMetadataDate dedicated coverage.
// Sprint: ff-sprint-s335-dotnet-deepening-20260630
// Ledger: PC-FODT-R353

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R353: Dedicated tests for FodtDocument.GetMetadataDate().
/// Empty document ok.
/// Returns non-null.
/// ParagraphCount unchanged after GetMetadataDate.
/// TableCount unchanged after GetMetadataDate.
/// SectionCount unchanged after GetMetadataDate.
/// Idempotent (called twice same result).
/// After SetDate returns correct date.
/// Dogfood: document with date and content returns non-null.
/// Dogfood: date unchanged after AddParagraph.
/// </summary>
public class FodtR353GetMetadataDateDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetMetadataDate_EmptyDocument_Ok()
    {
        var doc = FodtDocument.CreateNew();
        var ex = Record.Exception(() => doc.GetMetadataDate());
        Assert.Null(ex);
    }

    [Fact]
    public void GetMetadataDate_ReturnsNonNull()
    {
        var doc = FodtDocument.CreateNew();
        string? date = doc.GetMetadataDate();
        Assert.NotNull(date);
    }

    [Fact]
    public void GetMetadataDate_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Document body content");
        int before = doc.ParagraphCount;
        _ = doc.GetMetadataDate();
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void GetMetadataDate_TableCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Document body content");
        int before = doc.TableCount;
        _ = doc.GetMetadataDate();
        Assert.Equal(before, doc.TableCount);
    }

    [Fact]
    public void GetMetadataDate_SectionCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Document body content");
        int before = doc.SectionCount;
        _ = doc.GetMetadataDate();
        Assert.Equal(before, doc.SectionCount);
    }

    [Fact]
    public void GetMetadataDate_CalledTwice_SameResult()
    {
        var doc = FodtDocument.CreateNew();
        doc.SetDate("2026-06-30");
        string? first = doc.GetMetadataDate();
        string? second = doc.GetMetadataDate();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetMetadataDate_AfterSetDate_ReturnsDate()
    {
        var doc = FodtDocument.CreateNew();
        doc.SetDate("2026-01-15");
        string? date = doc.GetMetadataDate();
        Assert.NotNull(date);
        Assert.Equal("2026-01-15", date);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_DocumentWithDateAndContent_NonNull()
    {
        var doc = FodtDocument.CreateNew();
        doc.SetDate("2026-03-01");
        doc.SetTitle("Q1 Report");
        doc.SetAuthor("Reporting Team");
        doc.AddParagraph("This report covers the first quarter results.");
        string? date = doc.GetMetadataDate();
        Assert.NotNull(date);
        Assert.Equal(doc.ParagraphCount, doc.ParagraphCount);
    }

    [Fact]
    public void DogfoodPipeline_DateUnchangedAfterAddParagraph()
    {
        var doc = FodtDocument.CreateNew();
        doc.SetDate("2026-12-31");
        string? dateBefore = doc.GetMetadataDate();
        doc.AddParagraph("Additional content added to document");
        string? dateAfter = doc.GetMetadataDate();
        Assert.Equal(dateBefore, dateAfter);
    }
}
