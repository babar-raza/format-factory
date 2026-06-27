// Tests for FodtDocument.GetDocumentDescription dedicated coverage.
// Sprint: ff-sprint-s364-dotnet-deepening-20260630
// Ledger: PC-FODT-R382

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R382: Dedicated tests for FodtDocument.GetDocumentDescription().
/// Valid document returns non-null.
/// ParagraphCount unchanged after GetDocumentDescription.
/// TableCount unchanged after GetDocumentDescription.
/// SectionCount unchanged after GetDocumentDescription.
/// Idempotent (called twice same result).
/// Returns non-empty string.
/// After SetDocumentDescription returns expected.
/// Dogfood: description "Financial analysis document" non-null.
/// Dogfood: description "Policy and procedures" non-null.
/// </summary>
public class FodtR382GetDocumentDescriptionDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetDocumentDescription_ValidDocument_ReturnsNonNull()
    {
        var doc = FodtDocument.CreateNew();
        string? desc = doc.GetDocumentDescription();
        Assert.NotNull(desc);
    }

    [Fact]
    public void GetDocumentDescription_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Introduction text");
        int before = doc.ParagraphCount;
        _ = doc.GetDocumentDescription();
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void GetDocumentDescription_TableCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(2, 3, "Appendix");
        int before = doc.TableCount;
        _ = doc.GetDocumentDescription();
        Assert.Equal(before, doc.TableCount);
    }

    [Fact]
    public void GetDocumentDescription_SectionCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddSection("Overview");
        int before = doc.SectionCount;
        _ = doc.GetDocumentDescription();
        Assert.Equal(before, doc.SectionCount);
    }

    [Fact]
    public void GetDocumentDescription_Idempotent()
    {
        var doc = FodtDocument.CreateNew();
        string? first = doc.GetDocumentDescription();
        string? second = doc.GetDocumentDescription();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetDocumentDescription_ReturnsNonEmptyString()
    {
        var doc = FodtDocument.CreateNew();
        string? desc = doc.GetDocumentDescription();
        Assert.NotNull(desc);
        Assert.True(desc.Length > 0);
    }

    [Fact]
    public void GetDocumentDescription_AfterSetDocumentDescription_ReturnsExpected()
    {
        var doc = FodtDocument.CreateNew();
        doc.SetDocumentDescription("Internal use only — confidential");
        string? desc = doc.GetDocumentDescription();
        Assert.NotNull(desc);
        Assert.Equal("Internal use only — confidential", desc);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_FinancialAnalysisDescription_ReturnsNonNull()
    {
        var doc = FodtDocument.CreateNew();
        doc.SetDocumentDescription("Financial analysis document");
        doc.AddParagraph("Revenue grew 12% YoY");
        doc.AddTable(3, 4, "FinancialSummary");
        string? desc = doc.GetDocumentDescription();
        Assert.NotNull(desc);
    }

    [Fact]
    public void DogfoodPipeline_PolicyDescription_ReturnsNonNull()
    {
        var doc = FodtDocument.CreateNew();
        doc.SetDocumentDescription("Policy and procedures");
        string? desc = doc.GetDocumentDescription();
        Assert.NotNull(desc);
    }
}
