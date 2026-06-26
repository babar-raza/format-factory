// Tests for FodtDocument.ExportToMarkdownFile dedicated coverage.
// Sprint: ff-sprint-s184-dotnet-deepening-20260628
// Ledger: PC-FODT-R193

using System.IO;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R193: Dedicated tests for FodtDocument.ExportToMarkdownFile(string filePath).
/// Exports the document body as Markdown and writes it to a file.
/// null/whitespace filePath throws ArgumentException.
/// The file is created (or overwritten) at the given path.
/// File content matches ExportToMarkdown() string output.
/// Heading elements appear with # prefix in Markdown output.
/// Covers: null path throws; whitespace path throws; valid path creates file;
/// file exists after export; content matches ExportToMarkdown; heading uses # prefix;
/// empty doc writes file; overwrite previous file; multiple headings in markdown;
/// dogfood paragraph and heading pipeline.
/// </summary>
public class FodtR193ExportToMarkdownFileTests
{
    private static string TempPath() =>
        Path.Combine(Path.GetTempPath(), Path.GetRandomFileName() + ".md");

    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportToMarkdownFile_NullPath_ThrowsArgumentException()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Hello");
        Assert.Throws<ArgumentException>(() => doc.ExportToMarkdownFile(null!));
    }

    [Fact]
    public void ExportToMarkdownFile_WhitespacePath_ThrowsArgumentException()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Hello");
        Assert.Throws<ArgumentException>(() => doc.ExportToMarkdownFile("   "));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportToMarkdownFile_ValidPath_CreatesFile()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Markdown content");
        var path = TempPath();
        try
        {
            doc.ExportToMarkdownFile(path);
            Assert.True(File.Exists(path));
        }
        finally
        {
            if (File.Exists(path)) File.Delete(path);
        }
    }

    [Fact]
    public void ExportToMarkdownFile_ContentMatchesExportToMarkdown()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("Section", 1);
        doc.AppendParagraph("Body text");
        var path = TempPath();
        try
        {
            doc.ExportToMarkdownFile(path);
            var fileContent = File.ReadAllText(path);
            var methodContent = doc.ExportToMarkdown();
            Assert.Equal(methodContent, fileContent);
        }
        finally
        {
            if (File.Exists(path)) File.Delete(path);
        }
    }

    [Fact]
    public void ExportToMarkdownFile_HeadingUsesHashPrefix()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("My Title", 1);
        var path = TempPath();
        try
        {
            doc.ExportToMarkdownFile(path);
            var content = File.ReadAllText(path);
            Assert.Contains("#", content);
            Assert.Contains("My Title", content);
        }
        finally
        {
            if (File.Exists(path)) File.Delete(path);
        }
    }

    [Fact]
    public void ExportToMarkdownFile_EmptyDocument_CreatesFile()
    {
        var doc = FodtDocument.CreateEmpty();
        var path = TempPath();
        try
        {
            doc.ExportToMarkdownFile(path);
            Assert.True(File.Exists(path));
        }
        finally
        {
            if (File.Exists(path)) File.Delete(path);
        }
    }

    [Fact]
    public void ExportToMarkdownFile_OverwritesPreviousFile()
    {
        var doc1 = FodtDocument.CreateEmpty();
        doc1.AppendParagraph("First");
        var doc2 = FodtDocument.CreateEmpty();
        doc2.AppendParagraph("Second");
        var path = TempPath();
        try
        {
            doc1.ExportToMarkdownFile(path);
            doc2.ExportToMarkdownFile(path);
            var content = File.ReadAllText(path);
            Assert.Contains("Second", content);
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
        doc.AppendHeading("Introduction", 1);
        doc.AppendParagraph("This is the intro paragraph.");
        var path = TempPath();
        try
        {
            doc.ExportToMarkdownFile(path);
            var content = File.ReadAllText(path);
            Assert.Contains("Introduction", content);
            Assert.Contains("intro paragraph", content);
        }
        finally
        {
            if (File.Exists(path)) File.Delete(path);
        }
    }

    [Fact]
    public void DogfoodPipeline_MultipleHeadings_AllPresentInFile()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("Chapter 1", 1);
        doc.AppendHeading("Section 1.1", 2);
        doc.AppendParagraph("Content here.");
        var path = TempPath();
        try
        {
            doc.ExportToMarkdownFile(path);
            var content = File.ReadAllText(path);
            Assert.Contains("Chapter 1", content);
            Assert.Contains("Section 1.1", content);
        }
        finally
        {
            if (File.Exists(path)) File.Delete(path);
        }
    }
}
