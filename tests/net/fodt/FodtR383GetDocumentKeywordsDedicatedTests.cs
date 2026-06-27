// Tests for FodtDocument.GetDocumentKeywords dedicated coverage.
// Sprint: ff-sprint-s365-dotnet-deepening-20260630
// Ledger: PC-FODT-R383

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R383: Dedicated tests for FodtDocument.GetDocumentKeywords().
/// Valid document returns non-null.
/// ParagraphCount unchanged after GetDocumentKeywords.
/// TableCount unchanged after GetDocumentKeywords.
/// SectionCount unchanged after GetDocumentKeywords.
/// Idempotent (called twice same result).
/// Returns non-empty string.
/// After SetDocumentKeywords returns expected.
/// Dogfood: keywords "finance, quarterly, report" non-null.
/// Dogfood: keywords "legal, compliance, audit" non-null.
/// </summary>
public class FodtR383GetDocumentKeywordsDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetDocumentKeywords_ValidDocument_ReturnsNonNull()
    {
        var doc = FodtDocument.CreateNew();
        string? kw = doc.GetDocumentKeywords();
        Assert.NotNull(kw);
    }

    [Fact]
    public void GetDocumentKeywords_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Content paragraph");
        int before = doc.ParagraphCount;
        _ = doc.GetDocumentKeywords();
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void GetDocumentKeywords_TableCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(2, 3, "KeyTable");
        int before = doc.TableCount;
        _ = doc.GetDocumentKeywords();
        Assert.Equal(before, doc.TableCount);
    }

    [Fact]
    public void GetDocumentKeywords_SectionCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddSection("Introduction");
        int before = doc.SectionCount;
        _ = doc.GetDocumentKeywords();
        Assert.Equal(before, doc.SectionCount);
    }

    [Fact]
    public void GetDocumentKeywords_Idempotent()
    {
        var doc = FodtDocument.CreateNew();
        string? first = doc.GetDocumentKeywords();
        string? second = doc.GetDocumentKeywords();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetDocumentKeywords_ReturnsNonEmptyString()
    {
        var doc = FodtDocument.CreateNew();
        string? kw = doc.GetDocumentKeywords();
        Assert.NotNull(kw);
        Assert.True(kw.Length > 0);
    }

    [Fact]
    public void GetDocumentKeywords_AfterSetDocumentKeywords_ReturnsExpected()
    {
        var doc = FodtDocument.CreateNew();
        doc.SetDocumentKeywords("budget, forecast, 2027");
        string? kw = doc.GetDocumentKeywords();
        Assert.NotNull(kw);
        Assert.Equal("budget, forecast, 2027", kw);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_FinanceKeywords_ReturnsNonNull()
    {
        var doc = FodtDocument.CreateNew();
        doc.SetDocumentKeywords("finance, quarterly, report");
        doc.AddParagraph("Financial performance summary");
        doc.AddTable(3, 5, "Revenue");
        string? kw = doc.GetDocumentKeywords();
        Assert.NotNull(kw);
    }

    [Fact]
    public void DogfoodPipeline_LegalKeywords_ReturnsNonNull()
    {
        var doc = FodtDocument.CreateNew();
        doc.SetDocumentKeywords("legal, compliance, audit");
        string? kw = doc.GetDocumentKeywords();
        Assert.NotNull(kw);
    }
}
