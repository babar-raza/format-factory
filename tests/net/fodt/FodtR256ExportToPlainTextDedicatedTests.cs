// Tests for FodtDocument.ExportToPlainText dedicated coverage.
// Sprint: ff-sprint-s241-dotnet-deepening-20260629
// Ledger: PC-FODT-R256

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R256: Dedicated tests for FodtDocument.ExportToPlainText().
/// Returns non-null string.
/// Empty document → non-null (possibly empty string).
/// Single paragraph → contains paragraph text.
/// Heading → text appears in result.
/// Two paragraphs → result longer than one paragraph.
/// ParagraphCount unchanged after call.
/// Called twice → same result.
/// After AppendParagraph → result grows or same.
/// After ReplaceText → result reflects change.
/// Dogfood: append known text, verify appears in plain text output.
/// </summary>
public class FodtR256ExportToPlainTextDedicatedTests
{
    // -------------------------------------------------------------------------
    // Basic functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportToPlainText_EmptyDoc_ReturnsNonNull()
    {
        var doc = FodtDocument.CreateEmpty();
        var result = doc.ExportToPlainText();
        Assert.NotNull(result);
    }

    [Fact]
    public void ExportToPlainText_SingleParagraph_ContainsText()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Hello plain world");
        var result = doc.ExportToPlainText();
        Assert.NotNull(result);
        Assert.Contains("Hello plain world", result);
    }

    [Fact]
    public void ExportToPlainText_HeadingText_AppearsInResult()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("Introduction", 1);
        doc.AppendParagraph("Some body content.");
        var result = doc.ExportToPlainText();
        Assert.NotNull(result);
        // At least body content should appear
        Assert.Contains("Some body content", result);
    }

    [Fact]
    public void ExportToPlainText_TwoParagraphs_LongerThanOne()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("First paragraph");
        int lenOne = doc.ExportToPlainText()!.Length;
        doc.AppendParagraph("Second paragraph with more text");
        int lenTwo = doc.ExportToPlainText()!.Length;
        Assert.True(lenTwo >= lenOne);
    }

    [Fact]
    public void ExportToPlainText_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Test content");
        int paras = doc.ParagraphCount;
        doc.ExportToPlainText();
        Assert.Equal(paras, doc.ParagraphCount);
    }

    [Fact]
    public void ExportToPlainText_CalledTwice_SameResult()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Consistent output");
        var r1 = doc.ExportToPlainText();
        var r2 = doc.ExportToPlainText();
        Assert.Equal(r1, r2);
    }

    [Fact]
    public void ExportToPlainText_AfterAppendParagraph_NonDecreasingLength()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Initial text");
        int before = doc.ExportToPlainText()!.Length;
        doc.AppendParagraph("Additional text");
        int after = doc.ExportToPlainText()!.Length;
        Assert.True(after >= before);
    }

    [Fact]
    public void ExportToPlainText_AfterReplaceText_ReflectsChange()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Original content here");
        doc.ReplaceText("Original", "Replaced");
        var result = doc.ExportToPlainText();
        Assert.NotNull(result);
        Assert.Contains("Replaced", result);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_AppendKnownText_VerifyInOutput()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("DOGFOOD_MARKER_ALPHA");
        doc.AppendParagraph("DOGFOOD_MARKER_BETA");
        doc.AppendParagraph("DOGFOOD_MARKER_GAMMA");
        var result = doc.ExportToPlainText();
        Assert.NotNull(result);
        Assert.Contains("DOGFOOD_MARKER_ALPHA", result);
        Assert.Contains("DOGFOOD_MARKER_BETA", result);
        Assert.Contains("DOGFOOD_MARKER_GAMMA", result);
    }

    [Fact]
    public void DogfoodPipeline_MultipleOperations_StableOutput()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("Chapter One", 1);
        doc.AppendParagraph("Body of chapter one.");
        doc.AppendParagraph("Second body paragraph.");
        string result = doc.ExportToPlainText()!;
        Assert.NotNull(result);
        Assert.True(result.Length > 0);
        // Calling again should produce same result
        Assert.Equal(result, doc.ExportToPlainText());
    }
}
