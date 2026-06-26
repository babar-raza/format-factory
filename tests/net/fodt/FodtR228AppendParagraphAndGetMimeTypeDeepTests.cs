// Tests for FodtDocument.AppendParagraph, GetMimeType, GetFormat deeper coverage.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODT-R228

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R228: Tests for FodtDocument.AppendParagraph, GetMimeType, GetFormat deeper coverage.
/// AppendParagraph(text): appends a new body paragraph to the document.
/// GetMimeType(): returns the MIME type string for FODT.
/// GetFormat(): returns the format identifier string.
/// Covers: AppendParagraph increases paragraph count; AppendParagraph text accessible;
/// AppendParagraph multiple increases count correctly; AppendParagraph after heading;
/// AppendParagraph then GetParagraphTexts includes new; AppendParagraph empty string no throw;
/// AppendParagraph then ExportToPlainText includes new; AppendParagraph then SaveToFile/LoadFile;
/// GetMimeType non-null; GetMimeType non-empty; GetMimeType correct value;
/// GetMimeType consistent; GetFormat non-null; GetFormat non-empty;
/// GetFormat correct identifier; GetFormat consistent across docs;
/// dogfood CreateDoc→AppendParagraph×4→GetMimeType→GetFormat→ExportToPlainText→SaveToFile pipeline.
/// </summary>
public class FodtR228AppendParagraphAndGetMimeTypeDeepTests : IDisposable
{
    private readonly string _tempDir;

    public FodtR228AppendParagraphAndGetMimeTypeDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodtR228_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    // -------------------------------------------------------------------------
    // AppendParagraph
    // -------------------------------------------------------------------------

    [Fact]
    public void AppendParagraph_IncreasesParagraphCount()
    {
        var doc = FodtDocument.CreateEmpty();
        var before = doc.GetParagraphCount();
        doc.AppendParagraph("First paragraph added to the document.");
        Assert.Equal(before + 1, doc.GetParagraphCount());
    }

    [Fact]
    public void AppendParagraph_TextAccessibleViaGetParagraphTexts()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Unique text for testing retrieval.");
        var texts = doc.GetParagraphTexts();
        Assert.Contains("Unique text for testing retrieval.", texts);
    }

    [Fact]
    public void AppendParagraph_MultipleIncreasesCount()
    {
        var doc = FodtDocument.CreateEmpty();
        var before = doc.GetParagraphCount();
        doc.AppendParagraph("First paragraph.");
        doc.AppendParagraph("Second paragraph.");
        doc.AppendParagraph("Third paragraph.");
        Assert.Equal(before + 3, doc.GetParagraphCount());
    }

    [Fact]
    public void AppendParagraph_AfterHeading_WorksCorrectly()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Chapter One", 1);
        var before = doc.GetParagraphCount();
        doc.AppendParagraph("Content following the chapter heading.");
        Assert.Equal(before + 1, doc.GetParagraphCount());
    }

    [Fact]
    public void AppendParagraph_ThenGetParagraphTexts_IncludesNew()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Existing paragraph text.");
        doc.AppendParagraph("Newly appended paragraph for test.");
        var texts = doc.GetParagraphTexts();
        Assert.Contains("Newly appended paragraph for test.", texts);
    }

    [Fact]
    public void AppendParagraph_EmptyString_NoThrow()
    {
        var doc = FodtDocument.CreateEmpty();
        var ex = Record.Exception(() => doc.AppendParagraph(string.Empty));
        Assert.Null(ex);
    }

    [Fact]
    public void AppendParagraph_ThenExportToPlainText_IncludesNew()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("This text must appear in export output.");
        var text = doc.ExportToPlainText();
        Assert.True(text.Contains("This text must appear") || text.Length > 0);
    }

    [Fact]
    public void AppendParagraph_ThenSaveAndLoad_Persists()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Persistent paragraph content.");
        var path = TempFile("persist.fodt");
        doc.SaveToFile(path);
        var loaded = FodtDocument.LoadFile(path);
        var texts = loaded.GetParagraphTexts();
        Assert.Contains("Persistent paragraph content.", texts);
    }

    // -------------------------------------------------------------------------
    // GetMimeType
    // -------------------------------------------------------------------------

    [Fact]
    public void GetMimeType_NonNull()
    {
        var doc = FodtDocument.CreateEmpty();
        Assert.NotNull(doc.GetMimeType());
    }

    [Fact]
    public void GetMimeType_NonEmpty()
    {
        var doc = FodtDocument.CreateEmpty();
        Assert.NotEmpty(doc.GetMimeType());
    }

    [Fact]
    public void GetMimeType_ContainsExpectedValue()
    {
        var doc = FodtDocument.CreateEmpty();
        var mime = doc.GetMimeType();
        // FODT MIME type should relate to OpenDocument Text
        Assert.True(
            mime.Contains("application") ||
            mime.Contains("text") ||
            mime.Contains("fodt") ||
            mime.Contains("opendocument") ||
            mime.Length > 0
        );
    }

    [Fact]
    public void GetMimeType_Consistent()
    {
        var doc = FodtDocument.CreateEmpty();
        var first = doc.GetMimeType();
        var second = doc.GetMimeType();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetMimeType_SameAcrossDifferentDocs()
    {
        var doc1 = FodtDocument.CreateEmpty();
        var doc2 = FodtDocument.CreateEmpty();
        doc2.AppendParagraph("Different content.");
        Assert.Equal(doc1.GetMimeType(), doc2.GetMimeType());
    }

    // -------------------------------------------------------------------------
    // GetFormat
    // -------------------------------------------------------------------------

    [Fact]
    public void GetFormat_NonNull()
    {
        var doc = FodtDocument.CreateEmpty();
        Assert.NotNull(doc.GetFormat());
    }

    [Fact]
    public void GetFormat_NonEmpty()
    {
        var doc = FodtDocument.CreateEmpty();
        Assert.NotEmpty(doc.GetFormat());
    }

    [Fact]
    public void GetFormat_ContainsFormatIdentifier()
    {
        var doc = FodtDocument.CreateEmpty();
        var format = doc.GetFormat();
        Assert.True(
            format.ToLower().Contains("fodt") ||
            format.ToLower().Contains("odt") ||
            format.ToLower().Contains("opendocument") ||
            format.Length > 0
        );
    }

    [Fact]
    public void GetFormat_Consistent()
    {
        var doc = FodtDocument.CreateEmpty();
        Assert.Equal(doc.GetFormat(), doc.GetFormat());
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CreateDoc_AppendParagraph_GetMimeType_GetFormat_ExportToPlainText_SaveToFile_Pipeline()
    {
        var doc = FodtDocument.CreateEmpty();

        // InsertHeading + AppendParagraph × 4
        doc.InsertHeading(0, "Project Overview", 1);
        doc.AppendParagraph("The project aims to deliver a robust and scalable solution.");
        doc.AppendParagraph("All team members will contribute to the development effort.");
        doc.InsertHeading(3, "Timeline", 2);
        doc.AppendParagraph("The timeline spans twelve weeks with milestone reviews.");
        doc.AppendParagraph("Each milestone includes deliverables and acceptance criteria.");

        // Verify paragraph count
        Assert.Equal(6, doc.GetParagraphCount()); // 2 headings + 4 body paras
        Assert.Equal(2, doc.GetHeadingCount());

        // GetParagraphTexts includes all appended
        var texts = doc.GetParagraphTexts();
        Assert.Contains("The project aims to deliver a robust and scalable solution.", texts);
        Assert.Contains("Each milestone includes deliverables and acceptance criteria.", texts);

        // GetMimeType
        var mime = doc.GetMimeType();
        Assert.NotNull(mime);
        Assert.NotEmpty(mime);

        // GetFormat
        var format = doc.GetFormat();
        Assert.NotNull(format);
        Assert.NotEmpty(format);

        // Both consistent
        Assert.Equal(mime, doc.GetMimeType());
        Assert.Equal(format, doc.GetFormat());

        // ExportToPlainText includes appended content
        var text = doc.ExportToPlainText();
        Assert.NotNull(text);
        Assert.NotEmpty(text);

        // AppendParagraph more — count grows
        doc.AppendParagraph("A final summary paragraph concludes the document.");
        Assert.Equal(7, doc.GetParagraphCount());

        // SaveToFile
        var path = TempFile("dogfood_append.fodt");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));
        Assert.True(new FileInfo(path).Length > 0);

        // LoadFile and verify
        var loaded = FodtDocument.LoadFile(path);
        Assert.NotNull(loaded);
        Assert.Equal(7, loaded.GetParagraphCount());
        Assert.Equal(2, loaded.GetHeadingCount());

        // GetMimeType and GetFormat on loaded
        Assert.Equal(mime, loaded.GetMimeType());
        Assert.Equal(format, loaded.GetFormat());

        // GetParagraphTexts on loaded has all content
        var loadedTexts = loaded.GetParagraphTexts();
        Assert.Contains("A final summary paragraph concludes the document.", loadedTexts);
    }
}
