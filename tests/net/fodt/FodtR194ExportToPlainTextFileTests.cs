// Tests for FodtDocument.ExportToPlainTextFile dedicated coverage.
// Sprint: ff-sprint-s185-dotnet-deepening-20260628
// Ledger: PC-FODT-R194

using System.IO;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R194: Dedicated tests for FodtDocument.ExportToPlainTextFile(string filePath).
/// Exports the document body as plain text and writes it to a file.
/// null/whitespace filePath throws ArgumentException.
/// The file is created (or overwritten) at the given path.
/// File content matches GetPlainText() string output.
/// Empty document produces empty or whitespace-only file.
/// Covers: null path throws; whitespace path throws; valid path creates file;
/// file exists after export; content matches GetPlainText; empty doc creates file;
/// overwrite previous file; file not empty for non-empty doc;
/// dogfood paragraph text in file; dogfood heading text in file.
/// </summary>
public class FodtR194ExportToPlainTextFileTests
{
    private static string TempPath() =>
        Path.Combine(Path.GetTempPath(), Path.GetRandomFileName() + ".txt");

    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportToPlainTextFile_NullPath_ThrowsArgumentException()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Hello");
        Assert.Throws<ArgumentException>(() => doc.ExportToPlainTextFile(null!));
    }

    [Fact]
    public void ExportToPlainTextFile_WhitespacePath_ThrowsArgumentException()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Hello");
        Assert.Throws<ArgumentException>(() => doc.ExportToPlainTextFile("   "));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportToPlainTextFile_ValidPath_CreatesFile()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Plain text content");
        var path = TempPath();
        try
        {
            doc.ExportToPlainTextFile(path);
            Assert.True(File.Exists(path));
        }
        finally
        {
            if (File.Exists(path)) File.Delete(path);
        }
    }

    [Fact]
    public void ExportToPlainTextFile_ContentMatchesGetPlainText()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("Title", 1);
        doc.AppendParagraph("Body paragraph");
        var path = TempPath();
        try
        {
            doc.ExportToPlainTextFile(path);
            var fileContent = File.ReadAllText(path);
            var methodContent = doc.GetPlainText();
            Assert.Equal(methodContent, fileContent);
        }
        finally
        {
            if (File.Exists(path)) File.Delete(path);
        }
    }

    [Fact]
    public void ExportToPlainTextFile_EmptyDocument_CreatesFile()
    {
        var doc = FodtDocument.CreateEmpty();
        var path = TempPath();
        try
        {
            doc.ExportToPlainTextFile(path);
            Assert.True(File.Exists(path));
        }
        finally
        {
            if (File.Exists(path)) File.Delete(path);
        }
    }

    [Fact]
    public void ExportToPlainTextFile_NonEmptyDoc_FileNotEmpty()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Some text");
        var path = TempPath();
        try
        {
            doc.ExportToPlainTextFile(path);
            var content = File.ReadAllText(path);
            Assert.False(string.IsNullOrEmpty(content));
        }
        finally
        {
            if (File.Exists(path)) File.Delete(path);
        }
    }

    [Fact]
    public void ExportToPlainTextFile_OverwritesPreviousFile()
    {
        var doc1 = FodtDocument.CreateEmpty();
        doc1.AppendParagraph("First version");
        var doc2 = FodtDocument.CreateEmpty();
        doc2.AppendParagraph("Second version");
        var path = TempPath();
        try
        {
            doc1.ExportToPlainTextFile(path);
            doc2.ExportToPlainTextFile(path);
            var content = File.ReadAllText(path);
            Assert.Contains("Second version", content);
        }
        finally
        {
            if (File.Exists(path)) File.Delete(path);
        }
    }

    // -------------------------------------------------------------------------
    // Dogfood pipelines
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_ParagraphText_PresentInFile()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Unique paragraph content 42");
        var path = TempPath();
        try
        {
            doc.ExportToPlainTextFile(path);
            var content = File.ReadAllText(path);
            Assert.Contains("Unique paragraph content 42", content);
        }
        finally
        {
            if (File.Exists(path)) File.Delete(path);
        }
    }

    [Fact]
    public void DogfoodPipeline_HeadingText_PresentInFile()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("Section Header Text", 1);
        var path = TempPath();
        try
        {
            doc.ExportToPlainTextFile(path);
            var content = File.ReadAllText(path);
            Assert.Contains("Section Header Text", content);
        }
        finally
        {
            if (File.Exists(path)) File.Delete(path);
        }
    }
}
