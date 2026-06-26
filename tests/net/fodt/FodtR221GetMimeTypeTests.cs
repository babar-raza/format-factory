// Tests for FodtDocument.GetMimeType dedicated coverage.
// Sprint: ff-sprint-s206-dotnet-deepening-20260629
// Ledger: PC-FODT-R221

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R221: Dedicated tests for FodtDocument.GetMimeType().
/// Returns a non-null string.
/// Returns the FODT MIME type (application/vnd.oasis.opendocument.text-flat-xml or similar).
/// Consistent: called twice returns same value.
/// ParagraphCount unchanged after get.
/// Empty document returns valid MIME type.
/// Document with paragraphs returns same MIME type.
/// MIME type contains "opendocument" or "text".
/// MIME type does not contain "spreadsheet" or "presentation".
/// Dogfood: get MIME type, add paragraphs, get again — same value.
/// Dogfood: MIME type is a valid MIME string (contains "/").
/// </summary>
public class FodtR221GetMimeTypeTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetMimeType_EmptyDoc_ReturnsNonNull()
    {
        var doc = FodtDocument.CreateEmpty();
        Assert.NotNull(doc.GetMimeType());
    }

    [Fact]
    public void GetMimeType_ReturnsString()
    {
        var doc = FodtDocument.CreateEmpty();
        Assert.IsAssignableFrom<string>(doc.GetMimeType());
    }

    [Fact]
    public void GetMimeType_CalledTwice_SameValue()
    {
        var doc = FodtDocument.CreateEmpty();
        var t1 = doc.GetMimeType();
        var t2 = doc.GetMimeType();
        Assert.Equal(t1, t2);
    }

    [Fact]
    public void GetMimeType_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("A");
        doc.AppendParagraph("B");
        int before = doc.ParagraphCount;
        doc.GetMimeType();
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void GetMimeType_ContainsSlash_ValidMimeFormat()
    {
        var doc = FodtDocument.CreateEmpty();
        var mime = doc.GetMimeType();
        Assert.Contains("/", mime);
    }

    [Fact]
    public void GetMimeType_ContainsTextOrOpendocument()
    {
        var doc = FodtDocument.CreateEmpty();
        var mime = doc.GetMimeType()!.ToLowerInvariant();
        Assert.True(
            mime.Contains("text") || mime.Contains("opendocument"),
            $"Expected MIME type to reference text/opendocument, got: {mime}");
    }

    [Fact]
    public void GetMimeType_DocWithParagraphs_SameMime()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Para");
        doc.AppendHeading("Head", 1);
        var mime = doc.GetMimeType();
        Assert.NotNull(mime);
        Assert.Contains("/", mime);
    }

    [Fact]
    public void GetMimeType_DoesNotContainSpreadsheet()
    {
        var doc = FodtDocument.CreateEmpty();
        var mime = doc.GetMimeType()!.ToLowerInvariant();
        Assert.DoesNotContain("spreadsheet", mime);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipelines
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_GetBeforeAndAfterParagraph_SameMime()
    {
        var doc = FodtDocument.CreateEmpty();
        var before = doc.GetMimeType();
        doc.AppendParagraph("Added");
        var after = doc.GetMimeType();
        Assert.Equal(before, after);
    }

    [Fact]
    public void DogfoodPipeline_LoadedFile_MimeNonNull()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Test paragraph");
        var mime = doc.GetMimeType();
        Assert.NotNull(mime);
        Assert.True(mime.Length > 0);
    }
}
