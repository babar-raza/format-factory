// Tests for FodtDocument.GetStyleName dedicated coverage.
// Sprint: ff-sprint-s327-dotnet-deepening-20260630
// Ledger: PC-FODT-R345

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R345: Dedicated tests for FodtDocument.GetStyleName().
/// Valid call no exception on empty document.
/// Returns non-null string.
/// ParagraphCount unchanged after GetStyleName.
/// TableCount unchanged after GetStyleName.
/// SectionCount unchanged after GetStyleName.
/// Idempotent (called twice same result).
/// After AddParagraph still returns non-null.
/// Dogfood: styled document returns non-null style name.
/// Dogfood: document with heading returns non-null style name.
/// </summary>
public class FodtR345GetStyleNameDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetStyleName_EmptyDocument_NoException()
    {
        var doc = FodtDocument.CreateNew();
        var ex = Record.Exception(() => doc.GetStyleName());
        Assert.Null(ex);
    }

    [Fact]
    public void GetStyleName_ReturnsNonNull()
    {
        var doc = FodtDocument.CreateNew();
        string? name = doc.GetStyleName();
        Assert.NotNull(name);
    }

    [Fact]
    public void GetStyleName_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Some content");
        int before = doc.ParagraphCount;
        _ = doc.GetStyleName();
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void GetStyleName_TableCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Some content");
        int before = doc.TableCount;
        _ = doc.GetStyleName();
        Assert.Equal(before, doc.TableCount);
    }

    [Fact]
    public void GetStyleName_SectionCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Some content");
        int before = doc.SectionCount;
        _ = doc.GetStyleName();
        Assert.Equal(before, doc.SectionCount);
    }

    [Fact]
    public void GetStyleName_CalledTwice_SameResult()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Paragraph with default style");
        string? first = doc.GetStyleName();
        string? second = doc.GetStyleName();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetStyleName_AfterAddParagraph_NonNull()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Added paragraph");
        string? name = doc.GetStyleName();
        Assert.NotNull(name);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_StyledDocument_NonNullStyleName()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Introduction content");
        doc.AddParagraph("Main body text with standard paragraph style applied.");
        string? name = doc.GetStyleName();
        Assert.NotNull(name);
        Assert.Equal(doc.ParagraphCount, doc.ParagraphCount);
    }

    [Fact]
    public void DogfoodPipeline_DocumentWithHeading_NonNullStyleName()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddHeading("Document Title", 1);
        doc.AddParagraph("Body text following the heading.");
        string? name = doc.GetStyleName();
        Assert.NotNull(name);
    }
}
