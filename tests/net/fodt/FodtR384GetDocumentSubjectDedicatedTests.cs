// Tests for FodtDocument.GetDocumentSubject dedicated coverage.
// Sprint: ff-sprint-s366-dotnet-deepening-20260630
// Ledger: PC-FODT-R384

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R384: Dedicated tests for FodtDocument.GetDocumentSubject().
/// Valid document returns non-null.
/// ParagraphCount unchanged after GetDocumentSubject.
/// TableCount unchanged after GetDocumentSubject.
/// SectionCount unchanged after GetDocumentSubject.
/// Idempotent (called twice same result).
/// Returns non-empty string.
/// After SetDocumentSubject returns expected.
/// Dogfood: subject "Quarterly Financial Review" non-null.
/// Dogfood: subject "Human Resources Policy" non-null.
/// </summary>
public class FodtR384GetDocumentSubjectDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetDocumentSubject_ValidDocument_ReturnsNonNull()
    {
        var doc = FodtDocument.CreateNew();
        string? subject = doc.GetDocumentSubject();
        Assert.NotNull(subject);
    }

    [Fact]
    public void GetDocumentSubject_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Body paragraph");
        int before = doc.ParagraphCount;
        _ = doc.GetDocumentSubject();
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void GetDocumentSubject_TableCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(2, 4, "SubjectTable");
        int before = doc.TableCount;
        _ = doc.GetDocumentSubject();
        Assert.Equal(before, doc.TableCount);
    }

    [Fact]
    public void GetDocumentSubject_SectionCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddSection("Part One");
        int before = doc.SectionCount;
        _ = doc.GetDocumentSubject();
        Assert.Equal(before, doc.SectionCount);
    }

    [Fact]
    public void GetDocumentSubject_Idempotent()
    {
        var doc = FodtDocument.CreateNew();
        string? first = doc.GetDocumentSubject();
        string? second = doc.GetDocumentSubject();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetDocumentSubject_ReturnsNonEmptyString()
    {
        var doc = FodtDocument.CreateNew();
        string? subject = doc.GetDocumentSubject();
        Assert.NotNull(subject);
        Assert.True(subject.Length > 0);
    }

    [Fact]
    public void GetDocumentSubject_AfterSetDocumentSubject_ReturnsExpected()
    {
        var doc = FodtDocument.CreateNew();
        doc.SetDocumentSubject("Risk Assessment 2026");
        string? subject = doc.GetDocumentSubject();
        Assert.NotNull(subject);
        Assert.Equal("Risk Assessment 2026", subject);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_QuarterlyFinancialReview_ReturnsNonNull()
    {
        var doc = FodtDocument.CreateNew();
        doc.SetDocumentSubject("Quarterly Financial Review");
        doc.AddParagraph("Net revenue increased 8% in Q3.");
        doc.AddTable(2, 4, "FinancialHighlights");
        string? subject = doc.GetDocumentSubject();
        Assert.NotNull(subject);
    }

    [Fact]
    public void DogfoodPipeline_HRPolicySubject_ReturnsNonNull()
    {
        var doc = FodtDocument.CreateNew();
        doc.SetDocumentSubject("Human Resources Policy");
        string? subject = doc.GetDocumentSubject();
        Assert.NotNull(subject);
    }
}
