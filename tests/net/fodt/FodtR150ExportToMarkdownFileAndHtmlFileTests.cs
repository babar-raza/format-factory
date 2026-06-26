// Tests for FodtDocument.ExportToMarkdownFile and ExportToHtmlFile.
// Sprint: ff-sprint-s135-dotnet-deepening-20260627
// Ledger: PC-FODT-R150

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R150: Tests for FodtDocument.ExportToMarkdownFile and ExportToHtmlFile.
/// Both methods write the in-memory export (ExportToMarkdown/ExportToHtml) to disk.
/// They throw ArgumentException for null/empty/whitespace paths and create/overwrite files.
/// Covers: ExportToMarkdownFile null path throws; empty path throws; whitespace path throws;
/// file created on disk; content non-empty; content equals ExportToMarkdown();
/// overwrites existing file; ExportToHtmlFile null path throws; file created;
/// content equals ExportToHtml(); dogfood AppendParagraph×2→both file exports verified.
/// </summary>
public class FodtR150ExportToMarkdownFileAndHtmlFileTests
{
    // -------------------------------------------------------------------------
    // ExportToMarkdownFile null guards
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportToMarkdownFile_NullPath_ThrowsArgumentException()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Hello");
        Assert.Throws<ArgumentException>(() => doc.ExportToMarkdownFile(null!));
    }

    [Fact]
    public void ExportToMarkdownFile_EmptyPath_ThrowsArgumentException()
    {
        var doc = FodtDocument.CreateEmpty();
        Assert.Throws<ArgumentException>(() => doc.ExportToMarkdownFile(string.Empty));
    }

    [Fact]
    public void ExportToMarkdownFile_WhitespacePath_ThrowsArgumentException()
    {
        var doc = FodtDocument.CreateEmpty();
        Assert.Throws<ArgumentException>(() => doc.ExportToMarkdownFile("   "));
    }

    // -------------------------------------------------------------------------
    // ExportToMarkdownFile file creation and content
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportToMarkdownFile_ValidPath_CreatesFile()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Sprint S135 Markdown test");
        var path = Path.Combine(Path.GetTempPath(), $"fodt_r150_md_{Guid.NewGuid():N}.md");
        try
        {
            doc.ExportToMarkdownFile(path);
            Assert.True(File.Exists(path));
        }
        finally { if (File.Exists(path)) File.Delete(path); }
    }

    [Fact]
    public void ExportToMarkdownFile_ContentMatchesExportToMarkdown()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Alpha");
        doc.AppendParagraph("Beta");
        var path = Path.Combine(Path.GetTempPath(), $"fodt_r150_md_{Guid.NewGuid():N}.md");
        try
        {
            doc.ExportToMarkdownFile(path);
            var fileContent = File.ReadAllText(path);
            var inMemory = doc.ExportToMarkdown();
            Assert.Equal(inMemory, fileContent);
        }
        finally { if (File.Exists(path)) File.Delete(path); }
    }

    [Fact]
    public void ExportToMarkdownFile_OverwritesExistingFile()
    {
        var doc1 = FodtDocument.CreateEmpty();
        doc1.AppendParagraph("First version");
        var doc2 = FodtDocument.CreateEmpty();
        doc2.AppendParagraph("Second version");
        var path = Path.Combine(Path.GetTempPath(), $"fodt_r150_md_{Guid.NewGuid():N}.md");
        try
        {
            doc1.ExportToMarkdownFile(path);
            doc2.ExportToMarkdownFile(path);
            var content = File.ReadAllText(path);
            Assert.Contains("Second version", content);
            Assert.DoesNotContain("First version", content);
        }
        finally { if (File.Exists(path)) File.Delete(path); }
    }

    // -------------------------------------------------------------------------
    // ExportToHtmlFile null guard and content
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportToHtmlFile_NullPath_ThrowsArgumentException()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Hello");
        Assert.Throws<ArgumentException>(() => doc.ExportToHtmlFile(null!));
    }

    [Fact]
    public void ExportToHtmlFile_ValidPath_CreatesFile()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Sprint S135 HTML test");
        var path = Path.Combine(Path.GetTempPath(), $"fodt_r150_html_{Guid.NewGuid():N}.html");
        try
        {
            doc.ExportToHtmlFile(path);
            Assert.True(File.Exists(path));
        }
        finally { if (File.Exists(path)) File.Delete(path); }
    }

    [Fact]
    public void ExportToHtmlFile_ContentMatchesExportToHtml()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Gamma");
        doc.AppendParagraph("Delta");
        var path = Path.Combine(Path.GetTempPath(), $"fodt_r150_html_{Guid.NewGuid():N}.html");
        try
        {
            doc.ExportToHtmlFile(path);
            var fileContent = File.ReadAllText(path);
            var inMemory = doc.ExportToHtml();
            Assert.Equal(inMemory, fileContent);
        }
        finally { if (File.Exists(path)) File.Delete(path); }
    }

    // -------------------------------------------------------------------------
    // Dogfood: AppendParagraph×2 -> ExportToMarkdownFile + ExportToHtmlFile
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_AppendTwoParagraphs_BothFileExports_ContainTexts()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Title of document");
        doc.AppendParagraph("Body content here");

        var mdPath = Path.Combine(Path.GetTempPath(), $"fodt_r150_dog_md_{Guid.NewGuid():N}.md");
        var htmlPath = Path.Combine(Path.GetTempPath(), $"fodt_r150_dog_html_{Guid.NewGuid():N}.html");
        try
        {
            doc.ExportToMarkdownFile(mdPath);
            doc.ExportToHtmlFile(htmlPath);

            var mdContent = File.ReadAllText(mdPath);
            var htmlContent = File.ReadAllText(htmlPath);

            Assert.Contains("Title of document", mdContent);
            Assert.Contains("Body content here", mdContent);
            Assert.Contains("Title of document", htmlContent);
            Assert.Contains("Body content here", htmlContent);
        }
        finally
        {
            if (File.Exists(mdPath)) File.Delete(mdPath);
            if (File.Exists(htmlPath)) File.Delete(htmlPath);
        }
    }
}
