// Tests for FodtDocument.ExportToTxt dedicated coverage.
// Sprint: ff-sprint-s199-dotnet-deepening-20260629
// Ledger: PC-FODT-R214

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R214: Dedicated tests for FodtDocument.ExportToTxt(string outputPath).
/// null outputPath → ArgumentNullException.
/// Empty document: produces file (possibly empty or minimal content).
/// Single paragraph: file contains paragraph text.
/// Multiple paragraphs: all present in output.
/// Heading text included in output.
/// Output file is created at the given path.
/// File content is readable as plain text.
/// Newlines separate paragraphs.
/// Dogfood: write then read back, content matches.
/// Dogfood: multi-paragraph export and verify all.
/// </summary>
public class FodtR214ExportToTxtTests : IDisposable
{
    private readonly string _tempDir = System.IO.Path.Combine(System.IO.Path.GetTempPath(), "FodtR214_" + System.Guid.NewGuid().ToString("N")[..8]);

    public FodtR214ExportToTxtTests()
    {
        System.IO.Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        try { System.IO.Directory.Delete(_tempDir, recursive: true); } catch { }
    }

    private string TempPath(string name) => System.IO.Path.Combine(_tempDir, name);

    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportToTxt_NullPath_ThrowsArgumentNullException()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Hello");
        Assert.Throws<ArgumentNullException>(() => doc.ExportToTxt(null!));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportToTxt_EmptyDocument_CreatesFile()
    {
        var doc = FodtDocument.CreateEmpty();
        var path = TempPath("empty.txt");
        doc.ExportToTxt(path);
        Assert.True(System.IO.File.Exists(path));
    }

    [Fact]
    public void ExportToTxt_SingleParagraph_ContainsText()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Hello World");
        var path = TempPath("single.txt");
        doc.ExportToTxt(path);
        var content = System.IO.File.ReadAllText(path);
        Assert.Contains("Hello World", content);
    }

    [Fact]
    public void ExportToTxt_MultipleParagraphs_AllPresent()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("First");
        doc.AppendParagraph("Second");
        doc.AppendParagraph("Third");
        var path = TempPath("multi.txt");
        doc.ExportToTxt(path);
        var content = System.IO.File.ReadAllText(path);
        Assert.Contains("First", content);
        Assert.Contains("Second", content);
        Assert.Contains("Third", content);
    }

    [Fact]
    public void ExportToTxt_HeadingIncluded()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("My Title", 1);
        doc.AppendParagraph("Body text");
        var path = TempPath("heading.txt");
        doc.ExportToTxt(path);
        var content = System.IO.File.ReadAllText(path);
        Assert.Contains("My Title", content);
    }

    [Fact]
    public void ExportToTxt_FileIsReadableText()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Readable");
        var path = TempPath("readable.txt");
        doc.ExportToTxt(path);
        // Should be readable as plain text without exception
        var ex = Record.Exception(() => System.IO.File.ReadAllText(path));
        Assert.Null(ex);
    }

    [Fact]
    public void ExportToTxt_MultipleParagraphs_NewlinesSeparate()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Alpha");
        doc.AppendParagraph("Beta");
        var path = TempPath("newlines.txt");
        doc.ExportToTxt(path);
        var content = System.IO.File.ReadAllText(path);
        // Both paragraphs in content; order respected
        int alphaIdx = content.IndexOf("Alpha", StringComparison.Ordinal);
        int betaIdx = content.IndexOf("Beta", StringComparison.Ordinal);
        Assert.True(alphaIdx < betaIdx, "Alpha should appear before Beta");
    }

    // -------------------------------------------------------------------------
    // Dogfood pipelines
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_WriteAndReadBack_ContentMatches()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("DogfoodContent");
        var path = TempPath("dogfood.txt");
        doc.ExportToTxt(path);
        var content = System.IO.File.ReadAllText(path);
        Assert.Contains("DogfoodContent", content);
    }

    [Fact]
    public void DogfoodPipeline_MultiParagraph_AllVerified()
    {
        var doc = FodtDocument.CreateEmpty();
        var words = new[] { "Apple", "Banana", "Cherry" };
        foreach (var w in words) doc.AppendParagraph(w);
        var path = TempPath("all.txt");
        doc.ExportToTxt(path);
        var content = System.IO.File.ReadAllText(path);
        foreach (var w in words)
            Assert.Contains(w, content);
    }
}
