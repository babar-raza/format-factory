// Tests for FodtDocument.AppendText dedicated coverage.
// Sprint: ff-sprint-s300-dotnet-deepening-20260630
// Ledger: PC-FODT-R315

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R315: Dedicated tests for FodtDocument.AppendText(text).
/// Valid call no exception.
/// ParagraphCount increases or unchanged after AppendText.
/// TableCount unchanged after AppendText.
/// SectionCount unchanged after AppendText.
/// Called twice no exception.
/// Empty string no exception.
/// Multiple appends no exception.
/// Dogfood: append text and verify no exception.
/// Dogfood: append multiple texts no exception.
/// </summary>
public class FodtR315AppendTextDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void AppendText_ValidCall_NoException()
    {
        var doc = FodtDocument.CreateNew();
        var ex = Record.Exception(() => doc.AppendText("Hello World"));
        Assert.Null(ex);
    }

    [Fact]
    public void AppendText_ParagraphCountIncreasesOrUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        int before = doc.ParagraphCount;
        doc.AppendText("New text");
        int after = doc.ParagraphCount;
        Assert.True(after >= before);
    }

    [Fact]
    public void AppendText_TableCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        int tableBefore = doc.TableCount;
        doc.AppendText("Some text");
        Assert.Equal(tableBefore, doc.TableCount);
    }

    [Fact]
    public void AppendText_SectionCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        int secBefore = doc.GetSectionCount();
        doc.AppendText("Some text");
        Assert.Equal(secBefore, doc.GetSectionCount());
    }

    [Fact]
    public void AppendText_CalledTwice_NoException()
    {
        var doc = FodtDocument.CreateNew();
        doc.AppendText("First");
        var ex = Record.Exception(() => doc.AppendText("Second"));
        Assert.Null(ex);
    }

    [Fact]
    public void AppendText_EmptyString_NoException()
    {
        var doc = FodtDocument.CreateNew();
        var ex = Record.Exception(() => doc.AppendText(string.Empty));
        Assert.Null(ex);
    }

    [Fact]
    public void AppendText_MultipleAppends_NoException()
    {
        var doc = FodtDocument.CreateNew();
        var ex = Record.Exception(() =>
        {
            doc.AppendText("Line 1");
            doc.AppendText("Line 2");
            doc.AppendText("Line 3");
        });
        Assert.Null(ex);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_AppendText_NoException()
    {
        var doc = FodtDocument.CreateNew();
        var ex = Record.Exception(() => doc.AppendText("The quick brown fox jumps over the lazy dog."));
        Assert.Null(ex);
    }

    [Fact]
    public void DogfoodPipeline_AppendMultipleTexts_NoException()
    {
        var doc = FodtDocument.CreateNew();
        var ex = Record.Exception(() =>
        {
            doc.AppendText("Introduction paragraph.");
            doc.AppendText("Body content goes here.");
            doc.AppendText("Conclusion statement.");
        });
        Assert.Null(ex);
    }
}
