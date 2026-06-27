// Tests for FodtDocument.GetDocumentTitle dedicated coverage.
// Sprint: ff-sprint-s363-dotnet-deepening-20260630
// Ledger: PC-FODT-R381

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R381: Dedicated tests for FodtDocument.GetDocumentTitle().
/// Valid document returns non-null.
/// ParagraphCount unchanged after GetDocumentTitle.
/// TableCount unchanged after GetDocumentTitle.
/// SectionCount unchanged after GetDocumentTitle.
/// Idempotent (called twice same result).
/// Returns non-empty string.
/// After SetDocumentTitle returns expected.
/// Dogfood: title "Q4 Report 2026" non-null.
/// Dogfood: title "Strategy Overview" non-null.
/// </summary>
public class FodtR381GetDocumentTitleDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetDocumentTitle_ValidDocument_ReturnsNonNull()
    {
        var doc = FodtDocument.CreateNew();
        string? title = doc.GetDocumentTitle();
        Assert.NotNull(title);
    }

    [Fact]
    public void GetDocumentTitle_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Introduction paragraph");
        int before = doc.ParagraphCount;
        _ = doc.GetDocumentTitle();
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void GetDocumentTitle_TableCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(3, 4, "Appendix");
        int before = doc.TableCount;
        _ = doc.GetDocumentTitle();
        Assert.Equal(before, doc.TableCount);
    }

    [Fact]
    public void GetDocumentTitle_SectionCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddSection("Abstract");
        int before = doc.SectionCount;
        _ = doc.GetDocumentTitle();
        Assert.Equal(before, doc.SectionCount);
    }

    [Fact]
    public void GetDocumentTitle_Idempotent()
    {
        var doc = FodtDocument.CreateNew();
        string? first = doc.GetDocumentTitle();
        string? second = doc.GetDocumentTitle();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetDocumentTitle_ReturnsNonEmptyString()
    {
        var doc = FodtDocument.CreateNew();
        string? title = doc.GetDocumentTitle();
        Assert.NotNull(title);
        Assert.True(title.Length > 0);
    }

    [Fact]
    public void GetDocumentTitle_AfterSetDocumentTitle_ReturnsExpected()
    {
        var doc = FodtDocument.CreateNew();
        doc.SetDocumentTitle("Annual Performance Review");
        string? title = doc.GetDocumentTitle();
        Assert.NotNull(title);
        Assert.Equal("Annual Performance Review", title);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_Q4ReportTitle_ReturnsNonNull()
    {
        var doc = FodtDocument.CreateNew();
        doc.SetDocumentTitle("Q4 Report 2026");
        doc.AddParagraph("Executive Overview");
        doc.AddTable(2, 5, "KPIs");
        string? title = doc.GetDocumentTitle();
        Assert.NotNull(title);
    }

    [Fact]
    public void DogfoodPipeline_StrategyOverviewTitle_ReturnsNonNull()
    {
        var doc = FodtDocument.CreateNew();
        doc.SetDocumentTitle("Strategy Overview");
        string? title = doc.GetDocumentTitle();
        Assert.NotNull(title);
    }
}
