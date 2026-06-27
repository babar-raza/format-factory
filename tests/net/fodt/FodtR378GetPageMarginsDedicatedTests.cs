// Tests for FodtDocument.GetPageMargins dedicated coverage.
// Sprint: ff-sprint-s360-dotnet-deepening-20260630
// Ledger: PC-FODT-R378

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R378: Dedicated tests for FodtDocument.GetPageMargins().
/// Valid document returns non-null.
/// ParagraphCount unchanged after GetPageMargins.
/// TableCount unchanged after GetPageMargins.
/// SectionCount unchanged after GetPageMargins.
/// Idempotent (called twice same result).
/// Returns non-empty string.
/// After SetPageMargins returns expected value.
/// Dogfood: default margins non-null.
/// Dogfood: custom margins non-null.
/// </summary>
public class FodtR378GetPageMarginsDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetPageMargins_ValidDocument_ReturnsNonNull()
    {
        var doc = FodtDocument.CreateNew();
        string? margins = doc.GetPageMargins();
        Assert.NotNull(margins);
    }

    [Fact]
    public void GetPageMargins_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Paragraph content");
        int before = doc.ParagraphCount;
        _ = doc.GetPageMargins();
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void GetPageMargins_TableCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(3, 3, "DataTable");
        int before = doc.TableCount;
        _ = doc.GetPageMargins();
        Assert.Equal(before, doc.TableCount);
    }

    [Fact]
    public void GetPageMargins_SectionCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddSection("Section One");
        int before = doc.SectionCount;
        _ = doc.GetPageMargins();
        Assert.Equal(before, doc.SectionCount);
    }

    [Fact]
    public void GetPageMargins_Idempotent()
    {
        var doc = FodtDocument.CreateNew();
        string? first = doc.GetPageMargins();
        string? second = doc.GetPageMargins();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetPageMargins_ReturnsNonEmptyString()
    {
        var doc = FodtDocument.CreateNew();
        string? margins = doc.GetPageMargins();
        Assert.NotNull(margins);
        Assert.True(margins.Length > 0);
    }

    [Fact]
    public void GetPageMargins_AfterSetPageMargins_ReturnsExpected()
    {
        var doc = FodtDocument.CreateNew();
        doc.SetPageMargins("2cm");
        string? margins = doc.GetPageMargins();
        Assert.NotNull(margins);
        Assert.Equal("2cm", margins);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_DefaultMargins_ReturnsNonNull()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Executive Summary");
        doc.AddTable(2, 3, "KeyMetrics");
        string? margins = doc.GetPageMargins();
        Assert.NotNull(margins);
    }

    [Fact]
    public void DogfoodPipeline_CustomMargins_ReturnsNonNull()
    {
        var doc = FodtDocument.CreateNew();
        doc.SetPageMargins("1.5cm");
        string? margins = doc.GetPageMargins();
        Assert.NotNull(margins);
    }
}
