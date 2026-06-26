// Tests for FodtDocument.ExportToHtmlFile dedicated coverage.
// Sprint: ff-sprint-s183-dotnet-deepening-20260628
// Ledger: PC-FODT-R192

using System.IO;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R192: Dedicated tests for FodtDocument.ExportToHtmlFile(string filePath).
/// Exports the document body as HTML and writes it to a file.
/// null/whitespace filePath throws ArgumentException.
/// The file is created (or overwritten) at the given path.
/// File contains HTML content (at minimum an opening &lt;html&gt; or &lt;body&gt; tag).
/// File content matches ExportToHtml() string output.
/// Multiple exports overwrite the previous file.
/// Covers: null path throws; whitespace path throws; valid path creates file;
/// file exists after export; file contains html tag; content matches ExportToHtml;
/// empty doc writes html file; overwrite previous file; dogfood heading and paragraph;
/// dogfood file can be re-read as string.
/// </summary>
public class FodtR192ExportToHtmlFileTests
{
    private static string TempPath() =>
        Path.Combine(Path.GetTempPath(), Path.GetRandomFileName() + ".html");

    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportToHtmlFile_NullPath_ThrowsArgumentException()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Hello");
        Assert.Throws<ArgumentException>(() => doc.ExportToHtmlFile(null!));
    }

    [Fact]
    public void ExportToHtmlFile_WhitespacePath_ThrowsArgumentException()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Hello");
        Assert.Throws<ArgumentException>(() => doc.ExportToHtmlFile("   "));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportToHtmlFile_ValidPath_CreatesFile()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Content");
        var path = TempPath();
        try
        {
            doc.ExportToHtmlFile(path);
            Assert.True(File.Exists(path));
        }
        finally
        {
            if (File.Exists(path)) File.Delete(path);
        }
    }

    [Fact]
    public void ExportToHtmlFile_ContentContainsHtmlTag()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Test paragraph");
        var path = TempPath();
        try
        {
            doc.ExportToHtmlFile(path);
            var content = File.ReadAllText(path);
            Assert.True(content.Contains("<html") || content.Contains("<body") || content.Contains("<p"),
                "Expected HTML content in file");
        }
        finally
        {
            if (File.Exists(path)) File.Delete(path);
        }
    }

    [Fact]
    public void ExportToHtmlFile_ContentMatchesExportToHtml()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Match me");
        var path = TempPath();
        try
        {
            doc.ExportToHtmlFile(path);
            var fileContent = File.ReadAllText(path);
            var methodContent = doc.ExportToHtml();
            Assert.Equal(methodContent, fileContent);
        }
        finally
        {
            if (File.Exists(path)) File.Delete(path);
        }
    }

    [Fact]
    public void ExportToHtmlFile_EmptyDocument_CreatesFile()
    {
        var doc = FodtDocument.CreateEmpty();
        var path = TempPath();
        try
        {
            doc.ExportToHtmlFile(path);
            Assert.True(File.Exists(path));
        }
        finally
        {
            if (File.Exists(path)) File.Delete(path);
        }
    }

    [Fact]
    public void ExportToHtmlFile_OverwritesPreviousFile()
    {
        var doc1 = FodtDocument.CreateEmpty();
        doc1.AppendParagraph("First content");
        var doc2 = FodtDocument.CreateEmpty();
        doc2.AppendParagraph("Second content");
        var path = TempPath();
        try
        {
            doc1.ExportToHtmlFile(path);
            doc2.ExportToHtmlFile(path);
            var content = File.ReadAllText(path);
            Assert.Contains("Second content", content);
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
    public void DogfoodPipeline_HeadingAndParagraph_BothInFile()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("Chapter One", 1);
        doc.AppendParagraph("Body text here.");
        var path = TempPath();
        try
        {
            doc.ExportToHtmlFile(path);
            var content = File.ReadAllText(path);
            Assert.Contains("Chapter One", content);
            Assert.Contains("Body text here", content);
        }
        finally
        {
            if (File.Exists(path)) File.Delete(path);
        }
    }

    [Fact]
    public void DogfoodPipeline_FileCanBeReReadAsString()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Readable paragraph");
        var path = TempPath();
        try
        {
            doc.ExportToHtmlFile(path);
            var text = File.ReadAllText(path);
            Assert.False(string.IsNullOrEmpty(text));
        }
        finally
        {
            if (File.Exists(path)) File.Delete(path);
        }
    }
}
